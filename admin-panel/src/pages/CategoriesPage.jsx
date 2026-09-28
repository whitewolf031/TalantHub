import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import Modal from "../components/Modal.jsx";
import { useToast } from "../components/Toast.jsx";

const EMPTY = { key: "", emoji: "📢", name_uz: "", name_en: "", name_ru: "", order: 0, is_active: true };

export default function CategoriesPage() {
  const toast = useToast();
  const [items, setItems] = useState(null);
  const [editing, setEditing] = useState(null); // null | {..form, id?}

  const load = useCallback(async () => {
    try {
      setItems(await api.categories());
    } catch (err) {
      toast(err.message, "error");
    }
  }, [toast]);

  useEffect(() => {
    load();
  }, [load]);

  const toggleActive = async (c) => {
    try {
      await api.updateCategory(c.id, { is_active: !c.is_active });
      load();
    } catch (err) {
      toast(err.message, "error");
    }
  };

  const remove = async (c) => {
    if (!window.confirm(`«${c.name_uz}» turini o'chirasizmi?`)) return;
    try {
      await api.deleteCategory(c.id);
      toast("O'chirildi");
      load();
    } catch (err) {
      toast(err.message, "error");
    }
  };

  return (
    <>
      <div className="page-head">
        <h1>E'lon turlari</h1>
        <button className="btn btn-primary" onClick={() => setEditing({ ...EMPTY, order: (items?.length || 0) + 1 })}>
          Yangi tur qo'shish
        </button>
      </div>
      <p className="muted">
        Bu yerda qo'shilgan yoki faollashtirilgan turlar botda avtomatik tugma sifatida chiqadi — kodni o'zgartirish shart emas.
      </p>

      {!items ? (
        <p className="muted">Yuklanmoqda…</p>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Tartib</th>
                <th>Nomi</th>
                <th>English</th>
                <th>Русский</th>
                <th>Kalit</th>
                <th>E'lonlar</th>
                <th>Faol</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.id} className={c.is_active ? "" : "row-muted"}>
                  <td>{c.order}</td>
                  <td>
                    {c.emoji} <strong>{c.name_uz}</strong>
                  </td>
                  <td>{c.name_en}</td>
                  <td>{c.name_ru}</td>
                  <td>
                    <code>{c.key}</code>
                  </td>
                  <td>{c.announcements_count}</td>
                  <td>
                    <button
                      className={c.is_active ? "switch on" : "switch"}
                      onClick={() => toggleActive(c)}
                      aria-label={c.is_active ? "Faolsizlantirish" : "Faollashtirish"}
                      aria-pressed={c.is_active}
                    />
                  </td>
                  <td className="actions">
                    <button className="btn btn-ghost" onClick={() => setEditing(c)}>
                      Tahrirlash
                    </button>
                    <button className="btn btn-danger-outline" onClick={() => remove(c)}>
                      O'chirish
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <CategoryForm
          initial={editing}
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

function CategoryForm({ initial, onClose, onSaved }) {
  const toast = useToast();
  const isNew = !initial.id;
  const [form, setForm] = useState(initial);
  const [busy, setBusy] = useState(false);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    const payload = {
      key: form.key,
      emoji: form.emoji,
      name_uz: form.name_uz,
      name_en: form.name_en,
      name_ru: form.name_ru,
      order: Number(form.order),
      is_active: form.is_active,
    };
    try {
      if (isNew) await api.createCategory(payload);
      else await api.updateCategory(initial.id, payload);
      onSaved();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={isNew ? "Yangi e'lon turi" : "E'lon turini tahrirlash"} onClose={onClose}>
      <form className="form-grid" onSubmit={submit}>
        <label>
          Emoji
          <input value={form.emoji} onChange={set("emoji")} maxLength={8} required />
        </label>
        <label>
          Tartib raqami
          <input type="number" min="0" value={form.order} onChange={set("order")} required />
        </label>
        <label className="span-2">
          Ichki kalit (lotin harflari, tire yoki pastki chiziq)
          <input value={form.key} onChange={set("key")} placeholder="masalan: startup_partner" required />
        </label>
        <label className="span-2">
          Nomi (O'zbekcha)
          <input value={form.name_uz} onChange={set("name_uz")} required />
        </label>
        <label className="span-2">
          Nomi (English)
          <input value={form.name_en} onChange={set("name_en")} required />
        </label>
        <label className="span-2">
          Nomi (Русский)
          <input value={form.name_ru} onChange={set("name_ru")} required />
        </label>
        <label className="check span-2">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />
          Botda ko'rsatilsin
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
