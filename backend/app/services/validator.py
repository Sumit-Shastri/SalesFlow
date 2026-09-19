import pandas as pd

required_columns = [
    "Date",
    "Product",
    "Quantity",
    "Unit_Price"
]

def column_name_normalize(df):

    # copy of original
    df_clean = df.copy()

    # Mapping dictionary to store final renaiming

    rename_mapping = {}

    for col in df_clean.columns:
        clean_col = str(col).strip().replace(" ", "").replace("_", "").lower()
    
        if "date" in clean_col:
            rename_mapping[col] = "Date"

        elif "product" in clean_col or "item" in clean_col:
            rename_mapping[col] = "Product"
        
        elif "qty" in clean_col or "quant" in clean_col:
            rename_mapping[col] = "Quantity"

        elif "price" in clean_col or "rate" in clean_col or "cost" in clean_col:
            rename_mapping[col] = "Unit_Price"

    df_clean.rename(columns= rename_mapping, inplace=True)

    return df_clean

def validate_sales_data(df):

    # Normalize
    normalized_df = column_name_normalize(df)

    # Check if DataFrame is empty
    if df.empty:
        raise ValueError("The DataFrame is empty. Please provide a valid sales data file.")

    # Check if required columns exists
    
    missing_columns = []
    for column in required_columns:
        if column not in normalized_df.columns.tolist():
            missing_columns.append(column)
    
    if not missing_columns:
        print("Check : Required columns exists.")
    else:
        raise ValueError("Those Columns are missing : ",missing_columns)    

    