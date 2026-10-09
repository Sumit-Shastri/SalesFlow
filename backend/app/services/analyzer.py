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
#`                the previous month from the Dataframe and 
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


#############################################################
#   Method Name : time_analysis(df)
#   Description : This method returns brief summary of time 
#                 analysis which includes daily, monthly, product
#                 time analysis, time comparison and trends.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 05-10-2026
#############################################################

def time_analysis(df: pd.DataFrame) -> dict:
    return {
        "daily_analysis": daily_analysis(df),
        "monthly_analysis": monthly_analysis(df),
        "product_time_analysis": product_time_analysis(df),
        "time_comparison": time_comparison(df),
        "trends": trend(df)
    }

'''
# 4. Performance analysis

Essentials : 
    Revenue Ranking
    Quantity Ranking
    Revenue Contribution Percentage Ranking
    Average Selling Price Ranking
    Highest Revenue Product
    Highest Quantity Product
'''

#############################################################
#   Method Name : revenue_ranking(df)
#   Description : This method returns the revenue ranking of
#                 products in descending order.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : list[dict]
#   Author      : Sumit Shastri
#   Date        : 05-10-2026
#############################################################

def revenue_ranking(df: pd.DataFrame) -> list[dict]:
    revenue_ranking = (
        df.groupby("Product")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return revenue_ranking.to_dict(orient="records")


#############################################################
#   Method Name : quantity_ranking(df)
#   Description : This method returns the quantity ranking of
#                 products in descending order.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : list[dict]
#   Author      : Sumit Shastri
#   Date        : 05-10-2026
#############################################################

def quantity_ranking(df: pd.DataFrame) -> list[dict]:
    quantity_ranking = (
        df.groupby("Product")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return quantity_ranking.to_dict(orient="records")


#############################################################
#   Method Name : revenue_contribution_ranking(df)
#   Description : This method returns the revenue contribution
#                 ranking of products in descending order.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : list[dict]
#   Author      : Sumit Shastri
#   Date        : 05-10-2026
#############################################################

def revenue_contribution_ranking(df: pd.DataFrame) -> list[dict]:
    total_revenue = df["Revenue"].sum()

    revenue_contribution_ranking = (
        df.groupby("Product")["Revenue"]
        .sum()
        .apply(lambda x: (x / total_revenue) * 100)
        .sort_values(ascending=False)
        .reset_index()
    )

    return revenue_contribution_ranking.to_dict(orient="records")


#############################################################
#   Method Name : average_selling_price_ranking(df)
#   Description : This method returns the weighted average 
#                 selling price ranking of products in descending
#                 order.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : list[dict]
#   Author      : Sumit Shastri
#   Date        : 05-10-2026
#############################################################

def average_selling_price_ranking(df: pd.DataFrame) -> list[dict]:
    average_selling_price_ranking = (
        df.groupby("Product")
        .agg(
            total_revenue=("Revenue", "sum"),
            total_quantity=("Quantity", "sum")
        )
    )

    average_selling_price_ranking["average_selling_price"] = (
        average_selling_price_ranking["total_revenue"]
        / average_selling_price_ranking["total_quantity"]
    )

    average_selling_price_ranking = (
        average_selling_price_ranking["average_selling_price"]
        .sort_values(ascending=False)
        .reset_index()
    )

    return average_selling_price_ranking.to_dict(orient="records")


#############################################################
#   Method Name : performance_analysis(df)
#   Description : This method returns brief summary of Performance 
#                 analysis which revenue ranking, quantity ranking,
#                 revenue contribution percentage ranking, average 
#                 selling price ranking, highest revenue product 
#                 and highest quantity product.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 05-10-2026
#############################################################

def performance_analysis(df: pd.DataFrame) -> dict:

    revenue_rank = revenue_ranking(df)
    quantity_rank = quantity_ranking(df)

    highest_revenue_product = revenue_rank[0] if revenue_rank else None
    highest_quantity_product = quantity_rank[0] if quantity_rank else None

    return {
        "revenue_ranking": revenue_rank,
        "quantity_ranking": quantity_rank,
        "revenue_contribution_ranking": revenue_contribution_ranking(df),
        "average_selling_price_ranking": average_selling_price_ranking(df),
        "highest_revenue_product": highest_revenue_product,
        "highest_quantity_product": highest_quantity_product
    }


'''
# 5. Growth analysis

Essentials : 
    Monthly Revenue Growth
    Monthly Quantity Growth
    Monthly product growth
    Growth Summary /
        overall revenue growth percentage
        average monthly revenue growth percentage
        overall quantity growth percentage
        highest revenue growth product
        highest revenue growth rate
        lowest revenue growth product
        lowest revenue growth rate

'''

#############################################################
#   Method Name : monthly_revenue_growth(df)
#   Description : This method calculates the monthly revenue
#                 growth percentage for each month in the DataFrame.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 09-10-2026
#############################################################

def monthly_revenue_growth(df: pd.DataFrame) -> dict:

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    monthly_revenue = (
        df.groupby(df["Date"].dt.to_period("M"))["Revenue"]
        .sum()
        .sort_index()
    )

    monthly_growth = monthly_revenue.pct_change() * 100

    return {
        str(month): {
            "revenue": revenue,
            "growth_percentage": (
                float(growth) if np.isfinite(growth) else None
            )
        }
        for month, revenue, growth in zip(
            monthly_revenue.index,
            monthly_revenue.values,
            monthly_growth.values
        )
    }


#############################################################
#   Method Name : monthly_quantity_growth(df)
#   Description : This method calculates the monthly quantity
#                 growth percentage for each month in the DataFrame.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 09-10-2026
#############################################################

def monthly_quantity_growth(df: pd.DataFrame) -> dict:

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    monthly_quantity = (
        df.groupby(df["Date"].dt.to_period("M"))["Quantity"]
        .sum()
        .sort_index()
    )

    monthly_growth = monthly_quantity.pct_change() * 100

    return {
        str(month): {
            "quantity": quantity,
            "growth_percentage": (
                float(growth) if np.isfinite(growth) else None
            )
        }
        for month, quantity, growth in zip(
            monthly_quantity.index,
            monthly_quantity.values,
            monthly_growth.values
        )
    }


#############################################################
#   Method Name : monthly_product_growth(df)
#   Description : This method calculates the monthly product
#                 revenue , and product growth percentage for 
#                 each product and each month in the DataFrame.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 09-10-2026
#############################################################

def monthly_product_growth(df: pd.DataFrame) -> dict:

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    df["Year_Month"] = df["Date"].dt.to_period("M")

    # Aggregate monthly revenue for each product
    monthly_data = (
        df.groupby(["Product", "Year_Month"])["Revenue"]
        .sum()
        .reset_index()
        .sort_values(by=["Product", "Year_Month"])
    )

    # Calculate growth separately for each product
    monthly_data["Growth_Rate"] = (
        monthly_data.groupby("Product")["Revenue"]
        .pct_change() * 100
    )

    # Replace non-finite growth values with missing values
    monthly_data["Growth_Rate"] = monthly_data["Growth_Rate"].where(
        np.isfinite(monthly_data["Growth_Rate"]),
        np.nan
    )

    # Convert Year_Month to string for the output
    monthly_data["Year_Month"] = monthly_data["Year_Month"].astype(str)

    output_dict = {}

    for product, group in monthly_data.groupby("Product"):

        output_dict[product] = {}

        for _, row in group.iterrows():

            growth = row["Growth_Rate"]

            output_dict[product][row["Year_Month"]] = {
                "revenue": float(row["Revenue"]),
                "growth_percentage": (
                    float(growth) if pd.notna(growth) else None
                )
            }

    return output_dict

#############################################################
#   Method Name : growth_summary(df)
#   Description : This method calculates the overall growth 
#                 summary including overall revenue growth
#                 percentage, overall quantity growth percentage,
#                 highest revenue growth product, highest revenue
#                 growth rate, lowest revenue growth product, and
#                 lowest revenue growth rate.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 09-10-2026
#############################################################

def growth_summary(df: pd.DataFrame) -> dict:
    df = df.copy()

    if df.empty:
        return {
            "overall_revenue_growth_percentage": None,
            "average_monthly_revenue_growth_percentage": None,
            "overall_quantity_growth_percentage": None,
            "highest_revenue_growth_product": None,
            "highest_revenue_growth_rate": None,
            "lowest_revenue_growth_product": None,
            "lowest_revenue_growth_rate": None
        }

    df["Date"] = pd.to_datetime(df["Date"])

    # --------------------------------------------------
    # 1. Prepare a continuous monthly timeline
    # --------------------------------------------------

    df["Year_Month"] = df["Date"].dt.to_period("M")

    all_months = pd.period_range(
        start=df["Year_Month"].min(),
        end=df["Year_Month"].max(),
        freq="M"
    )

    # --------------------------------------------------
    # 2. Monthly revenue and quantity
    # --------------------------------------------------

    monthly_summary = (
        df.groupby("Year_Month")
        .agg(
            revenue=("Revenue", "sum"),
            quantity=("Quantity", "sum")
        )
        .reindex(all_months, fill_value=0)
    )

    # Revenue growth
    monthly_revenue_growth_rates = (
        monthly_summary["revenue"].pct_change() * 100
    )

    valid_revenue_growth = monthly_revenue_growth_rates[
        np.isfinite(monthly_revenue_growth_rates)
    ]

    average_monthly_revenue_growth_percentage = (
        float(valid_revenue_growth.mean())
        if not valid_revenue_growth.empty
        else None
    )

    if len(monthly_summary) >= 2:
        first_revenue = monthly_summary["revenue"].iloc[0]
        last_revenue = monthly_summary["revenue"].iloc[-1]

        overall_revenue_growth_percentage = (
            float((last_revenue - first_revenue) / first_revenue * 100)
            if first_revenue != 0
            else None
        )

        first_quantity = monthly_summary["quantity"].iloc[0]
        last_quantity = monthly_summary["quantity"].iloc[-1]

        overall_quantity_growth_percentage = (
            float((last_quantity - first_quantity) / first_quantity * 100)
            if first_quantity != 0
            else None
        )

    else:
        overall_revenue_growth_percentage = None
        overall_quantity_growth_percentage = None

    # --------------------------------------------------
    # 3. Compare products over the same two months
    # --------------------------------------------------

    if len(all_months) >= 2:

        previous_month = all_months[-2]
        latest_month = all_months[-1]

        product_monthly_revenue = (
            df.groupby(["Product", "Year_Month"])["Revenue"]
            .sum()
            .unstack(fill_value=0)
            .reindex(columns=all_months, fill_value=0)
        )

        previous_revenue = product_monthly_revenue[previous_month]
        latest_revenue = product_monthly_revenue[latest_month]

        # Percentage growth is undefined when previous revenue is zero.
        valid_products = previous_revenue > 0

        product_growth_rates = (
            (latest_revenue[valid_products]
             - previous_revenue[valid_products])
            / previous_revenue[valid_products]
        ) * 100

        product_growth_rates = product_growth_rates[
            np.isfinite(product_growth_rates)
        ]

    else:
        product_growth_rates = pd.Series(dtype=float)

    # --------------------------------------------------
    # 4. Highest and lowest revenue-growth products
    # --------------------------------------------------

    if not product_growth_rates.empty:

        highest_revenue_growth_product = (
            product_growth_rates.idxmax()
        )

        highest_revenue_growth_rate = float(
            product_growth_rates.max()
        )

        lowest_revenue_growth_product = (
            product_growth_rates.idxmin()
        )

        lowest_revenue_growth_rate = float(
            product_growth_rates.min()
        )

    else:
        highest_revenue_growth_product = None
        highest_revenue_growth_rate = None
        lowest_revenue_growth_product = None
        lowest_revenue_growth_rate = None

    # --------------------------------------------------
    # 5. Return summary
    # --------------------------------------------------

    return {
        "overall_revenue_growth_percentage":
            overall_revenue_growth_percentage,

        "average_monthly_revenue_growth_percentage":
            average_monthly_revenue_growth_percentage,

        "overall_quantity_growth_percentage":
            overall_quantity_growth_percentage,

        "highest_revenue_growth_product":
            highest_revenue_growth_product,

        "highest_revenue_growth_rate":
            highest_revenue_growth_rate,

        "lowest_revenue_growth_product":
            lowest_revenue_growth_product,

        "lowest_revenue_growth_rate":
            lowest_revenue_growth_rate
    }

#############################################################
#   Method Name : growth_summary(df)
#   Description : This method returns the overall growth analysis
#                 including monthly revenue growth, monthly 
#                 quantity growth, monthly product growth, 
#                 and a growth summary.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : dict
#   Author      : Sumit Shastri
#   Date        : 09-10-2026
#############################################################

def growth_analysis(df: pd.DataFrame) -> dict:

    return {
        "monthly_revenue_growth": monthly_revenue_growth(df),
        "monthly_quantity_growth": monthly_quantity_growth(df),
        "monthly_product_growth": monthly_product_growth(df),
        "growth_summary": growth_summary(df)
        }   