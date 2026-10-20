const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}/api${path}`, {
    ...options,
    headers: options.body instanceof FormData ? options.headers : { "Content-Type": "application/json", ...options.headers },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res as unknown as T;
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  uploadDataset: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<any>("/datasets/upload", { method: "POST", body: form });
  },
  listDatasets: () => request<any[]>("/datasets"),
  getDataset: (id: string) => request<any>(`/datasets/${id}`),
  previewDataset: (id: string, limit = 50) => request<any>(`/datasets/${id}/preview?limit=${limit}`),
  profileDataset: (id: string) => request<any>(`/datasets/${id}/profile`),
  cleanDataset: (id: string, steps: any[]) => request<any>(`/datasets/${id}/clean`, { method: "POST", body: JSON.stringify(steps) }),
  edaDataset: (id: string) => request<any>(`/datasets/${id}/eda`),
  visualize: (id: string, req: any) => request<any>(`/datasets/${id}/visualize`, { method: "POST", body: JSON.stringify(req) }),
  ask: (id: string, question: string) => request<any>(`/datasets/${id}/ask`, { method: "POST", body: JSON.stringify({ question }) }),
  sql: (id: string, body: { sql?: string; question?: string }) => request<any>(`/datasets/${id}/sql`, { method: "POST", body: JSON.stringify(body) }),
  insights: (id: string) => request<any>(`/datasets/${id}/insights`),
  dashboard: (id: string) => request<any>(`/datasets/${id}/dashboard`),

  problemType: (datasetId: string, target?: string) => request<any>(`/ml/problem-type?dataset_id=${datasetId}${target ? `&target=${target}` : ""}`),
  algorithms: (problemType: string) => request<any>(`/ml/algorithms?problem_type=${problemType}`),
  train: (body: any) => request<any>("/ml/train", { method: "POST", body: JSON.stringify(body) }),
  listModels: (datasetId?: string) => request<any[]>(`/ml/models${datasetId ? `?dataset_id=${datasetId}` : ""}`),
  getModel: (id: string) => request<any>(`/ml/models/${id}`),
  predict: (id: string, input: Record<string, any>) => request<any>(`/ml/models/${id}/predict`, { method: "POST", body: JSON.stringify({ input }) }),
  predictBatch: (id: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<any>(`/ml/models/${id}/predict-batch`, { method: "POST", body: form });
  },
  importance: (id: string) => request<any>(`/ml/models/${id}/importance`),

  knowledgeAsk: (question: string) => request<any>("/knowledge/ask", { method: "POST", body: JSON.stringify({ question }) }),

  reportUrl: (datasetId: string, modelId?: string) => `${API_URL}/api/reports/generate`,
  generateReport: async (datasetId: string, modelId?: string) => {
    const res = await fetch(`${API_URL}/api/reports/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ dataset_id: datasetId, model_id: modelId }),
    });
    if (!res.ok) throw new ApiError(res.status, "Report generation failed");
    return res.blob();
  },
};

export { ApiError, API_URL };
