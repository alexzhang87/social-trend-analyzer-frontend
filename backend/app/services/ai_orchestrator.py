import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
from ..core.config import settings
from ..data.models.database import User
from .llm_service import get_llm_provider

logger = logging.getLogger(__name__)

# Try to import OpenAI client
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Install with: pip install openai")

class AIOrchestrator:
    """
    AI Orchestrator manages different AI models and expert personas
    """
    
    def __init__(self):
        self.llm_provider = get_llm_provider()
        
        # Initialize OpenAI client if available and configured
        self.openai_client = None
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY != "not_set":
            try:
                self.openai_client = AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                    organization=settings.OPENAI_ORGANIZATION if settings.OPENAI_ORGANIZATION else None
                )
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.info("OpenAI client not available - using fallback responses")
        
        self.model_configs = {
            # 智谱AI模型
            "glm-4": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "top_p": 0.9
            },
            "glm-3-turbo": {
                "max_tokens": 3000,
                "temperature": 0.7,
                "top_p": 0.9
            },
            # OpenAI GPT模型
            "gpt-4": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            },
            "gpt-4-turbo": {
                "max_tokens": 4000,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            },
            "gpt-3.5-turbo": {
                "max_tokens": 3000,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        }
        
    async def process_message(
        self,
        message: str,
        expert: Dict[str, Any],
        session: Dict[str, Any],
        context: List[Dict[str, Any]] = None,
        user: User = None
    ) -> Dict[str, Any]:
        """
        Process a message through the AI orchestrator
        """
        try:
            # Select appropriate model
            model = self._select_model(expert, user)
            
            # Build conversation context
            messages = self._build_conversation_context(message, expert, context or [], session)
            
            # Choose API based on model type
            if model.startswith("gpt-") and self.openai_client:
                response_data = await self._get_openai_response(messages, model, expert)
            elif model.startswith("glm-") and self.llm_provider:
                # Use existing 智谱AI implementation
                response_data = await self._get_zhipu_response(messages, model, expert)
            else:
                # Fallback response
                response_data = await self._get_fallback_response(message, expert)
            
            # Add metadata
            response_data["metadata"] = {
                "expert_id": expert["id"],
                "model": response_data.get("model", model),
                "session_id": session.get("session_id"),
                "timestamp": datetime.now().isoformat(),
                "user_tier": user.subscription_tier.value if user else "free"
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error in AI orchestrator: {str(e)}")
            return {
                "response": f"I apologize, but I encountered a technical issue. As {expert['name']}, I'm here to help with {', '.join(expert['expertise']).lower()}. Please try rephrasing your question.",
                "model": "fallback",
                "metadata": {"error": True, "error_message": str(e)}
            }
    
    async def stream_message(
        self,
        message: str,
        expert: Dict[str, Any],
        session: Dict[str, Any],
        context: List[Dict[str, Any]] = None,
        user: User = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a response from the AI
        """
        try:
            # Use fallback streaming response
            async for chunk in self._stream_fallback_response(message, expert):
                yield chunk
                    
        except Exception as e:
            logger.error(f"Error streaming message: {str(e)}")
            # Yield error response
            yield {
                "success": False,
                "response": f"抱歉，处理您的消息时出现了错误。请稍后再试。",
                "expert": expert["name"],
                "model": "fallback",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "session_id": session.get("id")
            }
    
    def _select_model(self, expert: Dict[str, Any], user: User = None) -> str:
        """
        Select the appropriate AI model based on expert and user tier
        """
        if not user:
            return "glm-3-turbo"
            
        # Model selection based on subscription tier
        # OpenAI models for higher tiers (if available), fallback to 智谱AI
        if self.openai_client:
            tier_models = {
                "free": "glm-3-turbo",
                "pro": "gpt-3.5-turbo",
                "plus": "gpt-4-turbo", 
                "enterprise": "gpt-4"
            }
        else:
            # Fallback to 智谱AI models only
            tier_models = {
                "free": "glm-3-turbo",
                "pro": "glm-4",
                "plus": "glm-4",
                "enterprise": "glm-4"
            }
        
        return tier_models.get(user.subscription_tier.value, "glm-3-turbo")
    
    def _build_conversation_context(
        self,
        message: str,
        expert: Dict[str, Any],
        context: List[Dict[str, Any]],
        session: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Build the conversation context for the AI model
        """
        messages = []
        
        # System prompt with expert persona
        system_prompt = self._build_expert_system_prompt(expert)
        messages.append({"role": "system", "content": system_prompt})
        
        # Add context messages (last 5 for efficiency)
        for ctx_msg in context[-5:]:
            if ctx_msg.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": ctx_msg["role"],
                    "content": ctx_msg.get("content", "")
                })
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def _build_expert_system_prompt(self, expert: Dict[str, Any]) -> str:
        """
        Build a comprehensive system prompt for the expert persona
        """
        personality = expert.get("personality", {})
        
        prompt = f"""You are {expert['name']}, a {expert['title']}.

BACKGROUND & EXPERTISE:
{expert['description']}

Your areas of expertise include: {', '.join(expert.get('expertise', []))}

PERSONALITY & COMMUNICATION STYLE:
- Tone: {personality.get('tone', 'professional')}
- Style: {personality.get('style', 'analytical')}
- Key traits: {', '.join(personality.get('traits', []))}

INSTRUCTIONS:
1. Always respond as {expert['name']} with your specific expertise and personality
2. Provide practical, actionable advice based on your background
3. Use examples and case studies when relevant
4. Ask clarifying questions when needed
5. Maintain your professional {personality.get('tone', 'professional')} tone
6. Focus on your areas of expertise: {', '.join(expert.get('expertise', []))}
7. If asked about topics outside your expertise, acknowledge limitations and suggest consulting other experts
8. Keep responses concise but comprehensive
9. Use business terminology appropriate for your field
10. Always aim to provide value and actionable insights

Remember: You are an expert consultant helping with real business challenges. Provide thoughtful, professional guidance."""

        return prompt
    
    async def _get_openai_response(
        self,
        messages: List[Dict[str, str]],
        model: str,
        expert: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get response from OpenAI API
        """
        try:
            config = self.model_configs.get(model, self.model_configs["gpt-3.5-turbo"])
            
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                top_p=config["top_p"],
                frequency_penalty=config["frequency_penalty"],
                presence_penalty=config["presence_penalty"]
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": model,
                "tokens": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _stream_openai_response(
        self,
        messages: List[Dict[str, str]],
        model: str,
        expert: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream response from OpenAI API
        """
        try:
            config = self.model_configs.get(model, self.model_configs["gpt-3.5-turbo"])
            
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                top_p=config["top_p"],
                frequency_penalty=config["frequency_penalty"],
                presence_penalty=config["presence_penalty"],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "type": "content",
                        "content": chunk.choices[0].delta.content,
                        "model": model
                    }
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {str(e)}")
            yield {
                "type": "error",
                "message": "Error connecting to AI service"
            }
    
    async def _get_zhipu_response(
        self,
        messages: List[Dict[str, str]],
        model: str,
        expert: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get response from 智谱AI API
        """
        try:
            if not self.llm_provider:
                raise Exception("智谱AI provider not available")
            
            # Convert messages to 智谱AI format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Call 智谱AI API
            response = await self.llm_provider.generate_response(
                prompt=prompt,
                model=model,
                max_tokens=self.model_configs[model]["max_tokens"],
                temperature=self.model_configs[model]["temperature"]
            )
            
            return {
                "response": response.get("content", ""),
                "model": model,
                "tokens": response.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"智谱AI API error: {str(e)}")
            # Fallback to local response
            return await self._get_fallback_response("", expert)
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages to a single prompt for 智谱AI
        """
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"系统指令: {content}")
            elif role == "user":
                prompt_parts.append(f"用户: {content}")
            elif role == "assistant":
                prompt_parts.append(f"助手: {content}")
        
        return "\n\n".join(prompt_parts)
    
    async def _get_fallback_response(
        self,
        message: str,
        expert: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide a fallback response when AI services are unavailable
        """
        expertise_responses = {
            "Business Strategy": f"As a business strategy expert, I'd recommend analyzing your market position, competitive landscape, and growth opportunities. For your specific question about '{message[:50]}...', consider conducting a SWOT analysis and reviewing your value proposition.",
            
            "Financial Planning": f"From a financial planning perspective, it's important to evaluate cash flow, investment returns, and risk management. Regarding '{message[:50]}...', I'd suggest reviewing your financial statements and creating scenario-based projections.",
            
            "Marketing": f"As a marketing specialist, I focus on customer acquisition, brand positioning, and growth strategies. For your question about '{message[:50]}...', consider analyzing your target audience, competitive positioning, and channel effectiveness.",
            
            "Technology": f"From a technology standpoint, we should consider scalability, security, and innovation opportunities. Regarding '{message[:50]}...', I'd recommend evaluating your tech stack, automation possibilities, and digital transformation strategies."
        }
        
        # Get response based on expert's primary expertise
        primary_expertise = expert.get("expertise", ["General"])[0]
        response = expertise_responses.get(
            primary_expertise,
            f"As {expert['name']}, I specialize in {', '.join(expert.get('expertise', []))}. I'd be happy to help you with '{message[:50]}...'. Could you provide more specific details about your situation?"
        )
        
        # Simulate processing delay
        await asyncio.sleep(1)
        
        return {
            "response": response,
            "model": "fallback",
            "tokens": {"total": len(response.split())}
        }
    
    async def _stream_fallback_response(
        self,
        message: str,
        expert: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a fallback response
        """
        response = await self._get_fallback_response(message, expert)
        
        # Stream the response word by word
        words = response["response"].split()
        for i, word in enumerate(words):
            yield {
                "type": "content",
                "content": word + (" " if i < len(words) - 1 else ""),
                "model": "fallback"
            }
            await asyncio.sleep(0.05)  # Small delay between words