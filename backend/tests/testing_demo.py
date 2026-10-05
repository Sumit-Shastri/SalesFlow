import pandas as pd
import numpy as np

# Parameters
num_rows = 5000   # adjust size as needed
products = ["Laptop", "Phone", "Tablet", "Headphones", "Monitor"]

# Generate random data
dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
data = {
    "Date": np.random.choice(dates, num_rows),
    "Product": np.random.choice(products, num_rows),
    "Quantity": np.random.randint(1, 50, num_rows),
    "Unit_Price": np.random.randint(100, 5000, num_rows)
}

df = pd.DataFrame(data)

#df = pd.read_csv("D:\Projects\SalesFlow\data\clean_csv_data.csv")

df['Revenue'] = df['Quantity'] * df['Unit_Price']


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
        .apply(lambda g: g.set_index("Date")[["total_quantity", "total_revenue", "sales_record"]].to_dict("index"))
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

result = time_comparison(df)
print(result)