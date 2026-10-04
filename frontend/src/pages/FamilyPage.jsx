import React, { useState, useEffect } from 'react';
import { api } from '../api';
import SignalCard from '../components/SignalCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { ShieldCheck, RefreshCw } from 'lucide-react';

const DEFAULT_DATE = '2026-10-08';

export default function FamilyPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getCaregiverSignals(DEFAULT_DATE);
      setData(res);
    } catch (err) {
      setError('Failed to load caregiver signals.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="pb-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">Family Overview</h1>
        <button 
          onClick={loadData}
          className="p-2 rounded-lg bg-[var(--color-warm-cream)] dark:bg-[var(--color-warm-dark)] hover:bg-[var(--color-border-light)] dark:hover:bg-[var(--color-border-dark)] transition-colors"
        >
          <RefreshCw size={20} />
        </button>
      </div>

      <div className="bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300 p-4 rounded-xl flex items-start gap-3 mb-8 text-sm">
        <ShieldCheck className="flex-shrink-0 mt-0.5" />
        <p>Privacy Notice: Martha's private conversations stay private. This view only highlights recurring patterns and items needing attention to help you support her better.</p>
      </div>

      {error && (
        <div className="p-4 mb-6 bg-red-50 text-red-700 rounded-xl">
          {error}
        </div>
      )}

      {data && (
        <div className="space-y-6">
          {data.escalated && data.escalated.length > 0 && (
            <div className="bg-red-100 dark:bg-red-900/40 p-4 rounded-xl border border-red-200 dark:border-red-800 mb-6">
              <h2 className="text-red-800 dark:text-red-200 font-bold mb-2 flex items-center gap-2">
                Action Required
              </h2>
              <p className="text-red-700 dark:text-red-300 text-sm">
                There are items that Martha has missed multiple times and may need your help with.
              </p>
            </div>
          )}

          {data.daily_summary && (
            <div className="bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] p-6 rounded-2xl border border-[var(--color-border-light)] dark:border-[var(--color-border-dark)]">
              <h3 className="font-semibold text-gray-500 dark:text-gray-400 mb-2 uppercase text-sm tracking-wider">Martha's Day</h3>
              <p className="italic text-lg text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">"{data.daily_summary}"</p>
            </div>
          )}

          <div className="mt-8">
            <h3 className="font-bold text-xl mb-4">Insights & Signals</h3>
            
            {data.escalated && data.escalated.length > 0 && (
              <SignalCard type="escalated" items={data.escalated} />
            )}
            
            {data.repeated_topics && data.repeated_topics.length > 0 && (
              <SignalCard type="repeated" items={data.repeated_topics} />
            )}
            
            {data.pending_reminders && data.pending_reminders.length > 0 && (
              <SignalCard type="pending" items={data.pending_reminders} />
            )}

            {(!data.escalated?.length && !data.repeated_topics?.length && !data.pending_reminders?.length) && (
              <div className="text-center py-8 text-gray-500">
                No active signals to display right now. Everything looks good!
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
