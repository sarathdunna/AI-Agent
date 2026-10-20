import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud, Sparkles, ArrowRight } from "lucide-react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { DashboardKPIs } from "@/types";
import { CardSkeleton, EmptyState } from "@/components/Skeleton";

export default function Dashboard() {
  const { currentDataset, refreshDatasets, setCurrentDatasetId } = useDataset();
  const { push } = useToast();
  const navigate = useNavigate();
  const fileInput = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!currentDataset) {
      setKpis(null);
      return;
    }
    setLoading(true);
    api.dashboard(currentDataset.id).then(setKpis).catch(() => setKpis(null)).finally(() => setLoading(false));
  }, [currentDataset?.id]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const result = await api.uploadDataset(file);
      await refreshDatasets();
      setCurrentDatasetId(result.id);
      push(`Uploaded '${result.original_filename}' — ${result.n_rows} rows x ${result.n_cols} cols`, "success");
      navigate("/profile");
    } catch (err: any) {
      push(err.message || "Upload failed", "error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="card bg-gradient-to-br from-brand-600 to-brand-800 text-white border-0 py-10 px-8">
        <p className="uppercase tracking-wide text-brand-200 text-xs font-semibold mb-2">Data Analyst + ML Agent</p>
        <h1 className="text-3xl md:text-4xl font-bold max-w-2xl leading-tight">
          Turn Raw Data into Insights and Machine Learning Models with AI
        </h1>
        <p className="mt-3 text-brand-100 max-w-xl">
          Upload a dataset, explore it, clean it, ask questions in plain English, and train
          production-grade ML models — all in one guided workflow.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <input ref={fileInput} type="file" accept=".csv,.xlsx,.xls" hidden onChange={(e) => e.target.files && handleUpload(e.target.files[0])} />
          <button className="btn-primary bg-white text-brand-700 hover:bg-brand-50" onClick={() => fileInput.current?.click()} disabled={uploading}>
            <UploadCloud size={18} /> {uploading ? "Uploading..." : "Upload Dataset"}
          </button>
          <button
            className="btn-secondary bg-transparent border-white text-white hover:bg-white/10"
            disabled={loadingSample || uploading}
            onClick={async () => {
              setLoadingSample(true);
              try {
                const res = await fetch("/samples/customer_churn_sample.csv");
                if (!res.ok) throw new Error("Could not load sample dataset");
                const blob = await res.blob();
                const file = new File([blob], "customer_churn_sample.csv", { type: "text/csv" });
                await handleUpload(file);
              } catch (err: any) {
                push(err.message || "Failed to load sample dataset", "error");
              } finally {
                setLoadingSample(false);
              }
            }}
          >
            <Sparkles size={18} /> {loadingSample ? "Loading..." : "Try Sample Dataset"}
          </button>
        </div>
      </section>

      <section className="card">
        <h2 className="font-semibold text-slate-800 mb-4">Workflow</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {[
            ["1. Upload", "CSV / XLSX dataset"],
            ["2. Profile & Clean", "Understand & fix data"],
            ["3. Explore & Ask", "EDA, charts, NL queries"],
            ["4. Train & Explain", "ML Studio + predictions"],
          ].map(([title, desc]) => (
            <div key={title} className="rounded-lg border border-slate-200 p-4">
              <p className="font-semibold text-brand-700">{title}</p>
              <p className="text-slate-500 mt-1">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {!currentDataset && (
        <EmptyState title="No dataset selected" description="Upload a dataset above or pick one from the top bar to see live KPIs here." />
      )}

      {currentDataset && loading && <CardSkeleton />}

      {currentDataset && kpis && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            ["Rows", kpis.rows], ["Columns", kpis.columns], ["Missing cells", kpis.missing_cells],
            ["Duplicate rows", kpis.duplicate_rows], ["Numeric cols", kpis.numeric_columns],
            ["Categorical cols", kpis.categorical_columns], ["Cleaned", kpis.is_cleaned ? "Yes" : "No"],
            ["Models trained", kpis.models_trained],
          ].map(([label, value]) => (
            <div key={label as string} className="card">
              <p className="text-xs text-slate-500">{label}</p>
              <p className="text-2xl font-bold text-slate-800 mt-1">{String(value)}</p>
            </div>
          ))}
          {kpis.best_model && (
            <div className="card col-span-2 md:col-span-4">
              <p className="text-xs text-slate-500">Best model</p>
              <p className="font-semibold text-slate-800 mt-1">
                {kpis.best_model.algorithm} on target "{kpis.best_model.target}"
              </p>
              <div className="flex gap-4 mt-2 text-sm text-slate-600 flex-wrap">
                {Object.entries(kpis.best_model.metrics)
                  .filter(([k]) => !["explanations", "confusion_matrix"].includes(k))
                  .map(([k, v]) => (
                    <span key={k} className="bg-slate-100 rounded px-2 py-1">{k}: {String(v)}</span>
                  ))}
              </div>
              <button className="btn-secondary mt-4" onClick={() => navigate("/ml-studio")}>
                Open ML Studio <ArrowRight size={16} />
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
