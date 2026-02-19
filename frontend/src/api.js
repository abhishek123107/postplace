import axios from "axios";

export const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

export async function getAuthStatus(userId) {
  const res = await axios.get(`${API_BASE}/auth/status`, {
    params: { user_id: userId },
  });
  return res.data;
}

export async function getRecentBlogPosts(userId, limit = 20) {
  const res = await axios.get(`${API_BASE}/automation/blog/recent`, {
    params: { user_id: userId, limit },
  });
  return res.data;
}

export async function getScheduledAutomationPosts(userId, limit = 50) {
  const res = await axios.get(`${API_BASE}/automation/scheduled`, {
    params: { user_id: userId, limit },
  });
  return res.data;
}

export async function getAuthorizeUrl(platform, userId) {
  const res = await axios.get(`${API_BASE}/auth/connect`, {
    params: { platform, user_id: userId },
  });
  return res.data.authorize_url;
}

export async function sendPost({ userId, content, platforms, imageFile }) {
  const form = new FormData();
  form.append("user_id", userId);
  form.append("content", content);
  form.append("platforms", JSON.stringify(platforms));
  if (imageFile) form.append("image", imageFile);

  const res = await axios.post(`${API_BASE}/post/send`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
