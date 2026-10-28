"""Focused regressions for workflow behavior that is visible in the frontend."""
import json
from io import BytesIO

from starlette.datastructures import UploadFile

from app.api.upload import upload_sales_file
from app.services.validator import validate_sales_data_with_issues


def _complete_immediate(coroutine):
    """Complete an async route that performs no asynchronous I/O after upload parsing."""
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    raise AssertionError("The upload route unexpectedly yielded control.")


def test_messy_upload_preview_is_json_safe():
    """Blank CSV cells must become JSON null rather than Pandas NaN values."""
    csv = (
        b"Date,Product,Unit_Price,Quantity\n"
        b"2026-01-01,Alpha,10,2\n"
        b",Beta,,3\n"
        b"2026-01-03,,20,\n"
    )
    uploaded = _complete_immediate(
        upload_sales_file(
            UploadFile(file=BytesIO(csv), filename="messy_sales_data_2320_rows.csv")
        )
    )

    assert uploaded["preview"][1]["Date"] is None
    assert uploaded["preview"][1]["Unit_Price"] is None
    assert uploaded["preview"][2]["Product"] is None
    json.dumps(uploaded, allow_nan=False)


def test_validator_collects_multiple_independent_issues():
    """The UI receives all independent problems instead of only the first one."""
    import pandas as pd

    data = pd.DataFrame({
        "Date": ["not-a-date", "2026-01-02"],
        "Product": ["", "Valid"],
        "Quantity": ["not-a-number", "2"],
        "Unit_Price": [0, 10],
    })

    _, issues = validate_sales_data_with_issues(data)
    assert {issue["code"] for issue in issues} == {
        "invalid_dates",
        "missing_products",
        "invalid_quantity",
        "non_positive_unit_price",
    }
