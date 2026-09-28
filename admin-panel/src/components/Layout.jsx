import { useCallback, useEffect, useRef, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { api } from "../api.js";
import { useAuth } from "../auth.jsx";
import { useToast } from "./Toast.jsx";

const POLL_MS = 15000;

export default function Layout() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [notifPermission, setNotifPermission] = useState(
    "Notification" in window ? Notification.permission : "unsupported"
  );
  const previousPending = useRef(null);

  const refreshStats = useCallback(async () => {
    try {
      setStats(await api.stats());
    } catch {
      /* keyingi so'rovda qayta uriniladi */
    }
  }, []);

  useEffect(() => {
    refreshStats();
    const id = setInterval(refreshStats, POLL_MS);
    return () => clearInterval(id);
  }, [refreshStats]);

  // Yangi e'lon kelganda: toast + brauzer bildirishnomasi + sarlavhadagi son
  useEffect(() => {
    if (!stats) return;
    const before = previousPending.current;

    if (before !== null && stats.pending > before) {
      const added = stats.pending - before;
      const text = `Yangi e'lon keldi: ${added} ta tasdiqlashni kutmoqda`;
      toast(text, "alert");
      if (notifPermission === "granted") {
        new Notification("TalantHub", { body: text });
      }
    }

    previousPending.current = stats.pending;
    document.title = stats.pending > 0 ? `(${stats.pending}) TalantHub Admin` : "TalantHub Admin";
  }, [stats, toast, notifPermission]);

  const enableNotifications = async () => {
    setNotifPermission(await Notification.requestPermission());
  };

  const pending = stats?.pending ?? 0;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          TalantHub
          <span>Moderatsiya paneli</span>
        </div>

        <nav>
          <NavLink to="/" end>
            Bosh sahifa
          </NavLink>
          <NavLink to="/announcements">
            E'lonlar
            {pending > 0 && <span className="pill">{pending}</span>}
          </NavLink>
          <NavLink to="/categories">E'lon turlari</NavLink>
          <NavLink to="/users">Foydalanuvchilar</NavLink>
        </nav>

        <div className="sidebar-foot">
          {notifPermission === "default" && (
            <button className="btn btn-amber btn-block" onClick={enableNotifications}>
              Bildirishnomalarni yoqish
            </button>
          )}
          <div className="who">{user?.username}</div>
          <button className="btn btn-ghost-light btn-block" onClick={logout}>
            Chiqish
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet context={{ stats, refreshStats }} />
      </main>
    </div>
  );
}
