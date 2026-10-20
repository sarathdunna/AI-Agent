import { useState } from "react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { EmptyState } from "@/components/Skeleton";

type Action = "drop_duplicates" | "fill_missing" | "drop_missing" | "drop_column" | "handle_outliers" | "encode_column";

interface Step {
  action: Action;
  columns?: string[];
  strategy?: string;
}

export default function DataCleaning() {
  const { currentDataset } = useDataset();
  const { push } = useToast();
  const [steps, setSteps] = useState<Step[]>([{ action: "drop_duplicates" }]);
  const [log, setLog] = useState<any[] | null>(null);
  const [running, setRunning] = useState(false);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;

  const addStep = () => setSteps([...steps, { action: "fill_missing", strategy: "mean" }]);
  const updateStep = (i: number, patch: Partial<Step>) => setSteps(steps.map((s, idx) => (idx === i ? { ...s, ...patch } : s)));
  const removeStep = (i: number) => setSteps(steps.filter((_, idx) => idx !== i));

  const run = async () => {
    setRunning(true);
    try {
      const result = await api.cleanDataset(currentDataset.id, steps);
      setLog(result.cleaning_log);
      push(`Cleaning applied — ${result.n_rows} rows, ${result.n_cols} cols remain`, "success");
    } catch (err: any) {
      push(err.message || "Cleaning failed", "error");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Data Cleaning</h1>
      <p className="text-sm text-slate-500">
        Cleaning operates on a working copy — the original uploaded file is never modified.
      </p>

      <div className="card space-y-4">
        {steps.map((step, i) => (
          <div key={i} className="flex flex-wrap items-center gap-2 border border-slate-200 rounded-lg p-3">
            <select className="input w-48" value={step.action} onChange={(e) => updateStep(i, { action: e.target.value as Action })}>
              <option value="drop_duplicates">Drop duplicates</option>
              <option value="fill_missing">Fill missing</option>
              <option value="drop_missing">Drop missing rows</option>
              <option value="drop_column">Drop column</option>
              <option value="handle_outliers">Handle outliers (IQR)</option>
              <option value="encode_column">Encode column</option>
            </select>
            {step.action !== "drop_duplicates" && (
              <input
                className="input w-56"
                placeholder="columns (comma separated, blank = all)"
                onChange={(e) => updateStep(i, { columns: e.target.value ? e.target.value.split(",").map((s) => s.trim()) : undefined })}
              />
            )}
            {(step.action === "fill_missing") && (
              <select className="input w-36" value={step.strategy} onChange={(e) => updateStep(i, { strategy: e.target.value })}>
                <option value="mean">mean</option>
                <option value="median">median</option>
                <option value="mode">mode</option>
              </select>
            )}
            {step.action === "handle_outliers" && (
              <select className="input w-36" value={step.strategy} onChange={(e) => updateStep(i, { strategy: e.target.value })}>
                <option value="iqr_clip">clip</option>
                <option value="iqr_remove">remove</option>
              </select>
            )}
            {step.action === "encode_column" && (
              <select className="input w-36" value={step.strategy} onChange={(e) => updateStep(i, { strategy: e.target.value })}>
                <option value="onehot">one-hot</option>
                <option value="label">label</option>
              </select>
            )}
            <button className="text-red-500 text-sm ml-auto" onClick={() => removeStep(i)}>Remove</button>
          </div>
        ))}
        <div className="flex gap-3">
          <button className="btn-secondary" onClick={addStep}>+ Add step</button>
          <button className="btn-primary" onClick={run} disabled={running}>{running ? "Running..." : "Apply Cleaning"}</button>
        </div>
      </div>

      {log && (
        <div className="card overflow-x-auto">
          <p className="font-semibold text-slate-800 mb-3">Cleaning Log</p>
          <pre className="text-xs bg-slate-50 rounded-lg p-3 overflow-x-auto">{JSON.stringify(log, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
