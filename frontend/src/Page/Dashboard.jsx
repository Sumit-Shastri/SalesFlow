import React from "react";
import { Link } from "react-router-dom";
import "../Style/Dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard-container">
      <h1>SalesFlow Dashboard</h1>

      <p>
        Analyze, clean, validate, and visualize your sales data.
      </p>

      <div className="dashboard-services">
        <Link to="/loader" className="dashboard-card">
          <h2>Data Loader</h2>
          <p>Upload CSV or Excel files.</p>
        </Link>

        <Link to="/cleaner" className="dashboard-card">
          <h2>Data Cleaner</h2>
          <p>Clean and prepare your dataset.</p>
        </Link>

        <Link to="/validator" className="dashboard-card">
          <h2>Data Validator</h2>
          <p>Check data quality and validation errors.</p>
        </Link>

        <Link to="/analyzer" className="dashboard-card">
          <h2>Data Analyzer</h2>
          <p>Analyze sales data and generate insights.</p>
        </Link>
      </div>
    </div>
  );
}

export default Dashboard;