import { useState } from "react";
import { Send } from "lucide-react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { AskResult } from "@/types";
import { EmptyState } from "@/components/Skeleton";
import { ChartRenderer } from "@/charts/ChartRenderer";

const EXAMPLES = ["How many rows are in this dataset?", "What is the average of the first numeric column?", "Show me the top 5 rows"];

export default function AskData() {
  const { currentDataset } = useDataset();
  const { push } = useToast();
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<AskResult[]>([]);
  const [loading, setLoading] = useState(false);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;

  const ask = async (q?: string) => {
    const text = q || question;
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await api.ask(currentDataset.id, text);
      setHistory((h) => [...h, res]);
      setQuestion("");
    } catch (err: any) {
      push(err.message || "Query failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">Ask Data</h1>

      <div className="flex gap-2 flex-wrap">
        {EXAMPLES.map((e) => (
          <button key={e} className="text-xs bg-slate-100 hover:bg-slate-200 rounded-full px-3 py-1" onClick={() => ask(e)}>
            {e}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {history.map((h, idx) => (
          <div key={idx} className="card space-y-3">
            <p className="font-medium text-slate-800">You: {h.question}</p>
            <p className="text-xs font-mono text-slate-500 bg-slate-50 rounded p-2">{h.sql}</p>
            {h.error ? (
              <p className="text-sm text-red-600">{h.error}</p>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="text-sm w-full">
                    <thead><tr>{h.columns.map((c) => <th key={c} className="text-left pr-4 text-slate-500">{c}</th>)}</tr></thead>
                    <tbody>
                      {h.rows.slice(0, 10).map((r, i) => (
                        <tr key={i}>{h.columns.map((c) => <td key={c} className="pr-4">{String(r[c])}</td>)}</tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {h.chart && <ChartRenderer chartType={h.chart.chart_type} data={h.chart.data} />}
                <p className="text-sm text-slate-600 border-t border-slate-100 pt-2">{h.explanation}</p>
              </>
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-2 sticky bottom-4">
        <input
          className="input"
          placeholder="Ask a question about your data..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
        />
        <button className="btn-primary" onClick={() => ask()} disabled={loading}>
          <Send size={16} /> {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
