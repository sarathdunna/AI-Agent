import { useState } from "react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { EmptyState } from "@/components/Skeleton";

export default function SQLAgent() {
  const { currentDataset } = useDataset();
  const { push } = useToast();
  const [question, setQuestion] = useState("");
  const [sql, setSql] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;

  const generate = async () => {
    setLoading(true);
    try {
      const res = await api.sql(currentDataset.id, { question });
      setSql(res.sql);
      setResult(res);
    } catch (err: any) {
      push(err.message || "SQL generation failed", "error");
    } finally {
      setLoading(false);
    }
  };

  const runSql = async () => {
    setLoading(true);
    try {
      const res = await api.sql(currentDataset.id, { sql });
      setResult(res);
    } catch (err: any) {
      push(err.message || "SQL execution rejected", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">SQL Agent</h1>
      <p className="text-sm text-slate-500">Read-only SELECT/WITH queries only — DROP/DELETE/UPDATE/INSERT/ALTER etc. are always rejected.</p>

      <div className="card space-y-3">
        <label className="text-xs text-slate-500">Natural language question</label>
        <div className="flex gap-2">
          <input className="input" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="e.g. show average revenue by region" />
          <button className="btn-secondary" onClick={generate} disabled={loading}>Generate SQL</button>
        </div>
        <label className="text-xs text-slate-500 mt-2 block">SQL (editable)</label>
        <textarea className="input font-mono h-24" value={sql} onChange={(e) => setSql(e.target.value)} />
        <button className="btn-primary" onClick={runSql} disabled={loading}>{loading ? "Running..." : "Run Query"}</button>
      </div>

      {result && (
        <div className="card overflow-x-auto">
          <p className="text-xs text-slate-500 mb-2">Source: {result.sql_source} · {result.row_count} row(s)</p>
          <table className="text-sm w-full">
            <thead><tr>{(result.columns || []).map((c: string) => <th key={c} className="text-left pr-4 text-slate-500">{c}</th>)}</tr></thead>
            <tbody>
              {(result.rows || []).slice(0, 50).map((r: any, i: number) => (
                <tr key={i}>{(result.columns || []).map((c: string) => <td key={c} className="pr-4">{String(r[c])}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
