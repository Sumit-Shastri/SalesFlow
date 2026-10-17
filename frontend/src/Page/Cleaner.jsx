import { useState } from "react";
import { uploadFile } from "../Service/api";
import "../Style/Cleaner.css";
function Cleaner() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleCleaning() {
    if (!file) {
      setError("Please upload a dataset.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Replace /clean with the actual backend route.
      const data = await uploadFile("/clean", file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="service-page">
      <h1>Data Cleaning</h1>

      <p>
        Prepare your sales data for reliable analysis.
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
          onClick={handleCleaning}
          disabled={loading}
        >
          {loading ? "Cleaning..." : "Clean Dataset"}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {result && (
        <div className="result-box">
          <h2>Cleaning Results</h2>

          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Cleaner;