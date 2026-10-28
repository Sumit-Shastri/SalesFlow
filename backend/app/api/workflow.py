"""API coordination for the SalesFlow upload-to-report workflow.

The business rules stay in the services package. This router only selects the
right session file, returns user-facing responses, and persists stage outputs.
"""
from datetime import date, datetime
import math

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services.analyzer import run_full_analysis
from app.services.cleaner import clean_sales_data
from app.services.loader import load_sales_file
from app.services.session_store import (
    get_cleaned_file,
    get_session_file,
    get_working_file,
    load_json,
    save_json,
    session_path,
)
from app.services.validator import (
    validate_sales_data,
    validate_sales_data_with_issues,
)

router = APIRouter(prefix="/api", tags=["Sales Workflow"])


class SessionRequest(BaseModel):
    analysis_id: str = Field(min_length=1)


class CleanRequest(SessionRequest):
    remove_duplicates: bool = True


class ReportRequest(SessionRequest):
    company_name: str = Field(default="SalesFlow Demo Company", max_length=120)
    report_title: str = Field(default="Sales Performance Report", max_length=160)


def _json_safe(value):
    """Convert pandas/numpy values into JSON values without inventing data."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, (float, np.floating)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if value is pd.NA or (not isinstance(value, (bytes, bytearray)) and pd.isna(value)):
        return None
    return value


def _preview(df: pd.DataFrame, size: int = 5) -> list[dict]:
    return _json_safe(df.head(size).to_dict(orient="records"))


def _validation_response(analysis_id: str, normalized: pd.DataFrame, issues: list[dict]) -> dict:
    has_errors = any(issue["severity"] == "error" for issue in issues)
    missing_columns = any(issue["code"] == "missing_columns" for issue in issues)
    return {
        "analysis_id": analysis_id,
        "validation_passed": not has_errors,
        "can_clean": not missing_columns,
        "total_records": len(normalized),
        "columns": normalized.columns.tolist(),
        "issues": _json_safe(issues),
        "preview": _preview(normalized),
        "message": (
            "Validation passed. Review the cleaning options before analysis."
            if not has_errors
            else "Validation found issues. Review them before choosing a cleaning option."
        ),
    }


def _analysis_for_session(analysis_id: str) -> dict:
    try:
        return load_json(analysis_id, "analysis.json")
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=409,
            detail="Run the sales analysis before generating a report.",
        ) from exc


def _quality_notes(analysis_id: str) -> list[str]:
    try:
        summary = load_json(analysis_id, "cleaning_summary.json")
    except FileNotFoundError:
        return ["No automatic cleaning summary is available for this session."]
    return [
        f"Automatic cleaning retained {summary['records_after']} of {summary['records_before']} records.",
        summary["note"],
    ]


def _build_parsed_report(analysis_id: str, request: ReportRequest) -> dict:
    """Use the existing parser only after analysis has successfully completed."""
    try:
        from app.services.report.report_parser import run_full_report_parser
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Report components are unavailable. Install the backend requirements.",
        ) from exc

    return run_full_report_parser(
        _analysis_for_session(analysis_id),
        request.company_name,
        request.report_title,
        str(get_session_file(analysis_id)),
        _quality_notes(analysis_id),
    )


def _insight_fallback() -> dict:
    """A transparent PDF fallback; it is never presented as an AI result."""
    return {
        "section_explanations": {},
        "key_findings": [],
        "recommendations": [],
        "conclusion": "AI-generated interpretation was not available when this PDF was created.",
        "areas_worth_investigating": [],
    }


@router.post("/validate")
def validate_uploaded_data(payload: SessionRequest):
    """Normalize and validate an upload while preserving the original session file."""
    try:
        original_path = get_session_file(payload.analysis_id)
        df = load_sales_file(str(original_path))
        normalized, issues = validate_sales_data_with_issues(df)
        # A normalized working copy lets the cleaner reuse the validator's mapping.
        normalized.to_csv(session_path(payload.analysis_id, "working.csv"), index=False)
        return _validation_response(payload.analysis_id, normalized, issues)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to validate this file.") from exc


@router.post("/clean")
def clean_uploaded_data(payload: CleanRequest):
    """Run the established cleaner on the validator's normalized working copy."""
    try:
        working = load_sales_file(str(get_working_file(payload.analysis_id)))
        normalized, issues = validate_sales_data_with_issues(working)
        if any(issue["code"] == "missing_columns" for issue in issues):
            raise HTTPException(
                status_code=422,
                detail="Required columns are missing and cannot be repaired automatically. Correct the source file and upload it again.",
            )

        cleaned, summary = clean_sales_data(
            normalized,
            remove_duplicates=payload.remove_duplicates,
        )
        _, remaining_issues = validate_sales_data_with_issues(cleaned)
        remaining_errors = [issue for issue in remaining_issues if issue["severity"] == "error"]
        if remaining_errors:
            return {
                "analysis_id": payload.analysis_id,
                "cleaning_passed": False,
                "summary": _json_safe(summary),
                "issues": _json_safe(remaining_errors),
                "message": "Automatic cleaning could not produce a valid dataset. Correct the source file and upload it again.",
            }

        cleaned.to_csv(session_path(payload.analysis_id, "cleaned.csv"), index=False)
        save_json(payload.analysis_id, "cleaning_summary.json", _json_safe(summary))
        return {
            "analysis_id": payload.analysis_id,
            "cleaning_passed": True,
            "summary": _json_safe(summary),
            "issues": _json_safe(remaining_issues),
            "columns": cleaned.columns.tolist(),
            "preview": _preview(cleaned),
            "message": "Cleaning complete. Review the cleaned data, then run the analysis.",
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to clean this file.") from exc


@router.post("/analyze")
def analyze_cleaned_data(payload: SessionRequest):
    """Analyze only the cleaned dataset, never the original upload by accident."""
    try:
        cleaned = load_sales_file(str(get_cleaned_file(payload.analysis_id)))
        validated = validate_sales_data(cleaned)
        analysis = _json_safe(run_full_analysis(validated))
        save_json(payload.analysis_id, "analysis.json", analysis)
        return {
            "analysis_id": payload.analysis_id,
            "analysis": analysis,
            "message": "Analysis complete. Dashboard metrics use the cleaned dataset.",
        }
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to analyze this dataset.") from exc


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    return {"analysis_id": analysis_id, "analysis": _analysis_for_session(analysis_id)}


@router.post("/report/insights")
def generate_report_insights(payload: ReportRequest):
    """Generate Gemini insight text after verified metrics and charts have been parsed."""
    try:
        from app.services.report.report_insight_generator import generate_insights
        insights = generate_insights(_build_parsed_report(payload.analysis_id, payload))
        save_json(payload.analysis_id, "ai_insights.json", _json_safe(insights))
        return {
            "analysis_id": payload.analysis_id,
            "insights": _json_safe(insights),
            "message": "AI report insights generated from the current analysis.",
        }
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (TimeoutError, ConnectionError) as exc:
        raise HTTPException(status_code=504, detail="Gemini did not respond in time. Please try again.") from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=502, detail="Gemini returned an invalid report response.") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Unable to generate AI report insights right now.") from exc


@router.post("/report/pdf")
def download_report_pdf(payload: ReportRequest):
    """Generate a PDF from parser data and saved AI insights when available."""
    try:
        from app.services.report.report_pdf_generator import generate_sales_report
        try:
            insights = load_json(payload.analysis_id, "ai_insights.json")
        except FileNotFoundError:
            insights = _insight_fallback()

        output_path = session_path(payload.analysis_id, f"salesflow-report-{payload.analysis_id[:8]}.pdf")
        generate_sales_report(_build_parsed_report(payload.analysis_id, payload), insights, output_path)
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename="salesflow-sales-performance-report.pdf",
        )
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to generate the PDF report.") from exc
