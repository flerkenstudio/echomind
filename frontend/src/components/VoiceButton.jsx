import React from 'react';
import { Mic, MicOff } from 'lucide-react';
import { motion } from 'framer-motion';

export default function VoiceButton({ isListening, onToggle, supported }) {
  if (!supported) return null;

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={onToggle}
      type="button"
      className={`p-3 rounded-full flex-shrink-0 transition-colors ${
        isListening 
          ? 'bg-red-500 text-white animate-pulse' 
          : 'bg-[var(--color-warm-cream)] dark:bg-[var(--color-warm-dark)] text-[var(--color-text-light)] dark:text-[var(--color-text-dark)] hover:bg-[var(--color-border-light)] dark:hover:bg-[var(--color-border-dark)]'
      }`}
      aria-label={isListening ? "Stop listening" : "Start listening"}
    >
      {isListening ? <MicOff size={24} /> : <Mic size={24} />}
    </motion.button>
  );
}
