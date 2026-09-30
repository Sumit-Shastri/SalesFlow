import pandas as pd

from app.services.cleaner import (
    remove_empty_rows,
    clean_whitespace,
    clean_product_text,
    handle_duplicates,
    handle_missing_values,
    handle_invalid_values,
    convert_datatype,
    standardize_column_order
)

from tests.test_loader import df

print(df)


# ---------------------------------------------------------
# Test 1: remove_empty_rows()
# ---------------------------------------------------------

def test_remove_empty_rows():

    test_df = pd.concat([
        df,
        pd.DataFrame([{
            column: None for column in df.columns
        }])
    ], ignore_index=True)

    result = remove_empty_rows(test_df)

    print(result)

    assert len(result) == len(test_df) - 1


# ---------------------------------------------------------
# Test 2: clean_whitespace()
# ---------------------------------------------------------

def test_clean_whitespace():

    test_df = df.copy()

    # Add whitespace to Product column
    if "Product" in test_df.columns:
        test_df["Product"] = test_df["Product"].astype(str).apply(
            lambda x: "   " + x + "   "
        )

    result = clean_whitespace(test_df)

    print(result)

    if "Product" in result.columns:
        assert all(
            value == value.strip()
            for value in result["Product"]
        )


# ---------------------------------------------------------
# Test 3: clean_product_text()
# ---------------------------------------------------------

def test_clean_product_text():

    test_df = df.copy()

    if "Product" not in test_df.columns:
        return

    test_df.loc[test_df.index[0], "Product"] = "  Apple     iPhone     15  "

    result = clean_product_text(test_df)

    print(result)

    assert result.loc[result.index[0], "Product"] == "Apple iPhone 15"


# ---------------------------------------------------------
# Test 4: handle_duplicates()
# ---------------------------------------------------------

def test_handle_duplicates():

    test_df = pd.concat([df, df], ignore_index=True)

    result = handle_duplicates(test_df)

    print(result)

    assert len(result) == len(df)


# ---------------------------------------------------------
# Test 5: handle_missing_values()
# ---------------------------------------------------------

def test_handle_missing_values():

    test_df = df.copy()

    # Add one row containing a missing value
    test_df.loc[test_df.index[0], test_df.columns[0]] = None

    result = handle_missing_values(test_df)

    print(result)

    assert result.isnull().sum().sum() == 0


# ---------------------------------------------------------
# Test 6: handle_invalid_values()
# ---------------------------------------------------------

def test_handle_invalid_values():

    test_df = df.copy()

    # Create invalid values in first two rows
    test_df.loc[test_df.index[0], "Quantity"] = -5
    test_df.loc[test_df.index[1], "Unit_Price"] = 0

    result = handle_invalid_values(test_df)

    print(result)

    assert (result["Quantity"] > 0).all()
    assert (result["Unit_Price"] > 0).all()


# ---------------------------------------------------------
# Test 7: convert_datatype()
# ---------------------------------------------------------

def test_convert_datatype():

    test_df = df.copy()

    result = convert_datatype(test_df)

    print(result)

    assert result["Unit_Price"].dtype == float
    assert result["Quantity"].dtype == int


# ---------------------------------------------------------
# Test 8: standardize_column_order()
# ---------------------------------------------------------

def test_standardize_column_order():

    test_df = df.copy()

    required_columns = [
        "Date",
        "Product",
        "Quantity",
        "Unit_Price"
    ]

    result = standardize_column_order(
        test_df,
        required_columns
    )


    print(result)

    assert list(result.columns) == required_columns