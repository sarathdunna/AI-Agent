import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { EmptyState } from "@/components/Skeleton";

const STEPS = ["Target", "Problem Type", "Features", "Model", "Train/Test Split", "Train", "Compare", "Explain"];

export default function MLStudio() {
  const { currentDataset } = useDataset();
  const { push } = useToast();
  const [step, setStep] = useState(0);
  const [target, setTarget] = useState("");
  const [problemType, setProblemType] = useState<{ problem_type: string; explanation: string } | null>(null);
  const [features, setFeatures] = useState<string[]>([]);
  const [algorithms, setAlgorithms] = useState<any[]>([]);
  const [algorithm, setAlgorithm] = useState("");
  const [testSize, setTestSize] = useState(0.2);
  const [tune, setTune] = useState(false);
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState<any>(null);
  const [importance, setImportance] = useState<any>(null);

  useEffect(() => {
    if (currentDataset) setTarget(currentDataset.columns[currentDataset.columns.length - 1] || "");
  }, [currentDataset?.id]);

  if (!currentDataset) return <EmptyState title="No dataset selected" description="Select a dataset from the top bar." />;

  const detectProblemType = async () => {
    const res = await api.problemType(currentDataset.id, target);
    setProblemType(res);
    const algos = await api.algorithms(res.problem_type);
    setAlgorithms(algos.algorithms);
    setAlgorithm(algos.algorithms[0]?.name || "");
    setFeatures(currentDataset.columns.filter((c) => c !== target));
    setStep(1);
  };

  const toggleFeature = (col: string) => setFeatures((f) => (f.includes(col) ? f.filter((c) => c !== col) : [...f, col]));

  const runTraining = async () => {
    setTraining(true);
    try {
      const res = await api.train({
        dataset_id: currentDataset.id,
        target: problemType?.problem_type === "clustering" ? null : target,
        feature_columns: features,
        problem_type: problemType?.problem_type,
        algorithm,
        test_size: testSize,
        tune,
      });
      setTrainResult(res);
      push("Model trained successfully", "success");
      setStep(6);
      if (res.model_id) {
        const imp = await api.importance(res.model_id);
        setImportance(imp);
      }
    } catch (err: any) {
      push(err.message || "Training failed", "error");
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-slate-800">ML Studio</h1>

      <div className="flex gap-1 flex-wrap text-xs">
        {STEPS.map((s, i) => (
          <span key={s} className={`px-2 py-1 rounded-full ${i === step ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-500"}`}>{i + 1}. {s}</span>
        ))}
      </div>

      {step === 0 && (
        <div className="card space-y-3">
          <label className="text-sm font-medium">Select target column (leave for clustering)</label>
          <select className="input w-64" value={target} onChange={(e) => setTarget(e.target.value)}>
            <option value="">— none (clustering) —</option>
            {currentDataset.columns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <button className="btn-primary" onClick={detectProblemType}>Next: Detect Problem Type</button>
        </div>
      )}

      {step >= 1 && problemType && (
        <div className="card space-y-2">
          <p className="font-semibold">Problem type: <span className="text-brand-700">{problemType.problem_type}</span></p>
          <p className="text-sm text-slate-600">{problemType.explanation}</p>
        </div>
      )}

      {step === 1 && (
        <div className="card space-y-3">
          <p className="font-medium text-sm">Select feature columns</p>
          <div className="flex flex-wrap gap-2">
            {currentDataset.columns.filter((c) => c !== target).map((c) => (
              <label key={c} className={`text-xs px-3 py-1 rounded-full border cursor-pointer ${features.includes(c) ? "bg-brand-600 text-white border-brand-600" : "border-slate-300"}`}>
                <input type="checkbox" className="hidden" checked={features.includes(c)} onChange={() => toggleFeature(c)} />
                {c}
              </label>
            ))}
          </div>
          <button className="btn-primary" onClick={() => setStep(2)}>Next: Choose Model</button>
        </div>
      )}

      {step === 2 && (
        <div className="card space-y-3">
          <p className="font-medium text-sm">Choose algorithm</p>
          <div className="grid md:grid-cols-2 gap-3">
            {algorithms.map((a) => (
              <label key={a.name} className={`border rounded-lg p-3 cursor-pointer ${algorithm === a.name ? "border-brand-600 bg-brand-50" : "border-slate-200"}`}>
                <input type="radio" className="hidden" checked={algorithm === a.name} onChange={() => setAlgorithm(a.name)} />
                <p className="font-semibold text-sm">{a.name}</p>
                <p className="text-xs text-slate-500 mt-1">Pros: {a.pros.join(", ")}</p>
                <p className="text-xs text-slate-500">Cons: {a.cons.join(", ")}</p>
              </label>
            ))}
          </div>
          <button className="btn-primary" onClick={() => setStep(3)}>Next: Train/Test Split</button>
        </div>
      )}

      {step === 3 && (
        <div className="card space-y-3">
          <label className="text-sm font-medium">Test size: {Math.round(testSize * 100)}%</label>
          <input type="range" min={0.1} max={0.4} step={0.05} value={testSize} onChange={(e) => setTestSize(parseFloat(e.target.value))} />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={tune} onChange={(e) => setTune(e.target.checked)} /> Enable hyperparameter tuning (RandomizedSearchCV)
          </label>
          <button className="btn-primary" onClick={() => setStep(4)}>Next: Train</button>
        </div>
      )}

      {step === 4 && (
        <div className="card space-y-3">
          <p className="text-sm text-slate-600">Ready to train {algorithm} ({problemType?.problem_type}) on {features.length} feature(s).</p>
          <button className="btn-primary" onClick={runTraining} disabled={training}>{training ? "Training..." : "Train Model"}</button>
        </div>
      )}

      {step >= 6 && trainResult && (
        <div className="card space-y-3">
          <p className="font-semibold text-slate-800">Model Performance</p>
          <div className="flex gap-3 flex-wrap text-sm">
            {Object.entries(trainResult.metrics).filter(([k]) => !["explanations", "confusion_matrix"].includes(k)).map(([k, v]: any) => (
              <span key={k} className="bg-slate-100 rounded px-3 py-1">{k}: {typeof v === "object" ? JSON.stringify(v) : String(v)}</span>
            ))}
          </div>
          {trainResult.tuning && (
            <div className="text-sm">
              <p className="font-medium mt-2">Tuning: before vs after</p>
              <pre className="text-xs bg-slate-50 rounded p-2 overflow-x-auto">{JSON.stringify({ before: trainResult.tuning.before, after: trainResult.tuning.after, best_params: trainResult.tuning.best_params }, null, 2)}</pre>
            </div>
          )}
          <p className="text-xs text-slate-500">Model ID: {trainResult.model_id}</p>
        </div>
      )}

      {step >= 6 && importance?.available && (
        <div className="card space-y-2">
          <p className="font-semibold text-slate-800">Feature Importance / Explainability</p>
          <p className="text-sm text-slate-600">{importance.explanation}</p>
          <div className="space-y-1">
            {importance.features.slice(0, 10).map((f: any) => (
              <div key={f.feature} className="flex items-center gap-2 text-xs">
                <span className="w-40 truncate">{f.feature}</span>
                <div className="flex-1 bg-slate-100 rounded h-2">
                  <div className="bg-brand-600 h-2 rounded" style={{ width: `${Math.min(100, f.importance * 400)}%` }} />
                </div>
                <span>{f.importance}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
