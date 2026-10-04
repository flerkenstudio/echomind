import React from 'react';

export default function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-[var(--color-warm-cream)] border-t-[var(--color-accent-warm)]"></div>
    </div>
  );
}
