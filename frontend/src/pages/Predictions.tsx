import { useEffect, useRef, useState } from "react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { ModelSummary } from "@/types";
import { EmptyState } from "@/components/Skeleton";

export default function Predictions() {
  const { currentDataset } = useDataset();
  const { push } = useToast();
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [modelId, setModelId] = useState("");
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [batchResult, setBatchResult] = useState<any>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!currentDataset) return;
    api.listModels(currentDataset.id).then(setModels);
  }, [currentDataset?.id]);

  const model = models.find((m) => m.id === modelId);

  useEffect(() => {
    if (model) setInputs(Object.fromEntries(model.feature_columns.map((c) => [c, ""])));
  }, [modelId]);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;
  if (models.length === 0) return <EmptyState title="No trained models" description="Train a model in ML Studio first." />;

  const predict = async () => {
    try {
      const res = await api.predict(modelId, inputs);
      setResult(res);
    } catch (err: any) {
      push(err.message || "Prediction failed", "error");
    }
  };

  const predictBatch = async (file: File) => {
    try {
      const res = await api.predictBatch(modelId, file);
      setBatchResult(res);
    } catch (err: any) {
      push(err.message || "Batch prediction failed", "error");
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Predictions</h1>

      <div className="card space-y-3">
        <label className="text-sm font-medium">Select model</label>
        <select className="input w-72" value={modelId} onChange={(e) => setModelId(e.target.value)}>
          <option value="">— select —</option>
          {models.map((m) => <option key={m.id} value={m.id}>{m.algorithm} ({m.target || "clustering"})</option>)}
        </select>
      </div>

      {model && (
        <div className="card space-y-3">
          <p className="font-medium text-sm">Single-row prediction</p>
          <div className="grid md:grid-cols-3 gap-3">
            {model.feature_columns.map((c) => (
              <div key={c}>
                <label className="text-xs text-slate-500">{c}</label>
                <input className="input" value={inputs[c] || ""} onChange={(e) => setInputs({ ...inputs, [c]: e.target.value })} />
              </div>
            ))}
          </div>
          <button className="btn-primary" onClick={predict}>Predict</button>
          {result && (
            <div className="bg-brand-50 rounded-lg p-3 text-sm">
              <p className="font-semibold">Prediction: {String(result.prediction)}</p>
              {result.probabilities && <pre className="text-xs mt-1">{JSON.stringify(result.probabilities, null, 2)}</pre>}
            </div>
          )}
        </div>
      )}

      {model && (
        <div className="card space-y-3">
          <p className="font-medium text-sm">Batch prediction (CSV)</p>
          <input ref={fileInput} type="file" accept=".csv" onChange={(e) => e.target.files && predictBatch(e.target.files[0])} />
          {batchResult && (
            <div className="overflow-x-auto mt-3">
              <table className="text-sm w-full">
                <thead><tr>{batchResult.columns.map((c: string) => <th key={c} className="text-left pr-4 text-slate-500">{c}</th>)}</tr></thead>
                <tbody>
                  {batchResult.rows.slice(0, 20).map((r: any, i: number) => (
                    <tr key={i}>{batchResult.columns.map((c: string) => <td key={c} className="pr-4">{String(r[c])}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
