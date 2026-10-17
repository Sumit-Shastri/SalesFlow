import { useState } from "react";
import { uploadFile } from "../Service/api";
import "../Style/Loader.css";
function Loader() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload() {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Replace /load with your actual backend endpoint.
      const data = await uploadFile("/load", file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="service-page">
      <h1>Data Loader</h1>

      <p>
        Upload your sales dataset to begin the analysis process.
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

        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Loading..." : "Load Dataset"}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {result && (
        <div className="result-box">
          <h2>Loading Results</h2>

          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Loader;