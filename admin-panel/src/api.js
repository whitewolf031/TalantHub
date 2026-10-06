// Backend bilan muloqot. Barcha so'rovlar /api/admin/* ga ketadi va
// Authorization: Token <token> header bilan yuboriladi.

const BASE = import.meta.env.VITE_API_URL || "/api/admin";
const TOKEN_KEY = "talanthub_admin_token";

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

// DRF xatolarini odam o'qiy oladigan matnga aylantiradi
function extractMessage(data, status) {
  if (!data || typeof data !== "object") return `Xatolik (${status})`;
  if (typeof data.detail === "string") return data.detail;
  const parts = Object.entries(data).map(([field, msgs]) => {
    const text = Array.isArray(msgs) ? msgs.join(" ") : String(msgs);
    return `${field}: ${text}`;
  });
  return parts.join(" | ") || `Xatolik (${status})`;
}

async function request(path, { method = "GET", body, params } = {}) {
  const query = new URLSearchParams();
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") query.set(key, value);
  });
  const qs = query.toString();

  const headers = { "Content-Type": "application/json" };
  const token = tokenStore.get();
  if (token) headers.Authorization = `Token ${token}`;

  let response;
  try {
    response = await fetch(`${BASE}${path}${qs ? `?${qs}` : ""}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Serverga ulanib bo'lmadi. Backend ishlayotganini tekshiring.", 0);
  }

  if (response.status === 204) return null;

  let data = null;
  try {
    data = await response.json();
  } catch {
    /* JSON bo'lmagan javob */
  }

  if (!response.ok) {
    if (response.status === 401 && token) {
      tokenStore.clear();
      window.dispatchEvent(new Event("auth:logout"));
    }
    throw new ApiError(extractMessage(data, response.status), response.status, data);
  }
  return data;
}

export const api = {
  login: (username, password) => request("/auth/login/", { method: "POST", body: { username, password } }),
  me: () => request("/auth/me/"),
  logout: () => request("/auth/logout/", { method: "POST" }),
  stats: () => request("/stats/"),

  announcements: (params) => request("/announcements/", { params }),
  updateAnnouncement: (id, body) => request(`/announcements/${id}/`, { method: "PATCH", body }),
  deleteAnnouncement: (id) => request(`/announcements/${id}/`, { method: "DELETE" }),
  approveAnnouncement: (id) => request(`/announcements/${id}/approve/`, { method: "POST", body: {} }),
  rejectAnnouncement: (id, reason) =>
    request(`/announcements/${id}/reject/`, { method: "POST", body: { reason } }),
  approvePayment: (id) => request(`/announcements/${id}/approve-payment/`, { method: "POST", body: {} }),
  rejectPayment: (id, reason) =>
    request(`/announcements/${id}/reject-payment/`, { method: "POST", body: { reason } }),
  deleteResume: (id) => request(`/announcements/${id}/delete-resume/`, { method: "POST", body: {} }),

  paymentSettings: () => request("/payment-settings/"),
  updatePaymentSettings: (body) => request("/payment-settings/", { method: "PATCH", body }),


  categories: () => request("/categories/"),
  createCategory: (body) => request("/categories/", { method: "POST", body }),
  updateCategory: (id, body) => request(`/categories/${id}/`, { method: "PATCH", body }),
  deleteCategory: (id) => request(`/categories/${id}/`, { method: "DELETE" }),

  users: (params) => request("/users/", { params }),
  updateUser: (id, body) => request(`/users/${id}/`, { method: "PATCH", body }),
  toggleBlock: (id) => request(`/users/${id}/toggle-block/`, { method: "POST", body: {} }),
  deleteUser: (id) => request(`/users/${id}/`, { method: "DELETE" }),
};
