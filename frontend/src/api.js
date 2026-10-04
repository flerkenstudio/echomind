const BASE_URL = '/api';

export const api = {
  getHealth: async () => {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error('Network response was not ok');
    return res.json();
  },
  getDigest: async (date) => {
    const res = await fetch(`${BASE_URL}/digest/${date}`);
    if (!res.ok) throw new Error('Failed to fetch digest');
    return res.json();
  },
  getReminders: async (date) => {
    const res = await fetch(`${BASE_URL}/reminders/${date}`);
    if (!res.ok) throw new Error('Failed to fetch reminders');
    return res.json();
  },
  ackReminder: async (date, id) => {
    const res = await fetch(`${BASE_URL}/reminders/${date}/${id}/ack`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to ack reminder');
    return res.json();
  },
  tickReminders: async (date) => {
    const res = await fetch(`${BASE_URL}/reminders/tick?date=${date}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to tick reminders');
    return res.json();
  },
  addReminder: async (date, action) => {
    const res = await fetch(`${BASE_URL}/reminders/${date}/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    if (!res.ok) throw new Error('Failed to add reminder');
    return res.json();
  },
  askQuestion: async (date, question) => {
    const res = await fetch(`${BASE_URL}/qa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date, question })
    });
    if (!res.ok) throw new Error('Failed to ask question');
    return res.json();
  },
  getCaregiverSignals: async (date) => {
    const res = await fetch(`${BASE_URL}/caregiver/${date}`);
    if (!res.ok) throw new Error('Failed to fetch caregiver signals');
    return res.json();
  }
};
