import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // ─────────────────────────────────────────────
  // UPLOAD EXCEL
  // ─────────────────────────────────────────────
  const uploadExcel = async () => {
    if (!file) {
      setError("Please select an Excel file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setError("");
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload_excel/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) setError(data.error || "Upload failed.");
      else alert("Excel uploaded successfully!");
    } catch {
      setError("Upload failed. Check backend.");
    }

    setLoading(false);
  };

  // ─────────────────────────────────────────────
  // SUPER AI QUERY ANALYZE
  // ─────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Unknown error");
      } else {
        setResult(data);
      }
    } catch {
      setError("Server unreachable");
    }

    setLoading(false);
  };

  return (
    <div className="app-container">
      <h1 className="title">Real Estate Market Analyzer (AI Powered)</h1>

      {/* UPLOAD */}
      <div className="upload-section">
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={(e) => setFile(e.target.files[0])}
          className="upload-input"
        />
        <button className="upload-btn" onClick={uploadExcel} disabled={loading}>
          {loading ? "Uploading..." : "Upload Excel"}
        </button>
      </div>

      {/* QUERY */}
      <input
        type="text"
        className="input-box"
        value={query}
        placeholder="Ask anything (e.g., Compare Wakad & Baner)"
        onChange={(e) => setQuery(e.target.value)}
      />

      <button className="button" onClick={handleAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {error && <p className="error-text">{error}</p>}

      {result && (
        <>
          {/* DETECTED LOCATIONS */}
          <h2 className="section-title">AI Detected Locations</h2>
          <p className="ai-box">{result.locations_used?.join(", ")}</p>

          {/* SUMMARY */}
          <h2 className="section-title">Summary</h2>
          <p className="summary-text">{result.summary}</p>

          {/* AI INSIGHTS */}
          <h2 className="section-title">AI Insights</h2>
          <p className="ai-box">{result.ai_message}</p>

          {/* TREND CHART */}
          {result.chart?.length > 0 && (
            <>
              <h2 className="section-title">Sales Trend</h2>
              <div className="chart-container">
                <ResponsiveContainer>
                  <LineChart data={result.chart}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="Year" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="Value"
                      stroke="#2563eb"
                      strokeWidth={3}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </>
          )}

          {/* TABLE */}
          <h2 className="section-title">Table Data</h2>
          <div className="table-scroll">
            <pre className="table-box">
              {JSON.stringify(result.table, null, 2)}
            </pre>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
