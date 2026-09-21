import pandas as pd

required_columns = [
    "Date",
    "Product",
    "Quantity",
    "Unit_Price"
]

def normalize_column_names(df):

    # copy of original
    df_clean = df.copy()

    # Mapping dictionary to store final renaiming

    rename_mapping = {}

    counter = 0
    for col in df_clean.columns:
        clean_col = str(col).strip().replace(" ", "").replace("_", "").lower()
    
        if "date" in clean_col:
            if counter > 0:
                raise ValueError("Multiple date columns found. Please ensure there is only one date column in the sales data file.")
            rename_mapping[col] = "Date"
            counter += 1

        elif "product" in clean_col or "item" in clean_col:
            rename_mapping[col] = "Product"
        
        elif "qty" in clean_col or "quant" in clean_col:
            rename_mapping[col] = "Quantity"

        elif "price" in clean_col or "rate" in clean_col or "cost" in clean_col:
            rename_mapping[col] = "Unit_Price"

    df_clean.rename(columns= rename_mapping, inplace=True)

    return df_clean

def validate_sales_data(
                            df,  # type: pd.DataFrame
                        ):

    # Check if DataFrame is empty
    if df.empty:
        raise ValueError("The DataFrame is empty. Please provide a valid sales data file.")
    
    print("Check : DataFrame is not empty.")

    # Normalize
    normalized_df = normalize_column_names(df)

    # Check if required columns exists
    
    missing_columns = []
    for column in required_columns:
        if column not in normalized_df.columns.tolist():
            missing_columns.append(column)
    
    if not missing_columns:
        print("Check : Required columns exists.")
    else:
        raise ValueError("Those Columns are missing : ",missing_columns)    


    # Check if Date values are Valid

    normalized_df['Date'] = pd.to_datetime(normalized_df['Date'], errors='coerce') # errors ='coerce' will convert invalid dates to NaT

    if normalized_df['Date'].isnull().any():
        null_count = normalized_df['Date'].isnull().sum()
        raise ValueError(
                    f"{null_count} missing or invalid date values found in column 'Date'. "
                    "Please provide valid date values."
                        )
    print("Check : Date values are valid.")
    
    # Validate If product column is not empty

    if normalized_df['Product'].isnull().any():
        null_count = normalized_df['Product'].isnull().sum()
        raise ValueError(
                    f"{null_count} missing product values found in column 'Product'. "
                    "Please provide valid product values."
                        )
    print("Check : Product values are valid.")