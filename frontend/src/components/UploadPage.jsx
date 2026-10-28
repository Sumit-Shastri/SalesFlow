import { useState } from "react";
import "../UploadPage.css";

function UploadPage() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);

  function handleFileChange(event) {
    const selectedFile = event.target.files[0];

    if (!selectedFile) {
      return;
    }

    const allowedExtensions = [".csv", ".xlsx", ".xls"];

    const extension = selectedFile.name
      .slice(selectedFile.name.lastIndexOf("."))
      .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setError("Please upload a CSV or Excel file.");
      setFile(null);
      return;
    }

    setError("");
    setFile(selectedFile);
  }

  async function handleUpload() {
  if (!file) return;

  setLoading(true);
  setError("");
  setPreview(null);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    const result = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof result.detail === "string"
          ? result.detail
          : JSON.stringify(result.detail)
      );
    }

    setPreview(result);
  } catch (err) {
    setError(
      err.message || "Unable to connect to the SalesFlow backend."
    );
  } finally {
    setLoading(false);
  }
}

  return (
    <div className="upload-page">
      <nav className="upload-navbar">
        <div className="logo">
          Sales<span>Flow</span>
          <span className="logo-dot">.</span>
        </div>

        <span className="upload-step">STEP 01 / 04</span>
      </nav>

      <main className="upload-main">
        <button
          className="back-button"
          onClick={() => window.location.reload()}
        >
          ← Back to Home
        </button>

        <div className="upload-heading">
          <span className="upload-eyebrow">LET'S GET STARTED</span>

          <h1>
            Bring your data.
            <br />
            <span className="gradient-text">We'll find the story.</span>
          </h1>

          <p>
            Upload your sales data to begin your analysis.
            We'll validate your file before processing it.
          </p>
        </div>

        <label className="upload-box">
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
          />

          <div className="upload-icon">↑</div>

          <h3>Drop your file here</h3>

          <p>or click to browse your computer</p>

          <div className="file-formats">
            <span>CSV</span>
            <span>XLSX</span>
            <span>XLS</span>
          </div>
        </label>

        {error && (
          <div className="upload-error">
            {error}
          </div>
        )}

        {file && (
          <div className="selected-file">
            <div className="file-icon">▤</div>

            <div className="file-info">
              <strong>{file.name}</strong>

              <p>
                {(file.size / 1024).toFixed(2)} KB · File selected
              </p>
            </div>

            <button
              className="remove-file"
              onClick={() => setFile(null)}
              aria-label="Remove selected file"
            >
              ×
            </button>
          </div>
        )}

        <button
        className="upload-proceed"
        disabled={!file || loading}
        onClick={handleUpload}
        >
        {loading
            ? "Uploading and validating..."
            : preview
            ? "File Validated ✓"
            : "Upload & Preview"}

        <span>{loading ? "…" : "→"}</span>
        </button>

        {preview && (
        <section className="preview-section">
            <h2>Data Preview</h2>

            <p>{preview.message}</p>

            <div className="preview-stats">
            <div>
                <strong>{preview.total_records}</strong>
                <span>Total Records</span>
            </div>

            <div>
                <strong>{preview.columns.length}</strong>
                <span>Total Columns</span>
            </div>
            </div>

            <div className="table-wrapper">
            <table>
                <thead>
                <tr>
                    {preview.columns.map((column) => (
                    <th key={column}>{column}</th>
                    ))}
                </tr>
                </thead>

                <tbody>
                {preview.preview.map((row, index) => (
                    <tr key={index}>
                    {preview.columns.map((column) => (
                        <td key={column}>
                        {row[column] == null
                            ? "—"
                            : String(row[column])}
                        </td>
                    ))}
                    </tr>
                ))}
                </tbody>
            </table>
            </div>
        </section>
        )}

        <p className="upload-security">
          Your file will be processed by the SalesFlow backend.
        </p>
      </main>
    </div>
  );
}

export default UploadPage;