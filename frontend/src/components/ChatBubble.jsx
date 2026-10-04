import React from 'react';
import { motion } from 'framer-motion';
import { Mic } from 'lucide-react';

export default function ChatBubble({ message, onAddReminder }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col mb-6 ${isUser ? 'items-end' : 'items-start'}`}
    >
      <div 
        className={`max-w-[85%] p-4 rounded-2xl ${
          isUser 
            ? 'bg-[var(--color-accent-warm)] text-white rounded-br-none' 
            : 'bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] border border-[var(--color-border-light)] dark:border-[var(--color-border-dark)] rounded-bl-none'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        
        {!isUser && message.citation && (
          <div className="mt-3 text-sm flex items-center gap-1 text-gray-500 dark:text-gray-400 border-t border-gray-100 dark:border-gray-700 pt-2">
            <Mic size={14} />
            <span>heard at {new Date(message.citation.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        )}
      </div>

      {!isUser && message.offer_reminder && (
        <button
          onClick={() => onAddReminder(message.offer_reminder)}
          className="mt-2 text-sm bg-[var(--color-success-sage)] text-white px-4 py-2 rounded-full hover:opacity-90 transition-opacity flex items-center gap-2"
        >
          Yes, remind me
        </button>
      )}
    </motion.div>
  );
}
