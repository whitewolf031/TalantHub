import { Link, useOutletContext } from "react-router-dom";

export default function DashboardPage() {
  const { stats } = useOutletContext();

  if (!stats) return <p className="muted">Yuklanmoqda…</p>;

  return (
    <>
      <h1>Bosh sahifa</h1>

      <section className={`queue ${stats.pending > 0 ? "queue-active" : ""}`}>
        {stats.pending > 0 ? (
          <>
            <div>
              <strong>{stats.pending} ta e'lon</strong> tasdiqlashni kutmoqda
              <p className="muted">Eng eskisidan boshlab ko'rib chiqing.</p>
            </div>
            <Link className="btn btn-primary" to="/announcements">
              Ko'rib chiqish
            </Link>
          </>
        ) : (
          <div>
            <strong>Kutilayotgan e'lon yo'q</strong>
            <p className="muted">Yangi e'lon kelsa, shu yerda va chap menyuda ko'rinadi.</p>
          </div>
        )}
      </section>

      <table className="table summary">
        <tbody>
          <tr><th>Bugun kelgan e'lonlar</th><td>{stats.new_today}</td></tr>
          <tr><th>Tasdiqlangan e'lonlar</th><td>{stats.approved}</td></tr>
          <tr><th>Rad etilgan e'lonlar</th><td>{stats.rejected}</td></tr>
          <tr><th>Foydalanuvchilar</th><td>{stats.users}</td></tr>
          <tr><th>E'lon turlari</th><td>{stats.categories}</td></tr>
        </tbody>
      </table>
    </>
  );
}
