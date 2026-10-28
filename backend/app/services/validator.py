import pandas as pd

required_columns = [
    "Date",
    "Product",
    "Quantity",
    "Unit_Price"
]

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with commonly named sales columns mapped to canonical names."""

    # copy of original
    df_clean = df.copy()

    # Mapping dictionary to store final renaiming

    rename_mapping = {}

    mapped_targets = set()
    for col in df_clean.columns:
        clean_col = str(col).strip().replace(" ", "").replace("_", "").lower()

        target = None
        if "date" in clean_col:
            target = "Date"

        elif "product" in clean_col or "item" in clean_col:
            target = "Product"

        elif "qty" in clean_col or "quant" in clean_col:
            target = "Quantity"

        elif "price" in clean_col or "rate" in clean_col or "cost" in clean_col:
            target = "Unit_Price"

        if target:
            if target in mapped_targets:
                raise ValueError(
                    f"Multiple columns match '{target}'. Please keep only one matching sales column."
                )
            mapped_targets.add(target)
            rename_mapping[col] = target

    df_clean.rename(columns= rename_mapping, inplace=True)

    return df_clean


def _blank_mask(series: pd.Series) -> pd.Series:
    """Treat nulls and whitespace-only strings as missing values."""
    return series.isna() | series.astype("string").str.strip().eq("").fillna(False)


def _record_numbers(mask: pd.Series, limit: int = 20) -> list[int]:
    """Return 1-based record numbers for a compact, UI-friendly error list."""
    return [int(index) + 1 for index, value in enumerate(mask) if bool(value)][:limit]


def validate_sales_data_with_issues(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Normalize *df* and collect every validation issue without changing the source.

    ``validate_sales_data`` below retains its exception-based public contract for
    older callers. The workflow API uses this helper so the interface can show
    several independent data-quality problems at once.
    """
    if df.empty:
        return df.copy(), [{
            "code": "empty_dataset",
            "severity": "error",
            "message": "The file contains no sales records.",
            "count": 0,
            "records": [],
        }]

    normalized = normalize_column_names(df)
    normalized.columns = [str(column) for column in normalized.columns]
    issues: list[dict] = []

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

    if "Date" in normalized.columns:
        invalid_dates = pd.to_datetime(normalized["Date"], errors="coerce", format="mixed").isna()
        if invalid_dates.any():
            issues.append({
                "code": "invalid_dates",
                "severity": "error",
                "message": "Date contains missing or invalid values.",
                "count": int(invalid_dates.sum()),
                "records": _record_numbers(invalid_dates),
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

    for column, code, label in (
        ("Quantity", "invalid_quantity", "Quantity"),
        ("Unit_Price", "invalid_unit_price", "Unit_Price"),
    ):
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

    return normalized, issues

def validate_sales_data(
                            df,  # type: pd.DataFrame
                        ):

    normalized_df, issues = validate_sales_data_with_issues(df)

    if df.empty:
        raise ValueError("The DataFrame is empty. Please provide a valid sales data file.")
    errors = [issue for issue in issues if issue["severity"] == "error"]
    if errors:
        raise ValueError(errors[0]["message"])

    normalized_df["Date"] = pd.to_datetime(normalized_df["Date"], errors="coerce", format="mixed")
    normalized_df["Quantity"] = pd.to_numeric(normalized_df["Quantity"], errors="coerce")
    normalized_df["Unit_Price"] = pd.to_numeric(normalized_df["Unit_Price"], errors="coerce")
    return normalized_df
