import { useMemo, useState } from "react";
import { requestJson, requestPdf } from "../api";
import "../UploadPage.css";

const allowedExtensions = [".csv", ".xlsx", ".xls"];

function formatNumber(value) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(Number(value ?? 0));
}

function formatMoney(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(Number(value ?? 0));
}

function formatCompactMoney(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(Number(value ?? 0));
}

function DataPreview({ columns, rows, title = "Data Preview" }) {
  if (!columns?.length) return null;

  return (
    <section className="preview-section">
      <h2>{title}</h2>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
          </thead>
          <tbody>
            {rows?.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {columns.map((column) => (
                  <td key={column}>{row[column] == null ? "—" : String(row[column])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function IssueList({ issues = [] }) {
  if (!issues.length) {
    return <p className="status-message success">No validation issues were found.</p>;
  }

  return (
    <ul className="issue-list">
      {issues.map((issue, index) => (
        <li key={`${issue.code}-${index}`} className={issue.severity}>
          <strong>{issue.severity === "error" ? "Needs attention" : "Review suggested"}</strong>
          <span>{issue.message}</span>
          {issue.count > 0 && <small>{issue.count} affected record{issue.count === 1 ? "" : "s"}</small>}
        </li>
      ))}
    </ul>
  );
}

function Dashboard({ analysis }) {
  const kpis = analysis.overall_kpis;
  const revenueRanking = analysis.performance_analysis?.revenue_ranking ?? [];
  const monthly = Object.entries(analysis.time_analysis?.monthly_analysis ?? {});
  const maxRevenue = Math.max(...monthly.map(([, item]) => Number(item.total_revenue)), 1);
  const trends = analysis.time_analysis?.trends ?? {};
  const growth = analysis.growth_analysis?.growth_summary ?? {};

  return (
    <section className="dashboard-results">
      <div className="section-heading">
        <div>
          <span className="upload-eyebrow">LIVE ANALYSIS</span>
          <h2>Your sales dashboard</h2>
        </div>
        <span className="result-period">{kpis.first_date} to {kpis.last_date}</span>
      </div>

      <div className="result-metric-grid">
        <Metric label="Total Revenue" value={formatMoney(kpis.total_revenue)} />
        <Metric label="Quantity Sold" value={formatNumber(kpis.total_units_sold)} />
        <Metric label="Sales Records" value={formatNumber(kpis.number_of_sales_records)} />
        <Metric label="Average Unit Price" value={formatMoney(kpis.average_unit_price)} />
      </div>

      <div className="results-grid">
        <section className="result-card trend-card">
          <h3>Monthly Revenue</h3>
          {monthly.length ? (
            <div className="revenue-bars" aria-label="Monthly revenue chart">
              {monthly.map(([month, value]) => (
                <div className="revenue-bar" key={month}>
                  <span className="bar-value" title={formatMoney(value.total_revenue)}>
                    {formatCompactMoney(value.total_revenue)}
                  </span>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{ height: `${Math.max(6, (Number(value.total_revenue) / maxRevenue) * 100)}%` }}
                    />
                  </div>
                  <small>{month}</small>
                </div>
              ))}
            </div>
          ) : <p className="empty-state">Not enough time-series data to chart yet.</p>}
        </section>

        <section className="result-card">
          <h3>Product Revenue Ranking</h3>
          <ol className="ranking-list">
            {revenueRanking.slice(0, 6).map((item, index) => (
              <li key={item.Product}>
                <span>{index + 1}. {item.Product}</span>
                <strong>{formatMoney(item.Revenue)}</strong>
              </li>
            ))}
          </ol>
        </section>
      </div>

      <div className="results-grid three-up">
        <Metric label="Revenue Trend" value={trends.revenue_trend ?? "Not available"} />
        <Metric label="Quantity Trend" value={trends.quantity_trend ?? "Not available"} />
        <Metric
          label="Overall Revenue Growth"
          value={growth.overall_revenue_growth_percentage == null ? "Not enough periods" : `${formatNumber(growth.overall_revenue_growth_percentage)}%`}
        />
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="result-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function UploadPage({ onBack }) {
  const [file, setFile] = useState(null);
  const [upload, setUpload] = useState(null);
  const [validation, setValidation] = useState(null);
  const [cleaning, setCleaning] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [insights, setInsights] = useState(null);
  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [activeAction, setActiveAction] = useState("");

  const step = useMemo(() => {
    if (analysis) return 5;
    if (cleaning?.cleaning_passed) return 4;
    if (validation) return 3;
    if (upload) return 2;
    return 1;
  }, [analysis, cleaning, upload, validation]);

  function clearDownstream() {
    setValidation(null);
    setCleaning(null);
    setAnalysis(null);
    setInsights(null);
    setNotice("");
  }

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    const extension = selectedFile.name.slice(selectedFile.name.lastIndexOf(".")).toLowerCase();
    if (!allowedExtensions.includes(extension)) {
      setError("Please upload a CSV or Excel file (.csv, .xlsx, or .xls).");
      setFile(null);
      setUpload(null);
      clearDownstream();
      return;
    }

    setError("");
    setFile(selectedFile);
    setUpload(null);
    clearDownstream();
  }

  async function runAction(action, work) {
    setActiveAction(action);
    setError("");
    setNotice("");
    try {
      await work();
    } catch (requestError) {
      setError(requestError.message || "Unable to complete this step. Please try again.");
    } finally {
      setActiveAction("");
    }
  }

  function handleUpload() {
    if (!file) return;
    runAction("upload", async () => {
      const formData = new FormData();
      formData.append("file", file);
      const result = await requestJson("/api/upload", { method: "POST", body: formData });
      setUpload(result);
      clearDownstream();
      setNotice(result.message);
    });
  }

  function handleValidate() {
    runAction("validate", async () => {
      const result = await requestJson("/api/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: upload.analysis_id }),
      });
      setValidation(result);
      setCleaning(null);
      setAnalysis(null);
      setInsights(null);
      setNotice(result.message);
    });
  }

  function handleClean() {
    runAction("clean", async () => {
      const result = await requestJson("/api/clean", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: upload.analysis_id, remove_duplicates: removeDuplicates }),
      });
      setCleaning(result);
      setAnalysis(null);
      setInsights(null);
      setNotice(result.message);
    });
  }

  function handleAnalyze() {
    runAction("analyze", async () => {
      const result = await requestJson("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: upload.analysis_id }),
      });
      setAnalysis(result.analysis);
      setInsights(null);
      setNotice(result.message);
    });
  }

  function handleInsights() {
    runAction("insights", async () => {
      const result = await requestJson("/api/report/insights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis_id: upload.analysis_id }),
      });
      setInsights(result.insights);
      setNotice(result.message);
    });
  }

  function handlePdf() {
    runAction("pdf", async () => {
      const blob = await requestPdf("/api/report/pdf", { analysis_id: upload.analysis_id });
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = "salesflow-sales-performance-report.pdf";
      link.click();
      URL.revokeObjectURL(downloadUrl);
      setNotice("Your PDF report was generated and downloaded.");
    });
  }

  return (
    <div className="upload-page">
      <nav className="upload-navbar">
        <div className="logo">Sales<span>Flow</span><span className="logo-dot">.</span></div>
        <span className="upload-step">STEP {String(step).padStart(2, "0")} / 05</span>
      </nav>

      <main className="upload-main">
        <button className="back-button" onClick={onBack}>← Back to Home</button>

        <div className="upload-heading">
          <span className="upload-eyebrow">GUIDED SALES ANALYSIS</span>
          <h1>Bring your data.<br /><span className="gradient-text">We'll find the story.</span></h1>
          <p>Upload a sales file, validate and clean it, then explore analysis based on your actual records.</p>
        </div>

        {!upload && (
          <>
            <label className="upload-box">
              <input type="file" accept=".csv,.xlsx,.xls" onChange={handleFileChange} />
              <div className="upload-icon">↑</div>
              <h3>Drop your file here</h3>
              <p>or click to browse your computer</p>
              <div className="file-formats"><span>CSV</span><span>XLSX</span><span>XLS</span></div>
            </label>

            {file && (
              <div className="selected-file">
                <div className="file-icon">▤</div>
                <div className="file-info"><strong>{file.name}</strong><p>{(file.size / 1024).toFixed(2)} KB · Ready to upload</p></div>
                <button className="remove-file" onClick={() => setFile(null)} aria-label="Remove selected file">×</button>
              </div>
            )}
            <button className="upload-proceed" disabled={!file || activeAction} onClick={handleUpload}>
              {activeAction === "upload" ? "Uploading..." : "Upload & Preview"}<span>{activeAction === "upload" ? "…" : "→"}</span>
            </button>
          </>
        )}

        {error && <div className="upload-error" role="alert">{error}</div>}
        {notice && <div className="status-message success">{notice}</div>}

        {upload && (
          <>
            <section className="workflow-card">
              <div className="section-heading">
                <div><span className="upload-eyebrow">UPLOADED FILE</span><h2>{upload.filename}</h2></div>
                <span className="record-count">{upload.total_records} records</span>
              </div>
              <p>Your original upload remains unchanged in this analysis session.</p>
            </section>
            <DataPreview columns={upload.columns} rows={upload.preview} />
            {!validation && (
              <button className="upload-proceed" disabled={activeAction} onClick={handleValidate}>
                {activeAction === "validate" ? "Checking data quality..." : "Validate Dataset"}<span>{activeAction === "validate" ? "…" : "→"}</span>
              </button>
            )}
          </>
        )}

        {validation && (
          <section className="workflow-card">
            <div className="section-heading"><div><span className="upload-eyebrow">DATA QUALITY</span><h2>Validation results</h2></div><span className={validation.validation_passed ? "pill success" : "pill warning"}>{validation.validation_passed ? "Valid" : "Review needed"}</span></div>
            <IssueList issues={validation.issues} />
            {validation.can_clean ? (
              <div className="cleaning-options">
                <p>Automatic cleaning uses SalesFlow's existing rules. It trims text, removes malformed or non-positive records, converts data types, sorts dates, and keeps your original file intact.</p>
                <label className="checkbox-row"><input type="checkbox" checked={removeDuplicates} onChange={(event) => setRemoveDuplicates(event.target.checked)} /> Remove duplicate rows</label>
                {!cleaning && <button className="upload-proceed" disabled={activeAction} onClick={handleClean}>{activeAction === "clean" ? "Cleaning data..." : "Clean & Review Data"}<span>{activeAction === "clean" ? "…" : "→"}</span></button>}
              </div>
            ) : <p className="manual-note">This file is missing a required column. Please correct the source file manually and upload it again; SalesFlow will not guess a replacement column.</p>}
          </section>
        )}

        {cleaning?.cleaning_passed && (
          <>
            <section className="workflow-card">
              <div className="section-heading"><div><span className="upload-eyebrow">CLEANING COMPLETE</span><h2>Review cleaned data</h2></div><span className="pill success">Ready</span></div>
              <div className="cleaning-summary">
                <Metric label="Records kept" value={`${cleaning.summary.records_after} of ${cleaning.summary.records_before}`} />
                <Metric label="Rows removed" value={cleaning.summary.records_removed} />
                <Metric label="Duplicates removed" value={cleaning.summary.duplicate_rows_removed} />
              </div>
              <p className="summary-note">{cleaning.summary.note}</p>
            </section>
            <DataPreview columns={cleaning.columns} rows={cleaning.preview} title="Cleaned Data Preview" />
            {!analysis && <button className="upload-proceed" disabled={activeAction} onClick={handleAnalyze}>{activeAction === "analyze" ? "Running analysis..." : "Run Sales Analysis"}<span>{activeAction === "analyze" ? "…" : "→"}</span></button>}
          </>
        )}

        {analysis && (
          <>
            <Dashboard analysis={analysis} />
            <section className="workflow-card report-card">
              <div className="section-heading"><div><span className="upload-eyebrow">REPORTING</span><h2>Insights & PDF</h2></div></div>
              <p>Gemini insights use the verified analysis. If Gemini is unavailable, you can still download a data-driven PDF with a clear note that AI interpretation is unavailable.</p>
              <div className="report-actions">
                <button className="secondary-button" disabled={activeAction} onClick={handleInsights}>{activeAction === "insights" ? "Generating insights..." : "Generate AI Insights"}</button>
                <button className="upload-proceed compact" disabled={activeAction} onClick={handlePdf}>{activeAction === "pdf" ? "Generating PDF..." : "Download PDF Report"}<span>{activeAction === "pdf" ? "…" : "↓"}</span></button>
              </div>
              {insights && (
                <div className="insights-preview">
                  <h3>AI Executive Summary</h3>
                  <p>{insights.section_explanations?.executive_summary || "Gemini returned no executive-summary text."}</p>
                  {insights.key_findings?.length > 0 && <><h3>Key Findings</h3><ul>{insights.key_findings.slice(0, 3).map((finding) => <li key={finding.title}><strong>{finding.title}:</strong> {finding.finding}</li>)}</ul></>}
                </div>
              )}
            </section>
          </>
        )}

        <p className="upload-security">Your file is processed locally by the SalesFlow backend.</p>
      </main>
    </div>
  );
}

export default UploadPage;
