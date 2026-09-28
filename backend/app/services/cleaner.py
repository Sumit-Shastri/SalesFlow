#############################################################
#   Imports
#############################################################

import pandas as pd         # Importing the pandas library for data manipulation and analysis 


#############################################################
#   Methods
#############################################################

# 1. remove_empty_rows(df)


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