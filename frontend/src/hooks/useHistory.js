import { useEffect, useState } from "react";

const STORAGE_KEY = "phishing_history";
const MAX_ENTRIES = 20;

function readHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.slice(0, MAX_ENTRIES) : [];
  } catch {
    return [];
  }
}

export function useHistory() {
  const [history, setHistory] = useState(readHistory);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(0, MAX_ENTRIES)));
  }, [history]);

  function addEntry(entry) {
    const next = {
      id: crypto.randomUUID(),
      url: entry.url,
      is_phishing: Boolean(entry.is_phishing),
      confidence: Number(entry.confidence),
      risk_level: entry.risk_level,
      timestamp: new Date().toISOString(),
    };
    setHistory((current) => [next, ...current].slice(0, MAX_ENTRIES));
    return next;
  }

  function clearHistory() {
    setHistory([]);
  }

  function removeEntry(id) {
    setHistory((current) => current.filter((item) => item.id !== id));
  }

  return { history, addEntry, clearHistory, removeEntry };
}
