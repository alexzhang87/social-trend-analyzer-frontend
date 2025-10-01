import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ExpertManager:
    """
    Expert Manager handles AI expert personas and their configurations
    """
    
    def __init__(self):
        self.experts = self._initialize_experts()
    
    def _initialize_experts(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize the expert personas with their configurations
        """
        return {
            "sarah_chen": {
                "id": "sarah_chen",
                "name": "Sarah Chen",
                "title": "Business Strategy Expert",
                "description": "Specialized in strategic planning, market analysis, and business transformation with 15+ years of consulting experience at top-tier firms. Expert in competitive analysis, growth strategies, and organizational development.",
                "avatar": "/avatars/sarah.jpg",
                "expertise": ["Business Strategy", "Market Research", "Strategic Planning", "Competitive Analysis", "Growth Strategy"],
                "personality": {
                    "tone": "professional",
                    "style": "analytical",
                    "traits": ["detail-oriented", "strategic", "data-driven", "methodical", "insightful"]
                },
                "system_prompt_template": "business_strategy_expert",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "specializations": [
                    "Market Entry Strategy",
                    "Business Model Innovation",
                    "Digital Transformation",
                    "Merger & Acquisition Strategy",
                    "Competitive Intelligence"
                ],
                "industries": [
                    "Technology",
                    "Healthcare",
                    "Financial Services",
                    "Retail",
                    "Manufacturing"
                ]
            },
            
            "marcus_rodriguez": {
                "id": "marcus_rodriguez",
                "name": "Marcus Rodriguez",
                "title": "Financial Planning Advisor",
                "description": "Expert in financial modeling, investment strategies, and risk management for businesses of all sizes. CFA charterholder with extensive experience in corporate finance and venture capital.",
                "avatar": "/avatars/marcus.jpg",
                "expertise": ["Financial Planning", "Investment Strategy", "Risk Management", "Financial Modeling", "Corporate Finance"],
                "personality": {
                    "tone": "analytical",
                    "style": "methodical",
                    "traits": ["precise", "conservative", "thorough", "quantitative", "risk-aware"]
                },
                "system_prompt_template": "financial_expert",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "specializations": [
                    "Financial Forecasting",
                    "Capital Structure Optimization",
                    "Valuation Analysis",
                    "Cash Flow Management",
                    "Investment Portfolio Design"
                ],
                "certifications": ["CFA", "FRM", "CPA"]
            },
            
            "emma_thompson": {
                "id": "emma_thompson",
                "name": "Emma Thompson",
                "title": "Marketing & Growth Specialist",
                "description": "Creative marketing strategist with expertise in digital marketing, brand development, and growth hacking. Proven track record of scaling startups and established brands through innovative marketing approaches.",
                "avatar": "/avatars/emma.jpg",
                "expertise": ["Marketing", "Brand Strategy", "Growth Hacking", "Digital Marketing", "Customer Acquisition"],
                "personality": {
                    "tone": "creative",
                    "style": "innovative",
                    "traits": ["creative", "energetic", "trend-aware", "experimental", "results-driven"]
                },
                "system_prompt_template": "marketing_expert",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "specializations": [
                    "Performance Marketing",
                    "Content Strategy",
                    "Social Media Marketing",
                    "Conversion Optimization",
                    "Brand Positioning"
                ],
                "tools_expertise": [
                    "Google Analytics",
                    "Facebook Ads",
                    "HubSpot",
                    "Mailchimp",
                    "Canva"
                ]
            },
            
            "alex_kim": {
                "id": "alex_kim",
                "name": "Dr. Alex Kim",
                "title": "Technology & Innovation Consultant",
                "description": "Technology strategist specializing in digital transformation, AI implementation, and innovation management. PhD in Computer Science with extensive experience in enterprise technology adoption.",
                "avatar": "/avatars/alex.jpg",
                "expertise": ["Technology", "AI Strategy", "Digital Transformation", "Innovation Management", "Software Architecture"],
                "personality": {
                    "tone": "analytical",
                    "style": "technical",
                    "traits": ["innovative", "logical", "forward-thinking", "systematic", "pragmatic"]
                },
                "system_prompt_template": "technology_expert",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "specializations": [
                    "AI/ML Implementation",
                    "Cloud Architecture",
                    "Cybersecurity Strategy",
                    "DevOps & Automation",
                    "Technology Due Diligence"
                ],
                "technologies": [
                    "Python",
                    "AWS/Azure/GCP",
                    "Kubernetes",
                    "TensorFlow/PyTorch",
                    "Blockchain"
                ]
            },
            
            "lisa_wang": {
                "id": "lisa_wang",
                "name": "Lisa Wang",
                "title": "Operations & Process Expert",
                "description": "Operations specialist focused on process optimization, supply chain management, and operational excellence. Lean Six Sigma Black Belt with experience in manufacturing and service industries.",
                "avatar": "/avatars/lisa.jpg",
                "expertise": ["Operations", "Process Optimization", "Supply Chain", "Quality Management", "Lean Six Sigma"],
                "personality": {
                    "tone": "professional",
                    "style": "systematic",
                    "traits": ["efficient", "detail-oriented", "process-focused", "analytical", "improvement-minded"]
                },
                "system_prompt_template": "operations_expert",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "specializations": [
                    "Process Reengineering",
                    "Supply Chain Optimization",
                    "Quality Systems",
                    "Performance Metrics",
                    "Change Management"
                ],
                "methodologies": [
                    "Lean Manufacturing",
                    "Six Sigma",
                    "Kaizen",
                    "5S",
                    "Value Stream Mapping"
                ]
            },
            
            "david_brown": {
                "id": "david_brown",
                "name": "David Brown",
                "title": "Human Resources & Talent Expert",
                "description": "HR strategist specializing in talent acquisition, organizational development, and employee engagement. SHRM-SCP certified with expertise in building high-performance teams and culture transformation.",
                "avatar": "/avatars/david.jpg",
                "expertise": ["Human Resources", "Talent Management", "Organizational Development", "Employee Engagement", "Leadership Development"],
                "personality": {
                    "tone": "friendly",
                    "style": "collaborative",
                    "traits": ["empathetic", "people-focused", "strategic", "communicative", "culture-aware"]
                },
                "system_prompt_template": "hr_expert",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "specializations": [
                    "Talent Acquisition Strategy",
                    "Performance Management",
                    "Compensation & Benefits",
                    "Culture Development",
                    "Leadership Coaching"
                ],
                "certifications": ["SHRM-SCP", "SPHR", "ICF-ACC"]
            }
        }
    
    async def get_expert(self, expert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific expert by ID
        """
        try:
            return self.experts.get(expert_id)
        except Exception as e:
            logger.error(f"Error getting expert {expert_id}: {str(e)}")
            return None
    
    async def get_active_experts(self) -> List[Dict[str, Any]]:
        """
        Get all active experts
        """
        try:
            return [
                expert for expert in self.experts.values()
                if expert.get("is_active", False)
            ]
        except Exception as e:
            logger.error(f"Error getting active experts: {str(e)}")
            return []
    
    async def get_experts_by_expertise(self, expertise: str) -> List[Dict[str, Any]]:
        """
        Get experts by specific expertise area
        """
        try:
            matching_experts = []
            for expert in self.experts.values():
                if expertise.lower() in [exp.lower() for exp in expert.get("expertise", [])]:
                    matching_experts.append(expert)
            return matching_experts
        except Exception as e:
            logger.error(f"Error getting experts by expertise {expertise}: {str(e)}")
            return []
    
    async def search_experts(self, query: str) -> List[Dict[str, Any]]:
        """
        Search experts by name, title, description, or expertise
        """
        try:
            query_lower = query.lower()
            matching_experts = []
            
            for expert in self.experts.values():
                if not expert.get("is_active", False):
                    continue
                
                # Search in name, title, description
                searchable_text = " ".join([
                    expert.get("name", ""),
                    expert.get("title", ""),
                    expert.get("description", ""),
                    " ".join(expert.get("expertise", [])),
                    " ".join(expert.get("specializations", []))
                ]).lower()
                
                if query_lower in searchable_text:
                    matching_experts.append(expert)
            
            return matching_experts
        except Exception as e:
            logger.error(f"Error searching experts with query {query}: {str(e)}")
            return []
    
    async def get_expert_recommendations(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get expert recommendations based on user context
        """
        try:
            # Simple recommendation logic based on user's industry or interests
            user_industry = user_context.get("industry", "").lower()
            user_interests = [interest.lower() for interest in user_context.get("interests", [])]
            
            scored_experts = []
            
            for expert in self.experts.values():
                if not expert.get("is_active", False):
                    continue
                
                score = 0
                
                # Score based on industry match
                expert_industries = [ind.lower() for ind in expert.get("industries", [])]
                if user_industry in expert_industries:
                    score += 3
                
                # Score based on expertise match
                expert_expertise = [exp.lower() for exp in expert.get("expertise", [])]
                for interest in user_interests:
                    if any(interest in exp for exp in expert_expertise):
                        score += 2
                
                # Score based on specializations
                expert_specializations = [spec.lower() for spec in expert.get("specializations", [])]
                for interest in user_interests:
                    if any(interest in spec for spec in expert_specializations):
                        score += 1
                
                if score > 0:
                    expert_copy = expert.copy()
                    expert_copy["recommendation_score"] = score
                    scored_experts.append(expert_copy)
            
            # Sort by score and return top recommendations
            scored_experts.sort(key=lambda x: x["recommendation_score"], reverse=True)
            return scored_experts[:4]  # Return top 4 recommendations
            
        except Exception as e:
            logger.error(f"Error getting expert recommendations: {str(e)}")
            return await self.get_active_experts()  # Fallback to all active experts
    
    async def update_expert(self, expert_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update expert configuration
        """
        try:
            if expert_id not in self.experts:
                return False
            
            # Update allowed fields
            allowed_fields = [
                "name", "title", "description", "expertise", "personality",
                "is_active", "specializations", "industries"
            ]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    self.experts[expert_id][field] = value
            
            self.experts[expert_id]["updated_at"] = datetime.now().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Error updating expert {expert_id}: {str(e)}")
            return False
    
    async def get_expert_stats(self, expert_id: str) -> Dict[str, Any]:
        """
        Get usage statistics for an expert (placeholder for future implementation)
        """
        try:
            expert = await self.get_expert(expert_id)
            if not expert:
                return {}
            
            # Placeholder stats - in real implementation, this would query the database
            return {
                "expert_id": expert_id,
                "total_conversations": 0,
                "total_messages": 0,
                "average_rating": 0.0,
                "last_used": None,
                "popular_topics": []
            }
            
        except Exception as e:
            logger.error(f"Error getting expert stats for {expert_id}: {str(e)}")
            return {}