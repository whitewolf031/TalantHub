import { useCallback, useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { api } from "../api.js";
import Modal from "../components/Modal.jsx";
import Pagination from "../components/Pagination.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { useToast } from "../components/Toast.jsx";
import { formatDate, useDebounced } from "../utils.js";

const TABS = [
  { key: "pending", label: "Kutilmoqda" },
  { key: "payment_pending", label: "To'lov tekshiruvi" },
  { key: "waiting_payment", label: "To'lov kutilmoqda" },
  { key: "approved", label: "Tasdiqlangan" },
  { key: "rejected", label: "Rad etilgan" },
  { key: "", label: "Hammasi" },
];

export default function AnnouncementsPage() {
  const { stats, refreshStats } = useOutletContext();
  const toast = useToast();

  const [tab, setTab] = useState("pending");
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [categories, setCategories] = useState([]);
  const [data, setData] = useState({ count: 0, results: [] });
  const [loaded, setLoaded] = useState(false);
  const [openId, setOpenId] = useState(null);
  const [rejecting, setRejecting] = useState(null);
  const debouncedSearch = useDebounced(search);

  useEffect(() => {
    api.categories().then(setCategories).catch(() => {});
  }, []);

  const load = useCallback(async () => {
    try {
      setData(await api.announcements({ status: tab, category, search: debouncedSearch, page }));
    } catch (err) {
      if (err.status === 404 && page > 1) setPage(1); // oxirgi sahifadagi e'lonlar tugagan
      else toast(err.message, "error");
    } finally {
      setLoaded(true);
    }
  }, [tab, category, debouncedSearch, page, toast]);

  // Filtr o'zgarganda yoki yangi e'lon kelganda (stats o'zgarganda) ro'yxat yangilanadi
  useEffect(() => {
    load();
  }, [load, stats?.pending, stats?.payment_pending, stats?.waiting_payment, stats?.approved, stats?.rejected]);

  const afterChange = async () => {
    setOpenId(null);
    setRejecting(null);
    await load();
    refreshStats();
  };

  const approve = async (a) => {
    if (a.status === "payment_pending") {
      if (!window.confirm(`«${a.full_name}»ning to'lovi tasdiqlanib, e'lon kanalga yuboriladi. Tasdiqlaysizmi?`)) return;
      try {
        await api.approvePayment(a.id);
        toast("To'lov tasdiqlandi va e'lon kanalga yuborildi");
      } catch (err) {
        toast(err.message, "error");
      }
      afterChange();
      return;
    }

    if (a.is_premium && a.status === "pending") {
      if (!window.confirm(`«${a.full_name}» e'loni ma'qullanadi va foydalanuvchiga to'lov so'rovi yuboriladi. Tasdiqlaysizmi?`)) return;
      try {
        await api.approveAnnouncement(a.id);
        toast("E'lon ma'qullandi, to'lov so'rovi yuborildi");
      } catch (err) {
        toast(err.message, "error");
      }
      afterChange();
      return;
    }

    if (!window.confirm(`«${a.full_name}» e'loni kanalga yuboriladi. Tasdiqlaysizmi?`)) return;
    try {
      await api.approveAnnouncement(a.id);
      toast("Tasdiqlandi va kanalga yuborildi");
    } catch (err) {
      toast(err.message, "error");
    }
    afterChange();
  };

  const reject = async (a, reason) => {
    try {
      if (a.status === "payment_pending") {
        await api.rejectPayment(a.id, reason);
        toast("To'lov rad etildi");
      } else {
        await api.rejectAnnouncement(a.id, reason);
        toast("E'lon rad etildi");
      }
    } catch (err) {
      toast(err.message, "error");
    }
    afterChange();
  };

  const remove = async (a) => {
    if (!window.confirm(`#${a.id} e'lonni butunlay o'chirasizmi? Bu amalni qaytarib bo'lmaydi.`)) return;
    try {
      await api.deleteAnnouncement(a.id);
      toast("E'lon o'chirildi");
    } catch (err) {
      toast(err.message, "error");
    }
    afterChange();
  };

  const changeTab = (key) => {
    setTab(key);
    setPage(1);
  };

  const opened = data.results.find((a) => a.id === openId);
  const countFor = (key) => (key ? stats?.[key] : undefined);

  return (
    <>
      <h1>E'lonlar</h1>

      <div className="tabs">
        {TABS.map((t) => (
          <button key={t.key} className={tab === t.key ? "tab active" : "tab"} onClick={() => changeTab(t.key)}>
            {t.label}
            {countFor(t.key) !== undefined && <span className="tab-count">{countFor(t.key)}</span>}
          </button>
        ))}
      </div>

      <div className="toolbar">
        <input
          placeholder="Ism, telefon, username yoki yo'nalish bo'yicha qidirish"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setPage(1);
          }}
        >
          <option value="">Barcha turlar</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.emoji} {c.name_uz}
            </option>
          ))}
        </select>
      </div>

      {!loaded ? (
        <p className="muted">Yuklanmoqda…</p>
      ) : data.results.length === 0 ? (
        <p className="empty">
          {tab === "pending" ? "Kutilayotgan e'lon yo'q." : "Bu filtr bo'yicha e'lon topilmadi."}
        </p>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Turi</th>
                <th>Ism</th>
                <th>Yo'nalish</th>
                <th>Aloqa</th>
                <th>Oylik</th>
                <th>Kelgan vaqti</th>
                <th>Holat</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.results.map((a) => (
                <tr key={a.id} className={a.status === "pending" ? "row-pending" : ""}>
                  <td>#{a.id}</td>
                  <td>
                    {a.category.emoji} {a.category.name_uz}
                    {a.is_premium && (
                      <span
                        style={{
                          marginLeft: "6px",
                          fontSize: "11px",
                          background: "#e0e7ff",
                          color: "#3730a3",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontWeight: "600",
                        }}
                      >
                        💎 Premium
                      </span>
                    )}
                  </td>
                  <td>
                    <strong>{a.full_name}</strong>
                    <div className="muted">{a.age} yosh</div>
                  </td>
                  <td>{a.direction}</td>
                  <td>
                    {a.phone_number}
                    <div className="muted">{a.telegram_username}</div>
                  </td>
                  <td>{a.salary_display}</td>
                  <td>{formatDate(a.created_at)}</td>
                  <td>
                    <StatusBadge status={a.status} />
                  </td>
                  <td className="actions">
                    <button className="btn btn-ghost" onClick={() => setOpenId(a.id)}>
                      Ko'rish
                    </button>
                    {(a.status === "pending" || a.status === "payment_pending") && (
                      <>
                        <button className="btn btn-ok" onClick={() => approve(a)}>
                          {a.status === "payment_pending"
                            ? "To'lovni tasdiqlash"
                            : a.is_premium
                            ? "Ma'qullash"
                            : "Tasdiqlash"}
                        </button>
                        <button className="btn btn-danger-outline" onClick={() => setRejecting(a)}>
                          Rad etish
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} count={data.count} onChange={setPage} />

      {opened && (
        <AnnouncementModal
          announcement={opened}
          categories={categories}
          onClose={() => setOpenId(null)}
          onApprove={() => approve(opened)}
          onReject={() => setRejecting(opened)}
          onDelete={() => remove(opened)}
          onSaved={() => {
            toast("Saqlandi");
            load();
          }}
        />
      )}

      {rejecting && <RejectModal announcement={rejecting} onClose={() => setRejecting(null)} onConfirm={reject} />}
    </>
  );
}

function RejectModal({ announcement, onClose, onConfirm }) {
  const [reason, setReason] = useState("");
  return (
    <Modal title={`#${announcement.id} e'lonni rad etish`} onClose={onClose}>
      <label>
        Sabab (ixtiyoriy — foydalanuvchiga yuboriladi)
        <textarea rows={3} value={reason} onChange={(e) => setReason(e.target.value)} maxLength={255} />
      </label>
      <div className="modal-actions">
        <button className="btn btn-ghost" onClick={onClose}>
          Bekor qilish
        </button>
        <button className="btn btn-danger" onClick={() => onConfirm(announcement, reason)}>
          Rad etish
        </button>
      </div>
    </Modal>
  );
}

function AnnouncementModal({ announcement: a, categories, onClose, onApprove, onReject, onDelete, onSaved }) {
  const toast = useToast();
  const [editing, setEditing] = useState(false);
  const [deletingResume, setDeletingResume] = useState(false);

  const handleDeleteResume = async () => {
    if (!window.confirm("Rostdan ham ushbu rezyume faylini serverdan o'chirmoqchimisiz?")) return;
    setDeletingResume(true);
    try {
      await api.deleteResume(a.id);
      toast("Rezyume fayli muvaffaqiyatli o'chirildi");
      onSaved();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setDeletingResume(false);
    }
  };

  if (editing) {
    return (
      <Modal title={`#${a.id} e'lonni tahrirlash`} onClose={onClose} wide>
        <EditForm
          announcement={a}
          categories={categories}
          onCancel={() => setEditing(false)}
          onSaved={() => {
            setEditing(false);
            onSaved();
          }}
        />
      </Modal>
    );
  }

  const rows = [
    ["Turi", `${a.category.emoji} ${a.category.name_uz}`],
    ["Tarif", a.is_premium ? "💎 Premium (Pullik)" : "Oddiy (Bepul)"],
  ];

  if (a.is_premium) {
    rows.push(["Chiqarilish soni", `${a.post_count || 0} / 4 marta`]);
    if (a.next_publish_date) rows.push(["Keyingi chiqarilish", formatDate(a.next_publish_date)]);
    if (a.linkedin_url) {
      rows.push([
        "LinkedIn",
        <a href={a.linkedin_url} target="_blank" rel="noreferrer" key="linkedin">
          {a.linkedin_url}
        </a>,
      ]);
    }
    if (a.portfolio_url) {
      rows.push([
        "Portfolio",
        <a href={a.portfolio_url} target="_blank" rel="noreferrer" key="portfolio">
          {a.portfolio_url}
        </a>,
      ]);
    }
    if (a.resume_file_url) {
      rows.push([
        "Rezyume fayli",
        <div key="resume" style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <a href={a.resume_file_url} target="_blank" rel="noreferrer" className="btn btn-ghost" style={{ padding: "4px 8px" }}>
            📄 Yuklab olish
          </a>
          <button className="btn btn-danger-outline" style={{ padding: "4px 8px" }} onClick={handleDeleteResume} disabled={deletingResume}>
            🗑 Rezyumeni o'chirish
          </button>
        </div>,
      ]);
    } else if (a.resume_deleted_at) {
      rows.push(["Rezyume fayli", <span className="muted" key="resume-del">Rezyume o'chirilgan ({formatDate(a.resume_deleted_at)})</span>]);
    }
    if (a.payment_receipt_url) {
      rows.push([
        "To'lov cheki",
        <a href={a.payment_receipt_url} target="_blank" rel="noreferrer" key="receipt">
          <img
            src={a.payment_receipt_url}
            alt="To'lov cheki"
            style={{ maxWidth: "200px", maxHeight: "200px", objectFit: "contain", border: "1px solid #cbd5e1", borderRadius: "6px", marginTop: "4px" }}
          />
        </a>,
      ]);
    }
  }

  rows.push(
    ["Ism", a.full_name],
    ["Yosh", a.age],
    ["Yo'nalish", a.direction],
    ["Texnologiyalar", a.technologies],
    ["Qaysi shahardan", a.city_from],
    ["Qidirilayotgan shahar", a.city_looking],
    ["Oylik", a.salary_display],
    ["Murojaat vaqti", a.contact_time_display],
    ["Telefon", a.phone_number],
    ["Telegram", a.telegram_username],
    ["Maqsad", a.purpose],
    ["Yuboruvchi", `${a.user.first_name || "—"} ${a.user.username ? `(@${a.user.username})` : ""} · ID ${a.user.telegram_id}`],
    ["Kelgan vaqti", formatDate(a.created_at)]
  );

  if (a.status === "approved") rows.push(["Tasdiqlangan vaqti", formatDate(a.approved_at)]);
  if (a.status === "rejected") {
    rows.push(["Rad etilgan vaqti", formatDate(a.rejected_at)]);
    if (a.reject_reason) rows.push(["Rad etish sababi", a.reject_reason]);
  }

  return (
    <Modal title={`E'lon #${a.id}`} onClose={onClose} wide>
      <div className="modal-status">
        <StatusBadge status={a.status} />
        {a.is_premium && (
          <span style={{ fontSize: "12px", background: "#e0e7ff", color: "#3730a3", padding: "3px 8px", borderRadius: "4px", fontWeight: "600" }}>
            💎 Premium
          </span>
        )}
        {a.user.is_blocked && <span className="badge badge-rejected">Foydalanuvchi bloklangan</span>}
      </div>

      <dl className="details">
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <div className="modal-actions">
        <button className="btn btn-danger-outline push-left" onClick={onDelete}>
          O'chirish
        </button>
        <button className="btn btn-ghost" onClick={() => setEditing(true)}>
          Tahrirlash
        </button>
        {(a.status === "pending" || a.status === "payment_pending") && (
          <>
            <button className="btn btn-danger-outline" onClick={onReject}>
              {a.status === "payment_pending" ? "To'lovni rad etish" : "Rad etish"}
            </button>
            <button className="btn btn-ok" onClick={onApprove}>
              {a.status === "payment_pending"
                ? "To'lovni tasdiqlash va kanalga chiqarish"
                : a.is_premium
                ? "Ma'qullash (To'lov so'rash)"
                : "Tasdiqlash va kanalga yuborish"}
            </button>
          </>
        )}
      </div>
    </Modal>
  );
}

function EditForm({ announcement: a, categories, onCancel, onSaved }) {
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    category: a.category.id,
    full_name: a.full_name,
    age: a.age,
    direction: a.direction,
    technologies: a.technologies,
    telegram_username: a.telegram_username,
    phone_number: a.phone_number,
    city_from: a.city_from,
    city_looking: a.city_looking,
    salary_amount: a.salary_amount,
    salary_currency: a.salary_currency,
    contact_time_start: a.contact_time_start.slice(0, 5),
    contact_time_end: a.contact_time_end.slice(0, 5),
    purpose: a.purpose,
  });
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.updateAnnouncement(a.id, { ...form, category: Number(form.category), age: Number(form.age) });
      onSaved();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="form-grid" onSubmit={submit}>
      {a.status === "approved" && (
        <p className="muted span-2">
          Bu e'lon kanalga allaqachon chiqqan — o'zgartirish kanaldagi postga ta'sir qilmaydi.
        </p>
      )}
      <label>
        Turi
        <select value={form.category} onChange={set("category")}>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.emoji} {c.name_uz}
            </option>
          ))}
        </select>
      </label>
      <label>
        Ism
        <input value={form.full_name} onChange={set("full_name")} required />
      </label>
      <label>
        Yosh
        <input type="number" min="14" max="80" value={form.age} onChange={set("age")} required />
      </label>
      <label>
        Yo'nalish
        <input value={form.direction} onChange={set("direction")} required />
      </label>
      <label className="span-2">
        Texnologiyalar
        <input value={form.technologies} onChange={set("technologies")} required />
      </label>
      <label>
        Telegram username
        <input value={form.telegram_username} onChange={set("telegram_username")} required />
      </label>
      <label>
        Telefon (+998XXXXXXXXX)
        <input value={form.phone_number} onChange={set("phone_number")} required />
      </label>
      <label>
        Qaysi shahardan
        <input value={form.city_from} onChange={set("city_from")} required />
      </label>
      <label>
        Qidirilayotgan shahar
        <input value={form.city_looking} onChange={set("city_looking")} required />
      </label>
      <label>
        Oylik
        <input type="number" min="0" step="any" value={form.salary_amount} onChange={set("salary_amount")} required />
      </label>
      <label>
        Valyuta
        <select value={form.salary_currency} onChange={set("salary_currency")}>
          <option value="UZS">so'm (UZS)</option>
          <option value="USD">USD</option>
        </select>
      </label>
      <label>
        Murojaat: dan
        <input type="time" value={form.contact_time_start} onChange={set("contact_time_start")} required />
      </label>
      <label>
        Murojaat: gacha
        <input type="time" value={form.contact_time_end} onChange={set("contact_time_end")} required />
      </label>
      <label className="span-2">
        Maqsad
        <textarea rows={3} value={form.purpose} onChange={set("purpose")} required />
      </label>

      <div className="modal-actions span-2">
        <button type="button" className="btn btn-ghost" onClick={onCancel}>
          Bekor qilish
        </button>
        <button className="btn btn-primary" disabled={busy}>
          {busy ? "Saqlanmoqda…" : "Saqlash"}
        </button>
      </div>
    </form>
  );
}
