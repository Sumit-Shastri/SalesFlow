# SalesFlow Project Guide

This guide explains the code flow in beginner-friendly terms. SalesFlow keeps
its main responsibilities separate: routes coordinate a request, services do
the data work, and the React frontend displays the result.

## Main flow

```text
UploadPage.jsx
  -> POST /api/upload
  -> session_store.py saves original file
  -> loader.py reads preview
  -> POST /api/validate
  -> validator.py normalizes and reports issues
  -> POST /api/clean
  -> cleaner.py writes cleaned.csv
  -> POST /api/analyze
  -> analyzer.py produces analysis.json
  -> POST /api/report/insights (optional Gemini text)
  -> POST /api/report/pdf (download)
```

## Important backend files

| File | Main responsibility | Key inputs/outputs |
| --- | --- | --- |
| `app/main.py` | Builds the FastAPI application and registers routers. | Serves `/`, `/health`, and `/api/*`. |
| `api/upload.py` | Accepts CSV/Excel uploads and returns a small preview. | `UploadFile` → `analysis_id`, columns, five rows. |
| `api/workflow.py` | Coordinates later stages; does not duplicate business rules. | Session request → JSON result or PDF response. |
| `services/loader.py` | Reads CSV and Excel files. | Path → DataFrame. |
| `services/session_store.py` | Creates safe temporary session directories. | ID → original/working/cleaned/generated paths. |
| `services/validator.py` | Normalizes names and checks required fields. | DataFrame → normalized frame plus issues, or validated frame. |
| `services/cleaner.py` | Removes unsafe records and standardizes the clean copy. | Normalized DataFrame → cleaned frame and summary. |
| `services/analyzer.py` | Calculates KPIs, product/time/performance/growth outputs. | Cleaned DataFrame → analysis dictionary. |
| `services/report/report_parser.py` | Reorganizes analysis and creates chart buffers for reporting. | Analysis → eight report sections. |
| `services/report/report_insight_generator.py` | Calls Gemini and checks the returned JSON shape. | Parsed report → structured insight dictionary. |
| `services/report/report_pdf_generator.py` | Builds the final ReportLab PDF. | Parsed report + insight dictionary → `.pdf`. |

## Session flow

`create_session()` creates a UUID analysis ID and stores the exact uploaded
bytes as `original.csv`, `original.xlsx`, or `original.xls`. The API returns
that ID to React. Every later button sends the same ID in JSON.

Validation saves `working.csv`, which holds normalized column names. Cleaning
uses that file but leaves the original untouched; its output is `cleaned.csv`.
Analysis writes `analysis.json`, and generated insights are saved as
`ai_insights.json`. These files make it clear which stage produced each value.

## Validation

`normalize_column_names()` maps common variants such as `Order Date`, `Item`,
`Qty`, and `Price` to SalesFlow's four canonical fields. It rejects ambiguous
duplicate matches instead of guessing.

`validate_sales_data_with_issues()` is used by the workflow UI. It returns all
independent issues it can find: missing columns, invalid dates, blank products,
non-numeric fields, non-positive values, empty rows, and duplicate rows.

`validate_sales_data()` remains useful to service callers that need a validated
DataFrame. It raises a `ValueError` for the first error and converts dates and
numeric fields to usable types.

## Cleaning

`clean_sales_data()` is an orchestrator, not a second cleaning engine. It calls
the existing small functions in `cleaner.py` in a safe order:

1. Remove completely empty rows and trim text.
2. Normalize product whitespace.
3. Optionally remove duplicate rows.
4. Coerce date and numeric values so malformed values become explicit.
5. Remove missing/malformed values and non-positive quantity/price rows.
6. Convert types, select the four required columns, and sort by date.

It returns both the cleaned DataFrame and an honest count-based summary. If all
records would be removed, it raises an error rather than claiming success.

## Analysis

`run_full_analysis()` first calls `add_revenue_column()`, then returns these
top-level sections:

- `overall_kpis`
- `product_analysis`
- `time_analysis`
- `performance_analysis`
- `growth_analysis`

The dashboard reads those real keys. For example, product revenue ranking is
`performance_analysis.revenue_ranking`, not a hardcoded list.

## Reporting and Gemini

`run_full_report_parser()` converts analyzer output into reporting sections and
Matplotlib chart buffers. It handles a single-month dataset by placing an
explanatory placeholder where month-over-month comparison is unavailable.

`generate_insights()` creates the Gemini client only when the user presses
Generate AI Insights. This lets upload and analysis work without a key. The
function requires the exact expected JSON top-level keys before saving results.
The frontend shows errors returned by the API and does not portray a failure as
successful insight generation.

## Frontend files

| File | Purpose |
| --- | --- |
| `src/App.jsx` | Displays the welcome screen and opens the workflow. |
| `src/components/UploadPage.jsx` | Holds workflow state, calls API routes, previews data, and renders the dashboard. |
| `src/api.js` | One place for JSON/PDF requests and readable API errors. |
| `src/UploadPage.css` | Dark purple workflow/dashboard layout and responsive styles. |
| `vite.config.js` | Proxies `/api` calls to the FastAPI server during development. |

## Debugging checklist

1. Open `http://127.0.0.1:8000/docs` and confirm the API starts.
2. Verify the browser Network request includes the current `analysis_id`.
3. Check the error response `detail` rather than guessing from the frontend.
4. For data errors, inspect the validation issue `code`, `message`, and count.
5. For Gemini errors, check only whether `GEMINI_API_KEY` exists—never print it.
6. For PDF errors, run analysis first and make sure Matplotlib/ReportLab are
   installed in the backend environment.
