import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import Modal from "../components/Modal.jsx";
import Pagination from "../components/Pagination.jsx";
import { useToast } from "../components/Toast.jsx";
import { LANGUAGES, formatDate, useDebounced } from "../utils.js";

export default function UsersPage() {
  const toast = useToast();
  const [data, setData] = useState({ count: 0, results: [] });
  const [loaded, setLoaded] = useState(false);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [blocked, setBlocked] = useState("");
  const [editing, setEditing] = useState(null);
  const debouncedSearch = useDebounced(search);

  const load = useCallback(async () => {
    try {
      setData(await api.users({ search: debouncedSearch, blocked, page }));
    } catch (err) {
      if (err.status === 404 && page > 1) setPage(1);
      else toast(err.message, "error");
    } finally {
      setLoaded(true);
    }
  }, [debouncedSearch, blocked, page, toast]);

  useEffect(() => {
    load();
  }, [load]);

  const toggleBlock = async (u) => {
    const question = u.is_blocked
      ? `${u.first_name || u.telegram_id} blokdan chiqarilsinmi?`
      : `${u.first_name || u.telegram_id} bloklansinmi? U yangi e'lon joylay olmaydi.`;
    if (!window.confirm(question)) return;
    try {
      await api.toggleBlock(u.id);
      toast(u.is_blocked ? "Blokdan chiqarildi" : "Bloklandi");
      load();
    } catch (err) {
      toast(err.message, "error");
    }
  };

  const remove = async (u) => {
    if (!window.confirm(`${u.first_name || u.telegram_id} va uning barcha e'lonlari o'chiriladi. Davom etasizmi?`)) return;
    try {
      await api.deleteUser(u.id);
      toast("O'chirildi");
      load();
    } catch (err) {
      toast(err.message, "error");
    }
  };

  return (
    <>
      <h1>Foydalanuvchilar</h1>

      <div className="toolbar">
        <input
          placeholder="Ism, username, telefon yoki Telegram ID bo'yicha qidirish"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <select
          value={blocked}
          onChange={(e) => {
            setBlocked(e.target.value);
            setPage(1);
          }}
        >
          <option value="">Hammasi</option>
          <option value="false">Faol</option>
          <option value="true">Bloklangan</option>
        </select>
      </div>

      {!loaded ? (
        <p className="muted">Yuklanmoqda…</p>
      ) : data.results.length === 0 ? (
        <p className="empty">Foydalanuvchi topilmadi.</p>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Telegram ID</th>
                <th>Ism</th>
                <th>Telefon</th>
                <th>Til</th>
                <th>E'lonlar</th>
                <th>Oxirgi faollik</th>
                <th>Holat</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((u) => (
                <tr key={u.id} className={u.is_blocked ? "row-muted" : ""}>
                  <td>{u.telegram_id}</td>
                  <td>
                    <strong>{u.first_name || "—"}</strong>
                    <div className="muted">{u.username ? `@${u.username}` : ""}</div>
                  </td>
                  <td>{u.phone_number || "—"}</td>
                  <td>{LANGUAGES[u.language] || u.language}</td>
                  <td>{u.announcements_count}</td>
                  <td>{formatDate(u.last_activity_at)}</td>
                  <td>
                    {u.is_blocked ? (
                      <span className="badge badge-rejected">Bloklangan</span>
                    ) : (
                      <span className="badge badge-approved">Faol</span>
                    )}
                  </td>
                  <td className="actions">
                    <button className="btn btn-ghost" onClick={() => setEditing(u)}>
                      Tahrirlash
                    </button>
                    <button className={u.is_blocked ? "btn btn-ok" : "btn btn-danger-outline"} onClick={() => toggleBlock(u)}>
                      {u.is_blocked ? "Blokdan chiqarish" : "Bloklash"}
                    </button>
                    <button className="btn btn-ghost" onClick={() => remove(u)}>
                      O'chirish
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} count={data.count} onChange={setPage} />

      {editing && (
        <UserForm
          user={editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            toast("Saqlandi");
            load();
          }}
        />
      )}
    </>
  );
}

function UserForm({ user, onClose, onSaved }) {
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    first_name: user.first_name || "",
    username: user.username || "",
    phone_number: user.phone_number || "",
    language: user.language,
    is_blocked: user.is_blocked,
  });
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.updateUser(user.id, form);
      onSaved();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={`Foydalanuvchi ${user.telegram_id}`} onClose={onClose}>
      <form className="form-grid" onSubmit={submit}>
        <label className="span-2">
          Ism
          <input value={form.first_name} onChange={set("first_name")} />
        </label>
        <label>
          Username (@ belgisiz)
          <input value={form.username} onChange={set("username")} />
        </label>
        <label>
          Telefon
          <input value={form.phone_number} onChange={set("phone_number")} />
        </label>
        <label className="span-2">
          Til
          <select value={form.language} onChange={set("language")}>
            {Object.entries(LANGUAGES).map(([code, name]) => (
              <option key={code} value={code}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="check span-2">
          <input
            type="checkbox"
            checked={form.is_blocked}
            onChange={(e) => setForm({ ...form, is_blocked: e.target.checked })}
          />
          Bloklangan (yangi e'lon joylay olmaydi)
        </label>
        <div className="modal-actions span-2">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Bekor qilish
          </button>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? "Saqlanmoqda…" : "Saqlash"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
