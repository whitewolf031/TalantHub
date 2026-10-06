const LABELS = {
  pending: "Kutilmoqda",
  waiting_payment: "To'lov kutilmoqda",
  payment_pending: "To'lov tekshirilmoqda",
  approved: "Tasdiqlangan",
  rejected: "Rad etilgan",
};

export default function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{LABELS[status] || status}</span>;
}
