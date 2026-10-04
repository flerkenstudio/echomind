import React from 'react';
import { Repeat, Clock, AlertTriangle } from 'lucide-react';

export default function SignalCard({ type, items }) {
  if (!items || items.length === 0) return null;

  const getConfig = () => {
    switch (type) {
      case 'repeated':
        return {
          icon: Repeat,
          title: "Repeated Topics",
          color: "text-blue-600 dark:text-blue-400",
          bg: "bg-blue-50 dark:bg-blue-900/20",
          border: "border-blue-100 dark:border-blue-800"
        };
      case 'pending':
        return {
          icon: Clock,
          title: "Pending Reminders",
          color: "text-yellow-600 dark:text-yellow-400",
          bg: "bg-yellow-50 dark:bg-yellow-900/20",
          border: "border-yellow-100 dark:border-yellow-800"
        };
      case 'escalated':
        return {
          icon: AlertTriangle,
          title: "Needs Attention",
          color: "text-red-600 dark:text-red-400",
          bg: "bg-red-50 dark:bg-red-900/20",
          border: "border-red-100 dark:border-red-800"
        };
      default:
        return {};
    }
  };

  const config = getConfig();
  const Icon = config.icon;

  return (
    <div className={`p-5 rounded-2xl border ${config.border} ${config.bg} mb-4`}>
      <div className={`flex items-center gap-2 mb-3 ${config.color}`}>
        <Icon size={20} />
        <h3 className="font-semibold text-lg">{config.title}</h3>
      </div>
      <ul className="space-y-3">
        {items.map((item, idx) => (
          <li key={idx} className="flex justify-between items-start gap-4">
            <span className="text-[var(--color-text-light)] dark:text-[var(--color-text-dark)]">
              {item.topic || item.action}
            </span>
            {item.count && (
              <span className={`px-2 py-1 rounded-full text-sm font-medium ${config.color} bg-white dark:bg-black/20`}>
                {item.count}x
              </span>
            )}
            {item.boost && item.boost > 0 && (
              <span className={`px-2 py-1 rounded-full text-sm font-medium ${config.color} bg-white dark:bg-black/20`}>
                Boost: {item.boost}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
