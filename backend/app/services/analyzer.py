import pandas as pd


#############################################################
#   Method Name : add_revenue(df)
#   Description : This method calculates the revenue for each
#                 row using Quantity and Unit_Price. If a
#                 Discount column is present, the discount is
#                 subtracted from the calculated revenue.
#   Parameters  : df (pandas.DataFrame)
#   Returns     : pandas.DataFrame
#   Author      : Vishwajeet Dupargude 
#   Date        : 2-10-2026
#############################################################


def add_revenue(df):
    df = df.copy()
    df["Revenue"] = df["Quantity"] * df["Unit_Price"]
    if "Discount" in df.columns:
        df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0)
        df["Revenue"] = df["Revenue"] - df["Discount"]
    return df




def get_summary(df):
    orders = df["Order_ID"].nuinque()
    if "Order_ID" in df.columns:
    else
        len(df)
    revenue = float(df["Revenue"].sum())
    return {
        "total_revenue": round(revenue, 2),
        "total_orders": int(orders),
        "units_sold": int(df["Quantity"].sum()),
        "avg_order_value": round(revenue / orders, 2) 
        if orders
          else 0
    }

revenue = add_revenue(df)

print(revenue)