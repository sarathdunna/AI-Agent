import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { api } from "@/services/api";
import { useDataset } from "@/hooks/useDataset";
import { useToast } from "@/hooks/useToast";
import { EmptyState } from "@/components/Skeleton";

export default function Datasets() {
  const { datasets, refreshDatasets, setCurrentDatasetId, currentDataset } = useDataset();
  const { push } = useToast();
  const fileInput = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const result = await api.uploadDataset(file);
      await refreshDatasets();
      setCurrentDatasetId(result.id);
      push(`Uploaded '${result.original_filename}'`, "success");
    } catch (err: any) {
      push(err.message || "Upload failed", "error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-800">Datasets</h1>
        <input ref={fileInput} type="file" accept=".csv,.xlsx,.xls" hidden onChange={(e) => e.target.files && handleUpload(e.target.files[0])} />
        <button className="btn-primary" onClick={() => fileInput.current?.click()} disabled={uploading}>
          <UploadCloud size={18} /> {uploading ? "Uploading..." : "Upload Dataset"}
        </button>
      </div>

      {datasets.length === 0 ? (
        <EmptyState title="No datasets yet" description="Upload a CSV or Excel file to get started." />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-slate-200">
                <th className="py-2 pr-4">Filename</th>
                <th className="py-2 pr-4">Rows</th>
                <th className="py-2 pr-4">Columns</th>
                <th className="py-2 pr-4">Cleaned</th>
                <th className="py-2 pr-4">Uploaded</th>
                <th className="py-2" />
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.id} className={`border-b border-slate-100 ${currentDataset?.id === d.id ? "bg-brand-50" : ""}`}>
                  <td className="py-2 pr-4 font-medium">{d.original_filename}</td>
                  <td className="py-2 pr-4">{d.n_rows}</td>
                  <td className="py-2 pr-4">{d.n_cols}</td>
                  <td className="py-2 pr-4">{d.is_cleaned ? "Yes" : "No"}</td>
                  <td className="py-2 pr-4">{new Date(d.created_at).toLocaleString()}</td>
                  <td className="py-2">
                    <button className="btn-secondary" onClick={() => setCurrentDatasetId(d.id)}>
                      Select
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
