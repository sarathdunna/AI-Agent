import {
  BarChart, Bar, LineChart, Line, ScatterChart, Scatter, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";

const COLORS = ["#6366f1", "#818cf8", "#a5b4fc", "#4f46e5", "#c7d2fe", "#4338ca"];

export function ChartRenderer({ chartType, data }: { chartType: string; data: any[] }) {
  if (!data || data.length === 0) return <p className="text-sm text-slate-500">No data to display.</p>;

  if (chartType === "bar" || chartType === "count") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 11 }} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "pie") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" outerRadius={110} label>
            {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip /><Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "line") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="x" tick={{ fontSize: 11 }} /><YAxis />
          <Tooltip /><Line type="monotone" dataKey="y" stroke="#6366f1" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "scatter") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="x" type="number" tick={{ fontSize: 11 }} />
          <YAxis dataKey="y" type="number" />
          <Tooltip /><Scatter data={data} fill="#6366f1" />
        </ScatterChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "histogram") {
    return (
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="bin" tick={{ fontSize: 9 }} interval={0} angle={-30} textAnchor="end" height={60} />
          <YAxis /><Tooltip /><Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (chartType === "box" && data[0]) {
    const b = data[0];
    return (
      <div className="text-sm text-slate-700 space-y-1 py-4">
        <p>Min: {b.min}</p><p>Q1: {b.q1}</p><p>Median: {b.median}</p><p>Q3: {b.q3}</p><p>Max: {b.max}</p>
      </div>
    );
  }

  if (chartType === "heatmap") {
    const cols = Array.from(new Set(data.map((d: any) => d.x)));
    const cell = (x: string, y: string) => data.find((d: any) => d.x === x && d.y === y)?.value ?? 0;
    return (
      <div className="overflow-x-auto">
        <table className="text-xs border-collapse">
          <thead>
            <tr><th /> {cols.map((c) => <th key={c} className="px-2 py-1">{c}</th>)}</tr>
          </thead>
          <tbody>
            {cols.map((y) => (
              <tr key={y}>
                <td className="px-2 py-1 font-medium">{y}</td>
                {cols.map((x) => {
                  const v = cell(x, y);
                  const intensity = Math.round(Math.abs(v) * 200);
                  return (
                    <td key={x} className="px-2 py-1 text-center" style={{ backgroundColor: `rgba(99,102,241,${Math.abs(v)})`, color: Math.abs(v) > 0.5 ? "white" : "black" }}>
                      {v}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return <p className="text-sm text-slate-500">Unsupported chart type.</p>;
}
