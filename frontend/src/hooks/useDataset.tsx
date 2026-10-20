import React, { createContext, useContext, useEffect, useState } from "react";
import { Dataset } from "@/types";
import { api } from "@/services/api";

interface DatasetContextType {
  datasets: Dataset[];
  currentDataset: Dataset | null;
  setCurrentDatasetId: (id: string | null) => void;
  refreshDatasets: () => Promise<void>;
}

const DatasetContext = createContext<DatasetContextType | null>(null);

export function DatasetProvider({ children }: { children: React.ReactNode }) {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [currentId, setCurrentId] = useState<string | null>(() => localStorage.getItem("currentDatasetId"));

  const refreshDatasets = async () => {
    try {
      const list = await api.listDatasets();
      setDatasets(list);
      if (!currentId && list.length > 0) setCurrentDatasetId(list[0].id);
    } catch {
      /* backend may be offline; ignore */
    }
  };

  useEffect(() => {
    refreshDatasets();
  }, []);

  const setCurrentDatasetId = (id: string | null) => {
    setCurrentId(id);
    if (id) localStorage.setItem("currentDatasetId", id);
    else localStorage.removeItem("currentDatasetId");
  };

  const currentDataset = datasets.find((d) => d.id === currentId) || null;

  return (
    <DatasetContext.Provider value={{ datasets, currentDataset, setCurrentDatasetId, refreshDatasets }}>
      {children}
    </DatasetContext.Provider>
  );
}

export function useDataset() {
  const ctx = useContext(DatasetContext);
  if (!ctx) throw new Error("useDataset must be used within DatasetProvider");
  return ctx;
}
