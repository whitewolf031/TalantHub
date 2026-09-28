import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, tokenStore } from "./api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(Boolean(tokenStore.get()));

  // Sahifa yangilanganda token hali yaroqli ekanini tekshiramiz
  useEffect(() => {
    if (!tokenStore.get()) return;
    api
      .me()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setChecking(false));
  }, []);

  // api.js 401 olsa, shu hodisa orqali login sahifasiga qaytariladi
  useEffect(() => {
    const onLogout = () => setUser(null);
    window.addEventListener("auth:logout", onLogout);
    return () => window.removeEventListener("auth:logout", onLogout);
  }, []);

  const login = useCallback(async (username, password) => {
    const data = await api.login(username, password);
    tokenStore.set(data.token);
    setUser(data.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      /* token allaqachon yaroqsiz bo'lishi mumkin */
    }
    tokenStore.clear();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, checking, login, logout }}>{children}</AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
