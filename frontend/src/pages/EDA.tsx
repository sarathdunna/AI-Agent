import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { EDAResult } from "@/types";
import { CardSkeleton, EmptyState } from "@/components/Skeleton";

export default function EDA() {
  const { currentDataset } = useDataset();
  const [eda, setEda] = useState<EDAResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!currentDataset) return;
    setLoading(true);
    api.edaDataset(currentDataset.id).then(setEda).finally(() => setLoading(false));
  }, [currentDataset?.id]);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;
  if (loading || !eda) return <CardSkeleton />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Exploratory Data Analysis</h1>

      <div className="card">
        <p className="font-semibold text-slate-800 mb-2">Insights</p>
        <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
          {eda.insights.map((i, idx) => <li key={idx}>{i}</li>)}
        </ul>
      </div>

      <div className="card overflow-x-auto">
        <p className="font-semibold text-slate-800 mb-3">Descriptive Statistics</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-200">
              <th className="py-2 pr-4">Column</th><th className="py-2 pr-4">Mean</th><th className="py-2 pr-4">Median</th>
              <th className="py-2 pr-4">Std</th><th className="py-2 pr-4">Min</th><th className="py-2 pr-4">Max</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(eda.descriptive_stats).map(([col, s]) => (
              <tr key={col} className="border-b border-slate-100">
                <td className="py-2 pr-4 font-medium">{col}</td>
                <td className="py-2 pr-4">{s.mean}</td><td className="py-2 pr-4">{s.median}</td>
                <td className="py-2 pr-4">{s.std}</td><td className="py-2 pr-4">{s.min}</td><td className="py-2 pr-4">{s.max}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {eda.strong_correlations.length > 0 && (
        <div className="card">
          <p className="font-semibold text-slate-800 mb-3">Strong Correlations</p>
          <ul className="text-sm text-slate-700 space-y-1">
            {eda.strong_correlations.map((c, idx) => (
              <li key={idx}>{c.col1} ↔ {c.col2}: <span className="font-mono">{c.correlation}</span></li>
            ))}
          </ul>
        </div>
      )}

      {Object.keys(eda.outliers).length > 0 && (
        <div className="card">
          <p className="font-semibold text-slate-800 mb-3">Outliers (IQR method)</p>
          <ul className="text-sm text-slate-700 space-y-1">
            {Object.entries(eda.outliers).map(([col, o]) => (
              <li key={col}>{col}: {o.count} outliers ({o.pct}%)</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
