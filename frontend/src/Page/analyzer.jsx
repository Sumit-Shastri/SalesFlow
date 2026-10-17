import { useState } from "react";
import { uploadFile } from "../Service/api";

import "../Style/analyzer.css";

function Analyzer() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalysis() {
    if (!file) {
      setError("Please upload a dataset.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Replace /analyze with the actual backend route.
      const data = await uploadFile("/analyze", file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="service-page">
      <h1>Sales Data Analyzer</h1>

      <p>
        Generate summaries and insights from your sales dataset.
      </p>

      <div className="upload-box">
        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={(event) => {
            setFile(event.target.files?.[0] || null);
            setError("");
            setResult(null);
          }}
        />

        <button
          onClick={handleAnalysis}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze Dataset"}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {result && (
        <div className="result-box">
          <h2>Analysis Results</h2>

          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Analyzer;