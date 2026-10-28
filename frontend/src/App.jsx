import "./App.css";
import { useState } from "react";
import UploadPage from "./components/UploadPage";

function App() {

  const [currentPage, setCurrentPage] = useState("welcome");

  if (currentPage === "upload") {
    return <UploadPage />;
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="logo">
          Sales<span>Flow</span>
          <span className="logo-dot">.</span>
        </div>

        <div className="nav-right">
          <span className="status-dot"></span>
          Sales Intelligence Platform
        </div>
      </nav>

      <main className="hero">
        <div className="hero-content">
          <div className="badge">
            <span>✦</span> YOUR SALES, DECODED
          </div>

          <h1>
            Turn your sales data
            <br />
            into <span className="gradient-text">smart decisions.</span>
          </h1>

          <p className="description">
            Stop guessing. Start understanding.
            Upload your sales data, uncover hidden trends,
            and discover what's driving your business forward.
          </p>

          <div className="features">
            <div className="feature">
              <span className="feature-icon">↗</span>
              <div>
                <strong>Deep Analytics</strong>
                <p>Understand your performance</p>
              </div>
            </div>

            <div className="feature">
              <span className="feature-icon">◈</span>
              <div>
                <strong>Smart Insights</strong>
                <p>Discover meaningful patterns</p>
              </div>
            </div>

            <div className="feature">
              <span className="feature-icon">▤</span>
              <div>
                <strong>Ready-to-use Reports</strong>
                <p>Generate professional PDFs</p>
              </div>
            </div>
          </div>

          <button
            className="start-button"
            onClick={() => setCurrentPage("upload")}
          >
          Get Started <span>→</span>
          </button>

          <p className="support-text">
            Supports CSV and Excel files · Simple, guided workflow
          </p>
        </div>

        <div className="visual">
          <div className="visual-glow"></div>

          <div className="dashboard-card">
            <div className="card-header">
              <div>
                <span className="card-label">SALES OVERVIEW</span>
                <h3>Your business at a glance</h3>
              </div>

              <span className="live-badge">LIVE PREVIEW</span>
            </div>

            <div className="metric-grid">
              <div className="metric">
                <span>Total Revenue</span>
                <strong>₹12.8L</strong>
                <small>Illustrative metric</small>
              </div>

              <div className="metric">
                <span>Units Sold</span>
                <strong>8,420</strong>
                <small>Illustrative metric</small>
              </div>
            </div>

            <div className="chart-container">
              <div className="chart-heading">
                <span>Revenue Trend</span>
                <span>Monthly</span>
              </div>

              <div className="chart">
                <div className="chart-grid">
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>

                <svg
                  viewBox="0 0 400 140"
                  preserveAspectRatio="none"
                  className="chart-svg"
                  aria-label="Illustrative upward revenue trend"
                  role="img"
                >
                  <defs>
                    <linearGradient
                      id="chartGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor="#8b5cf6"
                        stopOpacity="0.35"
                      />
                      <stop
                        offset="100%"
                        stopColor="#8b5cf6"
                        stopOpacity="0"
                      />
                    </linearGradient>
                  </defs>

                  <path
                    d="M0 112 L55 90 L110 98 L165 62 L220 75 L275 42 L330 52 L400 12 L400 140 L0 140 Z"
                    fill="url(#chartGradient)"
                  />

                  <path
                    d="M0 112 L55 90 L110 98 L165 62 L220 75 L275 42 L330 52 L400 12"
                    fill="none"
                    stroke="#a78bfa"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>

              <div className="chart-months">
                <span>Jan</span>
                <span>Feb</span>
                <span>Mar</span>
                <span>Apr</span>
                <span>May</span>
                <span>Jun</span>
                <span>Jul</span>
                <span>Aug</span>
              </div>
            </div>

            <div className="insight">
              <span className="insight-icon">✦</span>
              <div>
                <strong>Find your next opportunity</strong>
                <p>
                  Turn your raw sales records into actionable insights.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer>
        <span>SalesFlow © 2026</span>
        <span>Built for better business decisions.</span>
      </footer>
    </div>
  );
}

export default App;