import { useState } from "react";
import { useAuth } from "../auth.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(username, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="login-wrap">
      <form className="login" onSubmit={submit}>
        <h1>TalantHub</h1>
        <p className="muted">Moderatsiya paneliga kirish. Django admin'dagi login va parol ishlatiladi.</p>

        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required />
        </label>
        <label>
          Parol
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>

        {error && <div className="error">{error}</div>}

        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? "Tekshirilmoqda…" : "Kirish"}
        </button>
      </form>
    </div>
  );
}
