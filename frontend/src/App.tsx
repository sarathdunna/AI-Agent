import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppLayout from "@/layouts/AppLayout";
import { ToastProvider } from "@/hooks/useToast";
import { DatasetProvider } from "@/hooks/useDataset";

import Dashboard from "@/pages/Dashboard";
import Datasets from "@/pages/Datasets";
import DataProfile from "@/pages/DataProfile";
import DataCleaning from "@/pages/DataCleaning";
import EDA from "@/pages/EDA";
import Visualizations from "@/pages/Visualizations";
import AskData from "@/pages/AskData";
import SQLAgent from "@/pages/SQLAgent";
import MLStudio from "@/pages/MLStudio";
import Predictions from "@/pages/Predictions";
import Reports from "@/pages/Reports";
import KnowledgeAssistant from "@/pages/KnowledgeAssistant";

export default function App() {
  return (
    <ToastProvider>
      <DatasetProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/datasets" element={<Datasets />} />
              <Route path="/profile" element={<DataProfile />} />
              <Route path="/cleaning" element={<DataCleaning />} />
              <Route path="/eda" element={<EDA />} />
              <Route path="/visualizations" element={<Visualizations />} />
              <Route path="/ask" element={<AskData />} />
              <Route path="/sql" element={<SQLAgent />} />
              <Route path="/ml-studio" element={<MLStudio />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/knowledge" element={<KnowledgeAssistant />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </DatasetProvider>
    </ToastProvider>
  );
}
