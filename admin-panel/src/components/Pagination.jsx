export default function Pagination({ page, count, pageSize = 20, onChange }) {
  const pages = Math.max(1, Math.ceil(count / pageSize));
  if (pages <= 1) return null;

  return (
    <div className="pagination">
      <button className="btn btn-ghost" disabled={page <= 1} onClick={() => onChange(page - 1)}>
        Oldingi
      </button>
      <span>
        {page} / {pages} — jami {count} ta
      </span>
      <button className="btn btn-ghost" disabled={page >= pages} onClick={() => onChange(page + 1)}>
        Keyingi
      </button>
    </div>
  );
}
