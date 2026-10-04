import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import AskPage from './pages/AskPage';
import FamilyPage from './pages/FamilyPage';
import HistoryPage from './pages/HistoryPage';
import { useNotifications } from './hooks/useNotifications';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('theme') === 'dark';
  });

  // Initialize notifications
  useNotifications();

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  return (
    <Routes>
      <Route path="/" element={<Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode} />}>
        <Route index element={<HomePage />} />
        <Route path="ask" element={<AskPage />} />
        <Route path="family" element={<FamilyPage />} />
        <Route path="history" element={<HistoryPage />} />
      </Route>
    </Routes>
  );
}

export default App;
