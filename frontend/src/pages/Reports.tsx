import { useEffect, useState } from "react";
import { FileDown } from "lucide-react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { ModelSummary } from "@/types";
import { EmptyState } from "@/components/Skeleton";

export default function Reports() {
  const { currentDataset } = useDataset();
  const { push } = useToast();
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [modelId, setModelId] = useState("");
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!currentDataset) return;
    api.listModels(currentDataset.id).then(setModels);
  }, [currentDataset?.id]);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;

  const download = async () => {
    setGenerating(true);
    try {
      const blob = await api.generateReport(currentDataset.id, modelId || undefined);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${currentDataset.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      push("Report downloaded", "success");
    } catch (err: any) {
      push(err.message || "Report generation failed", "error");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Reports</h1>
      <div className="card space-y-3">
        <p className="text-sm text-slate-600">Generates a PDF covering dataset profile, EDA insights and (optionally) model performance.</p>
        <label className="text-sm font-medium">Include model (optional)</label>
        <select className="input w-72" value={modelId} onChange={(e) => setModelId(e.target.value)}>
          <option value="">— none —</option>
          {models.map((m) => <option key={m.id} value={m.id}>{m.algorithm} ({m.target || "clustering"})</option>)}
        </select>
        <button className="btn-primary" onClick={download} disabled={generating}>
          <FileDown size={16} /> {generating ? "Generating..." : "Generate & Download PDF"}
        </button>
      </div>
    </div>
  );
}
