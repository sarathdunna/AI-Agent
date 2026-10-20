import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { ChartResult } from "@/types";
import { ChartRenderer } from "@/charts/ChartRenderer";
import { EmptyState } from "@/components/Skeleton";

const CHART_TYPES = ["bar", "line", "scatter", "histogram", "box", "heatmap", "pie", "count"];

export default function Visualizations() {
  const { currentDataset } = useDataset();
  const { push } = useToast();
  const [columns, setColumns] = useState<string[]>([]);
  const [chartType, setChartType] = useState("bar");
  const [x, setX] = useState("");
  const [y, setY] = useState("");
  const [result, setResult] = useState<ChartResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!currentDataset) return;
    setColumns(currentDataset.columns);
    setX(currentDataset.columns[0] || "");
    setY(currentDataset.columns[1] || "");
  }, [currentDataset?.id]);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;

  const generate = async () => {
    setLoading(true);
    try {
      const res = await api.visualize(currentDataset.id, { chart_type: chartType, x: x || null, y: y || null });
      setResult(res);
    } catch (err: any) {
      push(err.message || "Chart generation failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Visualizations</h1>

      <div className="card flex flex-wrap gap-3 items-end">
        <div>
          <label className="text-xs text-slate-500">Chart type</label>
          <select className="input w-40" value={chartType} onChange={(e) => setChartType(e.target.value)}>
            {CHART_TYPES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-500">X / column</label>
          <select className="input w-48" value={x} onChange={(e) => setX(e.target.value)}>
            {columns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        {["line", "scatter"].includes(chartType) && (
          <div>
            <label className="text-xs text-slate-500">Y</label>
            <select className="input w-48" value={y} onChange={(e) => setY(e.target.value)}>
              {columns.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        )}
        <button className="btn-primary" onClick={generate} disabled={loading}>{loading ? "Generating..." : "Generate Chart"}</button>
      </div>

      {result && (
        <div className="card">
          <ChartRenderer chartType={result.chart_type} data={result.data} />
          <p className="text-sm text-slate-600 mt-4 border-t border-slate-100 pt-3">{result.interpretation}</p>
        </div>
      )}
    </div>
  );
}
