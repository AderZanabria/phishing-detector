import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

function ok(data) {
  return { success: true, data, error: null };
}

function fail(error) {
  const detail = error?.response?.data?.detail;
  const message =
    (typeof detail === "string" && detail) ||
    detail?.message ||
    error?.message ||
    "No se pudo contactar la API.";
  return { success: false, data: null, error: message };
}

export async function checkHealth() {
  try {
    const { data } = await client.get("/health");
    return ok(data);
  } catch (error) {
    return fail(error);
  }
}

export async function predictUrl(url) {
  try {
    const { data } = await client.post("/api/v1/predict", { url });
    return ok(data);
  } catch (error) {
    return fail(error);
  }
}

export async function predictBatch(urls) {
  try {
    const { data } = await client.post("/api/v1/predict/batch", { urls });
    // El backend actual devuelve { results, errors }. También se acepta una lista.
    const results = Array.isArray(data) ? data : data?.results || [];
    const errors = Array.isArray(data) ? [] : data?.errors || [];
    return ok({ results, errors });
  } catch (error) {
    return fail(error);
  }
}
