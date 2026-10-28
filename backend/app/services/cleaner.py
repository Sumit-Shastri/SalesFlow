#############################################################
#   Imports
#############################################################

import pandas as pd         # Importing the pandas library for data manipulation and analysis 

from app.services.validator import required_columns


#############################################################
#   Methods
#############################################################

# 1. remove_empty_rows(df)
# 2. clean_whitespace(df)
# 3. clean_product_text(df)
# 4. handle_duplicates(df)
# 5. handle_missing_values(df)
# 6. handle_invalid_values(df)
# 7. convert_datatype(df)
# 8. standardize_column_order(df, required_columns)


#############################################################
#   Method Name : remove_empty_rows(df)
#   Description : This method removes any rows from
#                 the DataFrame that are completely 
#                 empty (i.e., all values in the row
#                 are NaN).
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame 
#   Author      : Sumit Shastri
#   Date        : 28-09-2026
#############################################################

def remove_empty_rows(df):

    df = df.dropna(how='all')  # Remove rows where all elements are NaN
    
    return df

#############################################################
#   Method Name : clean_whitespace(df)
#   Description : This method removes leading and trailing 
#                 whitespace from all string values in the 
#                 DataFrame. It ensures that the data is clean
#                 and free from unnecessary spaces that may 
#                 affect analysis or processing.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame 
#                 removed.
#   Author      : Sumit Shastri
#   Date        : 28-09-2026
#############################################################

def clean_whitespace(df):

    string_cols = df.select_dtypes(include=['object', 'string']).columns

    #strip whitespaces from them
    df[string_cols] = df[string_cols].apply(lambda x: x.str.strip())

    return df


#############################################################
#   Method Name : clean_product_text(df)
#   Description : This method cleans product names by replacing
#                 multiple consecutive whitespace characters 
#                 with a single space, ensuring consistent 
#                 formatting while preserving the original 
#                 product name.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 28-09-2026
#############################################################

def clean_product_text(df):

    if 'Product' in df.columns:
        df['Product'] = df['Product'].str.replace(r'\s+', ' ', regex=True).str.strip()
    
    return df

#############################################################
#   Method Name : handle_duplicates(df)
#   Description : This method removes duplicate rows from the 
#                 DataFrame.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 28-09-2026
#############################################################

def handle_duplicates(df):

    df = df.drop_duplicates()

    return df


#############################################################
#   Method Name : handle_missing_values(df)
#   Description : This method handles missing values in the 
#                 DataFrame.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 28-09-2026
#############################################################

def handle_missing_values(df):

    df.dropna(inplace=True)  # Remove rows with any NaN values

    return df

#############################################################
#   Method Name : handle_invalid_values(df)
#   Description : This method handles invalid values in the 
#                 DataFrame.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 30-09-2026
#############################################################

def handle_invalid_values(df):

    if 'Unit_Price' in df.columns:
        df = df[df['Unit_Price'] > 0]

    if 'Quantity' in df.columns:
        df = df[df['Quantity'] > 0]

    return df

#############################################################
#   Method Name : convert_datatype(df)
#   Description : This method converts the data types of columns
#                 in the DataFrame.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 30-09-2026
#############################################################

def convert_datatype(df):

    if 'Unit_Price' in df.columns:
        df['Unit_Price'] = df['Unit_Price'].astype(float)

    if 'Quantity' in df.columns:
        df['Quantity'] = df['Quantity'].astype(int)

    return df


#############################################################
#   Method Name : standardize_column_order(df, required_columns)
#   Description : This method standardizes the order of columns
#                 in the DataFrame.
#   Parameters  : df (pandas.DataFrame), required_columns (list)
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 30-09-2026
#############################################################

def standardize_column_order(df, required_columns):

    # Reorder the columns based on the required_columns list
    df = df[required_columns]

    return df

#############################################################
#   Method Name : sort_date()
#   Description : This method sorts dates in "Date" column
#                 in chronological order.
#   Parameters  : df (pandas.DataFrame), required_columns (list)
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 12-10-2026
#############################################################

def sort_date(df):

    df = df.sort_values(by="Date").reset_index(drop=True)

    return df


def clean_sales_data(
    df: pd.DataFrame,
    *,
    remove_duplicates: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """Apply SalesFlow's existing cleaning steps and describe their effect.

    This is the workflow-level orchestration of the smaller helpers above. It
    deliberately returns a new DataFrame so the uploaded original remains
    available in the analysis session.
    """
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "Automatic cleaning cannot continue because required columns are missing: "
            + ", ".join(missing_columns)
        )

    cleaned = df.copy()
    records_before = len(cleaned)
    empty_before = int(cleaned.isna().all(axis=1).sum())
    cleaned = remove_empty_rows(cleaned)
    empty_removed = records_before - len(cleaned)

    cleaned = clean_whitespace(cleaned)
    cleaned = clean_product_text(cleaned)
    # Empty text is a missing value after whitespace cleanup.
    cleaned["Product"] = cleaned["Product"].replace("", pd.NA)

    duplicates_removed = 0
    if remove_duplicates:
        before_duplicates = len(cleaned)
        cleaned = handle_duplicates(cleaned)
        duplicates_removed = before_duplicates - len(cleaned)

    # Coercion makes malformed values explicit; the existing missing/invalid
    # helpers then make the documented removal decisions.
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce", format="mixed")
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["Unit_Price"] = pd.to_numeric(cleaned["Unit_Price"], errors="coerce")

    before_missing = len(cleaned)
    cleaned = handle_missing_values(cleaned)
    missing_removed = before_missing - len(cleaned)

    before_invalid = len(cleaned)
    cleaned = handle_invalid_values(cleaned)
    invalid_removed = before_invalid - len(cleaned)

    cleaned = convert_datatype(cleaned)
    cleaned = standardize_column_order(cleaned, required_columns)
    cleaned = sort_date(cleaned)

    if cleaned.empty:
        raise ValueError(
            "Automatic cleaning removed every record. Correct the source data and upload it again."
        )

    return cleaned, {
        "records_before": records_before,
        "records_after": len(cleaned),
        "records_removed": records_before - len(cleaned),
        "empty_rows_removed": empty_removed,
        "duplicate_rows_removed": duplicates_removed,
        "missing_or_malformed_rows_removed": missing_removed,
        "non_positive_rows_removed": invalid_removed,
        "operations": [
            "Removed completely empty rows",
            "Trimmed whitespace and standardized product text",
            *( ["Removed duplicate rows"] if remove_duplicates else [] ),
            "Removed records with missing or malformed required values",
            "Removed records with zero or negative quantity or unit price",
            "Converted data types, standardized the required column order, and sorted dates",
        ],
        "note": (
            "Automatic cleaning used SalesFlow's existing rules. "
            "The original uploaded file was not changed."
        ),
    }
