import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard, Database, ClipboardList, SprayCan, BarChart3, LineChart,
  MessageSquareText, Terminal, BrainCircuit, Wand2, FileText, BookOpenText,
} from "lucide-react";
import { useDataset } from "@/hooks/useDataset";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/datasets", label: "Datasets", icon: Database },
  { to: "/profile", label: "Data Profile", icon: ClipboardList },
  { to: "/cleaning", label: "Data Cleaning", icon: SprayCan },
  { to: "/eda", label: "EDA", icon: BarChart3 },
  { to: "/visualizations", label: "Visualizations", icon: LineChart },
  { to: "/ask", label: "Ask Data", icon: MessageSquareText },
  { to: "/sql", label: "SQL Agent", icon: Terminal },
  { to: "/ml-studio", label: "ML Studio", icon: BrainCircuit },
  { to: "/predictions", label: "Predictions", icon: Wand2 },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/knowledge", label: "Knowledge Assistant", icon: BookOpenText },
];

export default function AppLayout() {
  const { datasets, currentDataset, setCurrentDatasetId } = useDataset();

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 shrink-0 bg-white border-r border-slate-200 flex flex-col">
        <div className="px-5 py-5 border-b border-slate-200">
          <p className="font-bold text-brand-700 text-lg leading-tight">Data Analyst</p>
          <p className="text-xs text-slate-500">+ ML Agent</p>
        </div>
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-1">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0">
          <div />
          <div className="flex items-center gap-3">
            <label className="text-xs text-slate-500">Active dataset</label>
            <select
              className="input w-64"
              value={currentDataset?.id || ""}
              onChange={(e) => setCurrentDatasetId(e.target.value || null)}
            >
              <option value="">— select a dataset —</option>
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.original_filename} ({d.n_rows}x{d.n_cols})
                </option>
              ))}
            </select>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
