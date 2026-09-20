from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


def load_sales_file(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == ".csv":
        try:
            return pd.read_csv(path)
        except EmptyDataError:
            raise ValueError(
                "The CSV file is completely empty. "
                "Please provide a valid sales data file."
            )

    if path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    raise ValueError("Unsupported file format. Use CSV or Excel.")