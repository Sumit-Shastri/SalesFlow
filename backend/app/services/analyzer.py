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
import numpy as np


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
        sales_records=("Product", "size"),
        revenue_contribution_percentage=(
            "Revenue",
            lambda x: (x.sum() / df["Revenue"].sum()) * 100
        )
    )

    summary["average_selling_price"] = (
        summary["total_revenue"] / summary["total_quantity"]
    )

    return summary.to_dict(orient="index")


'''
# 3. Time analysis

Will divide in groups : "daily_analysis"
                         "monthly_analysis"
                         "product_time_analysis"
                         "time_comparison"
                         "trends"

'''

#############################################################
#   Method Name : daily_analysis(df)
#   Description : This method will calculate the daily analysis.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 03-10-2026
#############################################################

def daily_analysis(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    daily_summary = df.groupby(df["Date"].dt.date).agg(
        total_quantity=("Quantity", "sum"),
        total_revenue=("Revenue", "sum"),
        sales_records=("Product", "size")
    )

    daily_summary["average_selling_price"] = (
        daily_summary["total_revenue"] /
        daily_summary["total_quantity"]
    )

    daily_summary.index = daily_summary.index.astype(str)

    return daily_summary.to_dict(orient="index")


#############################################################
#   Method Name : monthly_analysis(df)
#   Description : This method will calculate the monthly analysis.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 03-10-2026
#############################################################

def monthly_analysis(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    monthly_summary = df.groupby(df["Date"].dt.to_period("M")).agg(
        total_quantity=("Quantity", "sum"),
        total_revenue=("Revenue", "sum"),
        sales_records=("Product", "size")
    )

    monthly_summary["average_selling_price"] = (
        monthly_summary["total_revenue"] /
        monthly_summary["total_quantity"]
    )

    monthly_summary.index = monthly_summary.index.astype(str)

    return monthly_summary.to_dict(orient="index")


#############################################################
#   Method Name : product_time_analysis(df)
#   Description : This method will return monthly quantity and 
#                 revenue for each product.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 03-10-2026
#############################################################

def product_time_analysis(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    product_time_summary = df.groupby(
        ["Product", df["Date"].dt.strftime("%Y-%m")]
    ).agg(
        total_quantity=("Quantity", "sum"),
        total_revenue=("Revenue", "sum"),
        sales_records=("Product", "size")
    )

    # Convert grouped DataFrame to nested dict
    result = (
        product_time_summary
        .reset_index()
        .groupby("Product")
        .apply(lambda g: g.set_index("Date")[["total_quantity", "total_revenue", "sales_records"]].to_dict("index"))
        .to_dict()
    )

    return result


#############################################################
#   Method Name : time_comparison(df)
#   Description : This method compares the current month with
#`                the previous month from the Daataframe and 
#                 returns the comparison in a dictionary format.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 03-10-2026
#############################################################

def time_comparison(df: pd.DataFrame) -> dict:
    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"])

    time_comparison_summary = (
        df.groupby(df["Date"].dt.to_period("M"))
        .agg(
            revenue=("Revenue", "sum"),
            quantity=("Quantity", "sum")
        )
        .sort_index()
    )

    result = {}

    comparison_duos = len(time_comparison_summary) - 1

    for i in range(comparison_duos):
        previous_month = time_comparison_summary.index[i]
        current_month = time_comparison_summary.index[i + 1]

        previous_revenue = time_comparison_summary.loc[
            previous_month, "revenue"
        ]
        current_revenue = time_comparison_summary.loc[
            current_month, "revenue"
        ]

        previous_quantity = time_comparison_summary.loc[
            previous_month, "quantity"
        ]
        current_quantity = time_comparison_summary.loc[
            current_month, "quantity"
        ]

        revenue_change = (
            ((current_revenue - previous_revenue) / previous_revenue) * 100
            if previous_revenue != 0
            else np.nan
        )

        quantity_change = (
            ((current_quantity - previous_quantity) / previous_quantity) * 100
            if previous_quantity != 0
            else np.nan
        )

        result[f"{previous_month} to {current_month}"] = {
            "revenue_change_percentage": revenue_change,
            "quantity_change_percentage": quantity_change
        }

    return result



#############################################################
#   Method Name : trend(df)
#   Description : This method will calculate the trend of 
#                 revenue and quantity over time.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 05-10-2026
#############################################################

def trend(df: pd.DataFrame) -> dict:
    data = time_comparison(df)

    revenue_increases = 0
    revenue_decreases = 0

    quantity_increases = 0
    quantity_decreases = 0

    for comparison in data.values():

        revenue_change = comparison["revenue_change_percentage"]
        quantity_change = comparison["quantity_change_percentage"]

        if not np.isnan(revenue_change):
            if revenue_change > 0:
                revenue_increases += 1
            elif revenue_change < 0:
                revenue_decreases += 1

        if not np.isnan(quantity_change):
            if quantity_change > 0:
                quantity_increases += 1
            elif quantity_change < 0:
                quantity_decreases += 1

    if revenue_increases > revenue_decreases:
        revenue_trend = "Increasing"
    elif revenue_decreases > revenue_increases:
        revenue_trend = "Decreasing"
    else:
        revenue_trend = "Fluctuating"

    if quantity_increases > quantity_decreases:
        quantity_trend = "Increasing"
    elif quantity_decreases > quantity_increases:
        quantity_trend = "Decreasing"
    else:
        quantity_trend = "Fluctuating"

    return {
        "revenue_trend": revenue_trend,
        "quantity_trend": quantity_trend
    }