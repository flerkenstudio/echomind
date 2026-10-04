import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { Home, MessageCircle, Users, History, Sun, Moon } from 'lucide-react';

export default function Layout({ darkMode, toggleDarkMode }) {
  const navItems = [
    { to: "/", icon: Home, label: "Home" },
    { to: "/ask", icon: MessageCircle, label: "Ask" },
    { to: "/family", icon: Users, label: "Family" },
    { to: "/history", icon: History, label: "History" },
  ];

  return (
    <div className="min-h-screen flex flex-col max-w-2xl mx-auto px-4 py-6">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-[var(--color-accent-warm)]">EchoMind</h1>
        <button 
          onClick={toggleDarkMode}
          className="p-2 rounded-full hover:bg-[var(--color-border-light)] dark:hover:bg-[var(--color-border-dark)] transition-colors"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun size={24} /> : <Moon size={24} />}
        </button>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <nav className="fixed bottom-0 left-0 right-0 bg-[var(--color-card-light)] dark:bg-[var(--color-card-dark)] border-t border-[var(--color-border-light)] dark:border-[var(--color-border-dark)] px-6 py-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-50">
        <div className="max-w-2xl mx-auto flex justify-between items-center">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => 
                `flex flex-col items-center gap-1 p-2 rounded-xl transition-colors ${
                  isActive 
                    ? 'text-[var(--color-accent-warm)] font-semibold bg-[var(--color-warm-cream)] dark:bg-[var(--color-warm-dark)]' 
                    : 'text-gray-500 hover:text-[var(--color-text-light)] dark:hover:text-[var(--color-text-dark)]'
                }`
              }
            >
              <Icon size={24} />
              <span className="text-sm">{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
      {/* Spacer to prevent content from being hidden behind nav */}
      <div className="h-24"></div>
    </div>
  );
}
