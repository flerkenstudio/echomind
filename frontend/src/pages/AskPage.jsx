import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import ChatBubble from '../components/ChatBubble';
import VoiceButton from '../components/VoiceButton';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { Send } from 'lucide-react';

const DEFAULT_DATE = '2026-10-08';

export default function AskPage() {
  const [messages, setMessages] = useState([
    { role: 'bot', content: "Hello Martha! Is there anything you'd like to ask me about today?" }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  
  const { supported, isListening, transcript, startListening, stopListening, setTranscript } = useSpeechRecognition();

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isTyping) return;

    const userMsg = input.trim();
    setInput('');
    setTranscript('');
    
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsTyping(true);

    try {
      const response = await api.askQuestion(DEFAULT_DATE, userMsg);
      setMessages(prev => [...prev, {
        role: 'bot',
        content: response.answer,
        citation: response.citation,
        offer_reminder: response.offer_reminder
      }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        role: 'bot',
        content: "I'm having a little trouble thinking right now. Could you ask me again?"
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleToggleVoice = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleAddReminder = async (actionText) => {
    try {
      await api.addReminder(DEFAULT_DATE, actionText);
      setMessages(prev => [...prev, {
        role: 'bot',
        content: `I've added a reminder to: "${actionText}". I'll remind you about it later.`
      }]);
    } catch (err) {
      console.error(err);
      alert('Failed to add reminder');
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)]">
      <div className="flex-1 overflow-y-auto pr-2 pb-4 space-y-4">
        {messages.map((msg, idx) => (
          <ChatBubble key={idx} message={msg} onAddReminder={handleAddReminder} />
        ))}
        {isTyping && (
          <div className="text-gray-500 italic flex items-center gap-2 p-4">
            EchoMind is thinking... <span className="animate-pulse">🌼</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2 items-center bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] p-2 rounded-2xl border border-[var(--color-border-light)] dark:border-[var(--color-border-dark)] shadow-sm">
        <VoiceButton 
          isListening={isListening} 
          onToggle={handleToggleVoice} 
          supported={supported} 
        />
        
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          className="flex-1 bg-transparent border-none focus:outline-none text-lg px-2 text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]"
          disabled={isTyping || isListening}
        />
        
        <button
          type="submit"
          disabled={!input.trim() || isTyping}
          className="p-3 bg-[var(--color-accent-warm)] text-white rounded-full hover:opacity-90 disabled:opacity-50 transition-opacity flex-shrink-0"
        >
          <Send size={24} />
        </button>
      </form>
    </div>
  );
}
