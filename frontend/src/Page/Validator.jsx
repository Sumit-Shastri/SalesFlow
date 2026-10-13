import { useState } from "react";
import { uploadFile } from "../Service/api";
import "../Style/Validator.css";

function Validator() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleValidation() {
    if (!file) {
      setError("Please select a dataset.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Replace /validate with the actual backend route.
      const data = await uploadFile("/validate", file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="service-page">
      <h1>Data Validation</h1>

      <p>
        Check your sales data for invalid values and data-quality issues.
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
          onClick={handleValidation}
          disabled={loading}
        >
          {loading ? "Validating..." : "Validate Dataset"}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}

      {result && (
        <div className="result-box">
          <h2>Validation Results</h2>

          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default Validator;