#############################################################
#   Imports
#############################################################

import pandas as pd         # Importing the pandas library for data manipulation and analysis 


#############################################################
#   Methods
#############################################################

# 1. remove_empty_rows(df)
# 2. clean_whitespace(df)
# 3. clean_product_text(df)


#############################################################
#   Method Name : remove_empty_rows(df)
#   Description : This method removes any rows from
#                 the DataFrame that are completely 
#                 empty (i.e., all values in the row
#                 are NaN).
#   Parameters  : df (pandas.DataFrame) - The input DataFrame 
#                 from which empty rows will be removed.
#   Returns     : pandas.DataFrame - A new DataFrame with empty
#                 rows removed.
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
#   Parameters  : df (pandas.DataFrame) - The input DataFrame 
#                 from which whitespace will be removed.
#   Returns     : pandas.DataFrame - A new DataFrame with whitespace
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