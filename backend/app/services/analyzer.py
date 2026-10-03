"""
This modules does the analyzing work.
Responses in JSON format

We will do the analysis work of this version (v 1.0.0) of the project, 
for only 4 columns which are :
    1. Product (product name)
    2. Date (date of the product)
    3. Quantity (quantity of the product)
    4. Unit_Price (unit price of the product)

we divide analysis in categories as follows :
    1. Overall KPI's
    2. Product analysis
    3. Time Analysis
    4. Performance Analysis
    5. Growth Analysis
    6. Best and Worst Analysis
"""

#############################################################
#   Imports
#############################################################

import pandas as pd


#############################################################
#   Methods
#############################################################

#############################################################
#   Method Name : add_revenue_column(df)
#   Description : This method adds a new column 'Revenue' to 
#                 the dataframe which is calculated as
#                 Quantity * Unit_Price.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : df (pandas.DataFrame)
#   Author      : Sumit Shastri
#   Date        : 02-10-2026
#############################################################

def add_revenue_column(df: pd.DataFrame) -> pd.DataFrame:
    df['Revenue'] = df['Quantity'] * df['Unit_Price']
    return df

'''
# 1. Overall KPI's

Essentials : 

    Total Revenue
    Total Units Sold
    Average Unit Price
    Number of Products
    Number of Sales Records
'''

#############################################################
#   Method Name : overall_kpis(df)
#   Description : This method will calculate the overall KPI's.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 01-10-2026
#############################################################

def overall_kpis(df: pd.DataFrame) -> dict:

    # Total Revenue
    total_revenue = (df['Quantity'] * df['Unit_Price']).sum()

    # Total Units Sold
    total_units_sold = df['Quantity'].sum()

    # Average Unit Price
    average_unit_price = df['Unit_Price'].mean()

    # Number of Products
    number_of_products = df['Product'].nunique()

    # Number of Sales Records
    number_of_sales_records = len(df)

    # Average revenue per record
    average_revenue_per_record = total_revenue / number_of_sales_records

    return {
        "total_revenue" : total_revenue,
        "total_units_sold" : total_units_sold,
        "average_unit_price" : average_unit_price,
        "number_of_products" : number_of_products,
        "number_of_sales_records" : number_of_sales_records,
        "average_revenue_per_record" : average_revenue_per_record
    }


'''
# 2. Product analysis

Essentials : 
    total quantity
    total revenue
    average unit price
    sales record 
    revenue contribution percentage

'''

#############################################################
#   Method Name : product_analysis(df)
#   Description : This method will calculate the product analysis.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 03-10-2026
#############################################################

def product_analysis(df: pd.DataFrame) -> dict:

    grouped = df.groupby("Product")

    summary = grouped.agg(
        total_quantity=("Quantity", "sum"),
        total_revenue=("Revenue", "sum"),
        average_unit_price=("Unit_Price", "mean"),
        sales_records=("Product", "size")
    )

    return summary.to_dict(orient="index")