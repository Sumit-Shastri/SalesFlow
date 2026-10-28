// Vite proxies /api during local development. Set VITE_API_BASE_URL only when
// the frontend is intentionally served from a different origin.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function responseError(response) {
  try {
    const body = await response.json();
    return typeof body.detail === "string" ? body.detail : "The server could not complete this request.";
  } catch {
    return "The server returned an unexpected response.";
  }
}

export async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    throw new Error(await responseError(response));
  }
  return response.json();
}

export async function requestPdf(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(await responseError(response));
  }
  return response.blob();
}
