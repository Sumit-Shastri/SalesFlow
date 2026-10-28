from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.loader import load_sales_file
from app.services.session_store import get_session_file
from app.services.validator import normalize_column_names, required_columns

router = APIRouter(prefix="/api", tags=["Sales Workflow"])


class ValidateRequest(BaseModel):
    analysis_id: str = Field(min_length=1)


def _blank_mask(series: pd.Series) -> pd.Series:
    """Treat nulls and whitespace-only strings as missing values."""
    return series.isna() | series.astype("string").str.strip().eq("").fillna(False)


def _record_numbers(mask: pd.Series, limit: int = 20) -> list[int]:
    """Return 1-based data-record numbers (header row excluded)."""
    return [int(position) + 1 for position in range(len(mask)) if bool(mask.iloc[position])][:limit]


@router.post("/validate")
def validate_uploaded_data(payload: ValidateRequest):
    """Validate an uploaded file and save a normalized working copy for cleaning."""
    try:
        original_path = get_session_file(payload.analysis_id)
        df = load_sales_file(str(original_path))

        if df.empty:
            return {
                "analysis_id": payload.analysis_id,
                "validation_passed": False,
                "can_clean": False,
                "total_records": 0,
                "columns": df.columns.tolist(),
                "issues": [{
                    "code": "empty_dataset",
                    "severity": "error",
                    "message": "The file contains no sales records.",
                    "count": 0,
                    "records": [],
                }],
                "preview": [],
            }

        try:
            normalized = normalize_column_names(df)
        except ValueError as exc:
            return {
                "analysis_id": payload.analysis_id,
                "validation_passed": False,
                "can_clean": False,
                "total_records": len(df),
                "columns": df.columns.tolist(),
                "issues": [{
                    "code": "ambiguous_columns",
                    "severity": "error",
                    "message": str(exc),
                    "count": 1,
                    "records": [],
                }],
                "preview": df.head(5).where(pd.notna(df.head(5)), None).to_dict(orient="records"),
            }

        issues: list[dict] = []
        normalized.columns = [str(column) for column in normalized.columns]

        missing_columns = [column for column in required_columns if column not in normalized.columns]
        if missing_columns:
            issues.append({
                "code": "missing_columns",
                "severity": "error",
                "message": "Required columns are missing: " + ", ".join(missing_columns),
                "count": len(missing_columns),
                "columns": missing_columns,
                "records": [],
            })

        # Persist the normalized copy for later workflow stages, without altering the original upload.
        working_path = original_path.parent / "working.csv"
        normalized.to_csv(working_path, index=False)

        # Row-level checks only run when the required column exists.
        if "Date" in normalized.columns:
            parsed_dates = pd.to_datetime(normalized["Date"], errors="coerce")
            bad_dates = parsed_dates.isna()
            if bad_dates.any():
                issues.append({
                    "code": "invalid_dates",
                    "severity": "error",
                    "message": "Date contains missing or invalid values.",
                    "count": int(bad_dates.sum()),
                    "records": _record_numbers(bad_dates),
                })

        if "Product" in normalized.columns:
            blank_products = _blank_mask(normalized["Product"])
            if blank_products.any():
                issues.append({
                    "code": "missing_products",
                    "severity": "error",
                    "message": "Product contains missing or blank values.",
                    "count": int(blank_products.sum()),
                    "records": _record_numbers(blank_products),
                })

        for column, code, label in [
            ("Quantity", "invalid_quantity", "Quantity"),
            ("Unit_Price", "invalid_unit_price", "Unit_Price"),
        ]:
            if column not in normalized.columns:
                continue
            numeric = pd.to_numeric(normalized[column], errors="coerce")
            invalid_numeric = numeric.isna()
            if invalid_numeric.any():
                issues.append({
                    "code": code,
                    "severity": "error",
                    "message": f"{label} contains missing or non-numeric values.",
                    "count": int(invalid_numeric.sum()),
                    "records": _record_numbers(invalid_numeric),
                })
            non_positive = numeric.notna() & numeric.le(0)
            if non_positive.any():
                issues.append({
                    "code": f"non_positive_{column.lower()}",
                    "severity": "error",
                    "message": f"{label} contains zero or negative values.",
                    "count": int(non_positive.sum()),
                    "records": _record_numbers(non_positive),
                })

        empty_rows = normalized.isna().all(axis=1)
        if empty_rows.any():
            issues.append({
                "code": "empty_rows",
                "severity": "warning",
                "message": "Completely empty rows were found.",
                "count": int(empty_rows.sum()),
                "records": _record_numbers(empty_rows),
            })

        duplicate_rows = normalized.duplicated(keep="first")
        if duplicate_rows.any():
            issues.append({
                "code": "duplicate_rows",
                "severity": "warning",
                "message": "Duplicate rows were found. Confirm they are genuine duplicates before removing them.",
                "count": int(duplicate_rows.sum()),
                "records": _record_numbers(duplicate_rows),
            })

        has_errors = any(issue["severity"] == "error" for issue in issues)
        can_clean = not missing_columns
        preview_df = normalized.head(5)
        preview = preview_df.astype(object).where(pd.notna(preview_df), None).to_dict(orient="records")

        return {
            "analysis_id": payload.analysis_id,
            "validation_passed": not has_errors,
            "can_clean": can_clean,
            "total_records": len(normalized),
            "columns": normalized.columns.tolist(),
            "issues": issues,
            "preview": preview,
            "message": (
                "Validation passed. You can continue to cleaning or analysis."
                if not has_errors
                else "Validation found issues. Review them before choosing a cleaning option."
            ),
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to validate this file.") from exc
