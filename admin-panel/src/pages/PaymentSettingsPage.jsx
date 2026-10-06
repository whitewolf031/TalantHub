import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useToast } from "../components/Toast.jsx";

export default function PaymentSettingsPage() {
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    card_number: "",
    card_owner: "",
    amount: 10000,
    instruction_uz: "",
    instruction_en: "",
    instruction_ru: "",
    is_active: true,
  });

  useEffect(() => {
    api
      .paymentSettings()
      .then((data) => {
        if (data) {
          setForm({
            card_number: data.card_number || "",
            card_owner: data.card_owner || "",
            amount: data.amount || 10000,
            instruction_uz: data.instruction_uz || "",
            instruction_en: data.instruction_en || "",
            instruction_ru: data.instruction_ru || "",
            is_active: data.is_active ?? true,
          });
        }
      })
      .catch((err) => toast(err.message, "error"))
      .finally(() => setLoading(false));
  }, [toast]);

  const handleChange = (field) => (e) => {
    const value = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.updatePaymentSettings({
        ...form,
        amount: Number(form.amount),
      });
      toast("To'lov sozlamalari muvaffaqiyatli saqlandi!");
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="muted">Yuklanmoqda…</p>;

  return (
    <div style={{ maxWidth: "700px" }}>
      <h1>To'lov sozlamalari</h1>
      <p className="muted" style={{ marginBottom: "24px" }}>
        Telegram botda pullik (premium) e'lon berayotgan foydalanuvchilarga ko'rsatiladigan plastik karta va ko'rsatmalar.
      </p>

      <form onSubmit={handleSubmit} className="form-card" style={{ background: "#ffffff", padding: "24px", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>Plastik karta raqami:</label>
          <input
            type="text"
            required
            value={form.card_number}
            onChange={handleChange("card_number")}
            placeholder="8600 0000 0000 0000"
            style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
        </div>

        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>Karta egasining ismi-sharifi:</label>
          <input
            type="text"
            required
            value={form.card_owner}
            onChange={handleChange("card_owner")}
            placeholder="Falonavchi Pistonchi"
            style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
        </div>

        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>Pullik e'lon narxi (so'm):</label>
          <input
            type="number"
            required
            min="1000"
            step="1000"
            value={form.amount}
            onChange={handleChange("amount")}
            placeholder="10000"
            style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
        </div>

        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>Ko'rsatma matni (O'zbekcha):</label>
          <textarea
            rows={3}
            value={form.instruction_uz}
            onChange={handleChange("instruction_uz")}
            placeholder="To'lovni ushbu plastik kartaga o'tkazib, chek skrinshotini yuboring:"
            style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
        </div>

        <div style={{ marginBottom: "16px" }}>
          <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>Ko'rsatma matni (English):</label>
          <textarea
            rows={3}
            value={form.instruction_en}
            onChange={handleChange("instruction_en")}
            placeholder="Transfer the payment to this card and send the receipt screenshot:"
            style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>Ko'rsatma matni (Русский):</label>
          <textarea
            rows={3}
            value={form.instruction_ru}
            onChange={handleChange("instruction_ru")}
            placeholder="Переведите оплату на эту карту и отправьте скриншот чека:"
            style={{ width: "100%", padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          />
        </div>

        <div style={{ marginBottom: "24px", display: "flex", alignItems: "center", gap: "8px" }}>
          <input
            type="checkbox"
            id="is_active"
            checked={form.is_active}
            onChange={handleChange("is_active")}
            style={{ width: "18px", height: "18px" }}
          />
          <label htmlFor="is_active" style={{ cursor: "pointer", fontWeight: "500" }}>
            To'lov qabul qilish faol
          </label>
        </div>

        <button type="submit" className="btn btn-ok" disabled={saving}>
          {saving ? "Saqlanmoqda…" : "Saqlash"}
        </button>
      </form>
    </div>
  );
}
