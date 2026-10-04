import React, { useState, useEffect } from 'react';
import { api } from '../api';
import DigestCard from '../components/DigestCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { Calendar } from 'lucide-react';

export default function HistoryPage() {
  const [date, setDate] = useState('2026-10-08');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!date) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const [digestData, remindersData] = await Promise.all([
          api.getDigest(date).catch(() => null),
          api.getReminders(date).catch(() => [])
        ]);
        
        if (!digestData?.daily_summary && (!remindersData || remindersData.length === 0)) {
          setError('No history available for this date.');
          setData(null);
        } else {
          setData({ digest: digestData, reminders: remindersData });
        }
      } catch (err) {
        setError('Failed to load history.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [date]);

  return (
    <div className="pb-10">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">History</h1>
        <div className="flex items-center gap-2 bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] px-3 py-2 rounded-xl border border-[var(--color-border-light)] dark:border-[var(--color-border-dark)]">
          <Calendar size={20} className="text-[var(--color-accent-warm)]" />
          <input 
            type="date" 
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="bg-transparent border-none focus:outline-none text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]"
          />
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="text-center py-12 text-gray-500 bg-[var(--color-warm-cream)] dark:bg-[var(--color-warm-dark)] rounded-2xl">
          <Calendar size={48} className="mx-auto mb-4 opacity-50" />
          <p>{error}</p>
        </div>
      ) : data ? (
        <div className="space-y-6">
          <DigestCard digest={data.digest} />
          
          {data.reminders && data.reminders.length > 0 && (
            <div className="bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] p-6 rounded-3xl border border-[var(--color-border-light)] dark:border-[var(--color-border-dark)]">
              <h3 className="font-bold text-lg mb-4">Reminders from this day</h3>
              <ul className="space-y-3">
                {data.reminders.map(r => (
                  <li key={r.id} className="flex items-center gap-3 text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">
                    <div className={`w-2 h-2 rounded-full ${r.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500'}`} />
                    <span className={r.status === 'completed' ? 'line-through opacity-70' : ''}>{r.action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
