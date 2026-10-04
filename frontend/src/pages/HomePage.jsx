import React, { useState, useEffect } from 'react';
import { api } from '../api';
import DigestCard from '../components/DigestCard';
import ReminderCard from '../components/ReminderCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { RefreshCw, Moon } from 'lucide-react';
import { useNotifications } from '../hooks/useNotifications';

const DEFAULT_DATE = '2026-10-08';

export default function HomePage() {
  const [digest, setDigest] = useState(null);
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ticking, setTicking] = useState(false);
  
  const { sendNotification } = useNotifications();

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [digestData, remindersData] = await Promise.all([
        api.getDigest(DEFAULT_DATE).catch(() => null),
        api.getReminders(DEFAULT_DATE).catch(() => [])
      ]);
      if (digestData) setDigest(digestData);
      setReminders(remindersData || []);
    } catch (err) {
      setError('Failed to load data. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAck = async (id) => {
    try {
      await api.ackReminder(DEFAULT_DATE, id);
      setReminders(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      console.error('Failed to ack reminder:', err);
      alert('Failed to save. Please try again.');
    }
  };

  const handleTick = async () => {
    try {
      setTicking(true);
      const res = await api.tickReminders(DEFAULT_DATE);
      if (res.triggered && res.triggered.length > 0) {
        res.triggered.forEach(r => {
          sendNotification('EchoMind Reminder', r.action);
        });
      }
      await loadData();
    } catch (err) {
      console.error('Failed to simulate check-in:', err);
      alert('Failed to simulate check-in.');
    } finally {
      setTicking(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="pb-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">Today</h1>
        <div className="flex gap-2">
          <button 
            onClick={handleTick}
            disabled={ticking}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[var(--color-warm-cream)] dark:bg-[var(--color-warm-dark)] hover:bg-[var(--color-border-light)] dark:hover:bg-[var(--color-border-dark)] text-sm transition-colors disabled:opacity-50"
            title="Simulate evening check-in"
          >
            <Moon size={16} /> Check-in
          </button>
          <button 
            onClick={loadData}
            className="p-1.5 rounded-lg bg-[var(--color-warm-cream)] dark:bg-[var(--color-warm-dark)] hover:bg-[var(--color-border-light)] dark:hover:bg-[var(--color-border-dark)] transition-colors"
            title="Refresh"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 mb-6 bg-red-50 text-red-700 rounded-xl">
          {error}
        </div>
      )}

      <DigestCard digest={digest} />

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4 text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">
          {reminders.length > 0 ? "Your Reminders" : "All caught up for today!"}
        </h2>
        
        <div className="space-y-4">
          {reminders.map(reminder => (
            <ReminderCard key={reminder.id} reminder={reminder} onAck={handleAck} />
          ))}
        </div>
      </div>
    </div>
  );
}
