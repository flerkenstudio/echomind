import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Clock, AlertTriangle } from 'lucide-react';

export default function ReminderCard({ reminder, onAck }) {
  const [isAcking, setIsAcking] = useState(false);
  const isAskedTwice = reminder.priority > 1;
  const isEscalated = reminder.escalated;

  const handleAck = async () => {
    setIsAcking(true);
    await onAck(reminder.id);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={`p-6 rounded-2xl shadow-sm border mb-4 bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] 
        ${isEscalated ? 'border-[var(--color-warning-soft)]' : 'border-[var(--color-border-light)] dark:border-[var(--color-border-dark)]'}
      `}
    >
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-start gap-4">
          <p className="text-xl font-medium flex-1">{reminder.action}</p>
          {isAskedTwice && !isEscalated && (
            <span className="flex items-center gap-1 text-sm bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 px-3 py-1 rounded-full whitespace-nowrap">
              ⭐ Priority
            </span>
          )}
          {isEscalated && (
            <span className="flex items-center gap-1 text-sm bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-3 py-1 rounded-full whitespace-nowrap">
              <AlertTriangle size={14} /> Escalated
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm">
          <Clock size={16} />
          <span>Added: {new Date(reminder.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>

        <button
          onClick={handleAck}
          disabled={isAcking}
          className="mt-2 w-full flex items-center justify-center gap-2 py-4 bg-[var(--color-success-sage)] hover:opacity-90 text-white rounded-xl text-lg font-medium transition-opacity disabled:opacity-50"
        >
          {isAcking ? 'Saving...' : (
            <>
              <Check size={24} /> Got it
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
}
