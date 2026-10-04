import React from 'react';
import { motion } from 'framer-motion';

export default function DigestCard({ digest }) {
  if (!digest || !digest.daily_summary) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] p-6 rounded-3xl shadow-sm border border-[var(--color-border-light)] dark:border-[var(--color-border-dark)] mb-8"
    >
      <h2 className="text-2xl font-bold mb-4 text-[var(--color-accent-warm)]">Good Day, Martha 🌼</h2>
      <p className="text-xl leading-relaxed italic text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">
        "{digest.daily_summary}"
      </p>
    </motion.div>
  );
}
