import React, { useState, useRef, useEffect } from 'react';
import { Leaf, User, Send } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const SimpleChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 判断是否有消息（决定布局模式）
  const hasMessages = messages.length > 0;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Thank you for your message: "${userMessage.content}". This is a simulated AI response demonstrating the chat functionality. I can help you analyze trends, provide insights, and answer various questions.`,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // 渲染输入框组件
  const renderInputBox = (isCenter: boolean = false) => (
    <div className={`${isCenter ? 'w-full max-w-2xl mx-auto' : 'w-full'}`}>
      <div className="relative">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Message IdeaEden..."
          className={`w-full px-6 py-4 pr-14 border border-gray-300 rounded-3xl resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500 shadow-sm ${
            isCenter ? 'text-lg' : 'text-base'
          }`}
          rows={1}
          style={{ 
            minHeight: isCenter ? '56px' : '48px', 
            maxHeight: '120px',
            fontSize: isCenter ? '18px' : '16px',
            lineHeight: '1.5'
          }}
        />
        <button
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          className={`absolute right-2 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 text-white rounded-full flex items-center justify-center hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
            isCenter ? 'w-10 h-10' : 'w-8 h-8'
          }`}
        >
          <Send className={isCenter ? 'w-4 h-4' : 'w-3 h-3'} />
        </button>
      </div>
    </div>
  );

  // 渲染功能按钮
  const renderFeatureButtons = () => (
    <div className="w-full max-w-2xl mx-auto mt-4">
      <div className="flex gap-2 justify-center">
        <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
          <span>🔍</span>
          <span>Keyword Analysis</span>
        </button>
        <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
          <span>🎯</span>
          <span>PMF Evaluation</span>
        </button>
        <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
          <span>📊</span>
          <span>Market Dashboard</span>
        </button>
        <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
          <span>📈</span>
          <span>Analysis Reports</span>
        </button>
      </div>
    </div>
  );



  if (!hasMessages) {
    // 初始状态：中央布局
    return (
      <div className="h-screen bg-white flex flex-col">
        <div className="flex-1 flex flex-col items-center justify-center px-6">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4 mb-12">
            <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 rounded-xl flex items-center justify-center shadow-lg">
              <Leaf className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">IdeaEden</h1>
          </div>

          {/* Center Input Box */}
          {renderInputBox(true)}

          {/* Feature Buttons */}
          {renderFeatureButtons()}
        </div>
      </div>
    );
  }

  // 有消息后：标准聊天布局
  return (
    <div className="h-screen bg-white flex flex-col">
      {/* Top Header */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-lg font-semibold text-gray-900">IdeaEden</h1>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto px-6 py-6 scrollbar-hide">
          <div className="space-y-8">
            {messages.map((message, index) => (
              <div key={message.id}>
                {/* Message Content */}
                <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl ${message.sender === 'user' ? 'text-right' : 'text-left'}`}>
                    {/* Sender Identity */}
                    <div className="flex items-center space-x-2 mb-2">
                      {message.sender === 'ai' && (
                        <>
                          <div className="w-6 h-6 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 rounded-md flex items-center justify-center">
                            <Leaf className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-sm font-medium text-gray-900">IdeaEden</span>
                        </>
                      )}
                      {message.sender === 'user' && (
                        <div className="flex items-center space-x-2 justify-end">
                          <span className="text-sm font-medium text-gray-900">You</span>
                          <div className="w-6 h-6 bg-gray-700 rounded-md flex items-center justify-center">
                            <User className="w-4 h-4 text-white" />
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Message Text */}
                    <div className={`prose prose-sm max-w-none ${
                      message.sender === 'user' 
                        ? 'text-gray-900' 
                        : 'text-gray-800'
                    }`}>
                      <p className="whitespace-pre-wrap leading-relaxed m-0">
                        {message.content}
                      </p>
                    </div>
                    
                    {/* Timestamp */}
                    <div className={`text-xs text-gray-500 mt-2 ${
                      message.sender === 'user' ? 'text-right' : 'text-left'
                    }`}>
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
                
                {/* Message Separator */}
                {index < messages.length - 1 && (
                  <div className="border-b border-gray-100 mt-8"></div>
                )}
              </div>
            ))}
            
            {/* AI Typing Animation */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-3xl">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 rounded-md flex items-center justify-center">
                      <Leaf className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm font-medium text-gray-900">IdeaEden</span>
                  </div>
                  <div className="flex items-center space-x-1 py-3">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Input Area */}
        <div className="flex-shrink-0 border-t border-gray-200 bg-white">
          <div className="px-6 py-4">
            {renderInputBox(false)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleChatPage;