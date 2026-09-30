import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 120000,
});

export async function uploadPolicy(file) {
  const form = new FormData();
  form.append("file", file);

  const response = await api.post("/api/upload", form);
  return response.data;
}

export async function analyzePolicy(documentId) {
  const response = await api.post(`/api/analyze/${documentId}`);
  return response.data;
}

export async function askPolicy(documentId, question) {
  const response = await api.post(`/api/ask/${documentId}`, { question });
  return response.data;
}

export async function getDocument(documentId) {
  const response = await api.get(`/api/documents/${documentId}`);
  return response.data;
}
