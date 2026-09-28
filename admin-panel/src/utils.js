import { useEffect, useState } from "react";

export function useDebounced(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

export function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-GB", { dateStyle: "short", timeStyle: "short" });
}

export const LANGUAGES = { uz: "O'zbekcha", en: "English", ru: "Русский" };
