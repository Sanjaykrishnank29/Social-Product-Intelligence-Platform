import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Message {
  role: 'user' | 'model';
  content: string;
}

export const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'model',
      content: "Hello! I'm **SocialIntel AI**, your copilot for this dashboard. I can answer questions about brand metrics, sentiment analysis, reports, alerts, or help you search reviews. Try asking me to compare brands or navigate to pages!"
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [navigatingTo, setNavigatingTo] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: textToSend };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Map history format to ChatMessage type in the backend
      const historyPayload = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await axios.post('http://localhost:8001/api/v1/chat', {
        message: textToSend,
        history: historyPayload
      });

      const { answer, navigate_to } = response.data;

      const assistantMessage: Message = {
        role: 'model',
        content: answer || "I couldn't process that request."
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (navigate_to) {
        setNavigatingTo(navigate_to);
        setTimeout(() => {
          navigate(navigate_to);
          setNavigatingTo(null);
        }, 1500);
      }
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        {
          role: 'model',
          content: "Sorry, I'm having trouble connecting to the backend right now. Make sure the server is running."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (text: string) => {
    handleSend(text);
  };

  // Basic formatter to support bold (**text**) and line breaks in assistant answers
  const formatMessageContent = (text: string) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index} className="font-extrabold text-on-surface">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  const quickSuggestions = [
    "Compare Amazon and Flipkart",
    "Show recent alerts",
    "Show executive insights",
    "Search reviews for 'refund'",
    "Show me Flipkart intelligence",
    "Take me to Reports page"
  ];

  return (
    <div className="fixed bottom-6 right-6 z-[999] font-body-md">
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 rounded-full bg-secondary hover:bg-secondary/95 text-white flex items-center justify-center shadow-xl hover:scale-105 transition-all duration-300 relative group"
        >
          <span className="material-symbols-outlined text-[28px] animate-pulse">chat</span>
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
        </button>
      )}

      {/* Glassmorphic Chat Drawer */}
      {isOpen && (
        <div className="w-[380px] sm:w-[420px] h-[550px] bg-white/70 backdrop-blur-2xl border border-white/40 rounded-[24px] shadow-2xl flex flex-col overflow-hidden transition-all duration-500 transform scale-100 origin-bottom-right">
          {/* Header */}
          <div className="p-4 bg-surface/80 border-b border-outline-variant/30 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/15 flex items-center justify-center text-secondary">
                <span className="material-symbols-outlined text-[24px]">smart_toy</span>
              </div>
              <div>
                <h3 className="font-headline-sm text-[16px] font-bold text-on-surface">SocialIntel Copilot</h3>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  <span className="text-[12px] text-on-surface-variant/80">Online & Ready</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-full hover:bg-black/10 flex items-center justify-center text-on-surface-variant transition-colors"
            >
              <span className="material-symbols-outlined text-[20px]">close</span>
            </button>
          </div>

          {/* Navigation Overlay */}
          {navigatingTo && (
            <div className="absolute inset-0 bg-secondary-container/90 backdrop-blur-sm z-[100] flex flex-col items-center justify-center text-secondary p-6 text-center animate-fade-in">
              <span className="material-symbols-outlined text-[48px] animate-spin mb-3">explore</span>
              <p className="font-bold text-[18px]">Navigating Page...</p>
              <p className="text-[14px] text-on-surface-variant mt-1">Taking you to {navigatingTo}</p>
            </div>
          )}

          {/* Messages Window */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-slate-50/20">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} items-end gap-2`}
              >
                {msg.role === 'model' && (
                  <div className="w-6 h-6 rounded-full bg-secondary/15 flex items-center justify-center text-secondary text-[14px] flex-shrink-0">
                    <span className="material-symbols-outlined text-[14px]">smart_toy</span>
                  </div>
                )}
                <div
                  className={`max-w-[75%] p-3 rounded-2xl text-[14px] leading-relaxed break-words shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-secondary text-white rounded-br-none'
                      : 'bg-white text-on-surface border border-outline-variant/20 rounded-bl-none'
                  }`}
                >
                  <p className="whitespace-pre-line">
                    {msg.role === 'model' ? formatMessageContent(msg.content) : msg.content}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start items-end gap-2">
                <div className="w-6 h-6 rounded-full bg-secondary/15 flex items-center justify-center text-secondary text-[14px] flex-shrink-0">
                  <span className="material-symbols-outlined text-[14px]">smart_toy</span>
                </div>
                <div className="bg-white p-3 rounded-2xl rounded-bl-none border border-outline-variant/20 flex gap-1 shadow-sm items-center h-8">
                  <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant/60 animate-bounce"></span>
                  <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant/60 animate-bounce delay-150"></span>
                  <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant/60 animate-bounce delay-300"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions List */}
          <div className="px-4 py-2 border-t border-outline-variant/20 flex gap-2 overflow-x-auto whitespace-nowrap scrollbar-none bg-white/40">
            {quickSuggestions.map((s, idx) => (
              <button
                key={idx}
                onClick={() => handleQuickAction(s)}
                className="px-3 py-1 bg-surface-container-low hover:bg-secondary hover:text-white border border-outline-variant/30 text-[12px] text-on-surface-variant font-medium rounded-full transition-all cursor-pointer shadow-sm hover:scale-102 flex-shrink-0"
              >
                {s}
              </button>
            ))}
          </div>

          {/* Input Panel */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
            className="p-4 bg-surface/80 border-t border-outline-variant/30 flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="flex-1 bg-white border border-outline-variant/40 rounded-full py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-secondary/20 font-body-md text-[14px] shadow-inner text-on-surface"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="w-10 h-10 rounded-full bg-secondary hover:bg-secondary/95 text-white flex items-center justify-center shadow-md hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:scale-100"
            >
              <span className="material-symbols-outlined text-[20px]">send</span>
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
