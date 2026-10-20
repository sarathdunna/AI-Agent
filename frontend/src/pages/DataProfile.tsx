import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { DatasetProfile } from "@/types";
import { CardSkeleton, EmptyState } from "@/components/Skeleton";

export default function DataProfile() {
  const { currentDataset } = useDataset();
  const [profile, setProfile] = useState<DatasetProfile | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!currentDataset) return;
    setLoading(true);
    api.profileDataset(currentDataset.id).then(setProfile).finally(() => setLoading(false));
  }, [currentDataset?.id]);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;
  if (loading || !profile) return <CardSkeleton />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Data Profile</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          ["Rows", profile.n_rows], ["Columns", profile.n_cols],
          ["Duplicate rows", `${profile.duplicate_rows} (${profile.duplicate_pct}%)`],
          ["Total missing cells", profile.total_missing_cells],
        ].map(([label, value]) => (
          <div key={label as string} className="card">
            <p className="text-xs text-slate-500">{label}</p>
            <p className="text-2xl font-bold text-slate-800 mt-1">{String(value)}</p>
          </div>
        ))}
      </div>

      {profile.class_imbalance.length > 0 && (
        <div className="card border-amber-300 bg-amber-50">
          <p className="font-semibold text-amber-800 mb-2">Class Imbalance Detected</p>
          {profile.class_imbalance.map((c) => (
            <p key={c.column} className="text-sm text-amber-700">
              '{c.column}': majority class is {c.majority_pct}% of rows (imbalance ratio {c.imbalance_ratio}x)
            </p>
          ))}
        </div>
      )}

      <div className="card">
        <p className="font-semibold text-slate-800 mb-2">Suggested target columns</p>
        <div className="flex gap-2 flex-wrap">
          {profile.target_candidates.map((t) => (
            <span key={t} className="bg-brand-50 text-brand-700 text-sm px-3 py-1 rounded-full">{t}</span>
          ))}
        </div>
      </div>

      <div className="card overflow-x-auto">
        <p className="font-semibold text-slate-800 mb-3">Columns</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b border-slate-200">
              <th className="py-2 pr-4">Name</th>
              <th className="py-2 pr-4">Type</th>
              <th className="py-2 pr-4">Missing</th>
              <th className="py-2 pr-4">Unique</th>
              <th className="py-2 pr-4">High cardinality</th>
              <th className="py-2 pr-4">Mean / Top value</th>
            </tr>
          </thead>
          <tbody>
            {profile.columns.map((c) => (
              <tr key={c.name} className="border-b border-slate-100">
                <td className="py-2 pr-4 font-medium">{c.name}</td>
                <td className="py-2 pr-4">{c.inferred_type}</td>
                <td className="py-2 pr-4">{c.missing_count} ({c.missing_pct}%)</td>
                <td className="py-2 pr-4">{c.unique_count}</td>
                <td className="py-2 pr-4">{c.high_cardinality ? "Yes" : "No"}</td>
                <td className="py-2 pr-4">
                  {c.inferred_type === "numeric" ? c.mean?.toFixed(2) : (c.top_values && Object.keys(c.top_values)[0])}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
