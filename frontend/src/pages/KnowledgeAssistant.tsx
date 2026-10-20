import { useState } from "react";
import { Send } from "lucide-react";
import { api } from "@/services/api";
import { useToast } from "@/hooks/useToast";

interface Msg {
  question: string;
  answer: string;
  matches: { doc: string; score: number }[];
}

const EXAMPLES = ["What is overfitting?", "Explain precision vs recall", "What is R-squared?"];

export default function KnowledgeAssistant() {
  const { push } = useToast();
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<Msg[]>([]);
  const [loading, setLoading] = useState(false);

  const ask = async (q?: string) => {
    const text = q || question;
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await api.knowledgeAsk(text);
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
      <h1 className="text-xl font-bold text-slate-800">Knowledge Assistant</h1>
      <p className="text-sm text-slate-500">Ask about core ML/stats concepts. Answers are retrieved from a local knowledge base via TF-IDF search.</p>

      <div className="flex gap-2 flex-wrap">
        {EXAMPLES.map((e) => (
          <button key={e} className="text-xs bg-slate-100 hover:bg-slate-200 rounded-full px-3 py-1" onClick={() => ask(e)}>{e}</button>
        ))}
      </div>

      <div className="space-y-4">
        {history.map((h, idx) => (
          <div key={idx} className="card space-y-2">
            <p className="font-medium text-slate-800">You: {h.question}</p>
            <p className="text-sm text-slate-700 whitespace-pre-wrap">{h.answer}</p>
            {h.matches.length > 0 && (
              <p className="text-xs text-slate-400">Sources: {h.matches.map((m) => `${m.doc} (${m.score})`).join(", ")}</p>
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input className="input" placeholder="Ask about a concept..." value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={(e) => e.key === "Enter" && ask()} />
        <button className="btn-primary" onClick={() => ask()} disabled={loading}><Send size={16} /> {loading ? "..." : "Send"}</button>
      </div>
    </div>
  );
}
