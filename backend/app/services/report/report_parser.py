"""

This Module 'Report' works on the output of analyzer Module.
The plan of report is to create a analyzed specific report and 
generate preview and downloadable pdf file.

Let us divide report in 8 sections :

    Section 1 : Report cover and Information
        - Reporting period
        - Generated on
        - Report Type
        - Data Source
        - Prepared using 
        - company name
        - report title
        - Number of sales record analyzed
        - Data quality notes
    +
    Section 2 : Executive Summary
        - Total revenue
        - Total units sold
        - Number of products
        - overall revenue growth
        - one or two important findings
        - a brief overall performance summary.

        << The AI component can eventually generate the 
        written summary using the verified metrics from your Analyzer.>>

    Section 3 : Overall Sales Performance
        ~ How did the business sell and how did it perform.

        - Total revenue
        - Total Units sold
        - Number of Products
        - Number of Sales Record
        - Average Unit Price

        - visuals : 
            A monthly revenue summary table.
            KPI cards or a compact KPI table.   

    Section 4 : Product Performance analysis

        ~ Which products are contributing most to sales, and which are contributing least?

        - Visuals : 

            1. Revenue by product
            (A bar chart showing which products generate the most revenue.)

            2. Revenue Contribution
            (A table or chart showing each product's share of total revenue.)

            3. Product Ranking
            (A table ranking products by revenue and quantity sold.)

        - Ai Components

    Section 5 : Time and Trend Analysis

        ~ How did sales change over time?

        - Monthly revenue.
        - Monthly units sold.
        - Month-over-month revenue.
        - Month-over-month quantity changes.
        - Highest-revenue month.
        - Lowest-revenue month.

        Visuals : 
            line chart showing monthly revenue
            chart for units sold
        
        - Ai component

    
    Section 6 : Growth Analysis

        ~ Is the business growing or declining, and which products 
          are experiencing the largest changes?

        - overall revenue change
        - average monthly revenue growth
        - overall quantity growth
        - highest growth product
        - lowest growth product

        - Written analysis (Ai component)

    Section 7 : Key Findings and Recommendations

        ~ This section explains their significance and suggests
          what the business owner might investigate next.

        A . Key Findings
        B . Recommendations


    Section 8 : Conclusion

    ~ The report should end with a short summary of 
      the overall performance and the main areas worth
      investigating.

"""

#############################################################
#   Imports
#############################################################

import pandas as pd
from app.services.analyzer import run_full_analysis
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from io import BytesIO

#############################################################
#   Data Definitions
#############################################################

#############################################################
#   Methods
#############################################################

"""
Section 1 : Report cover and Information
    - Reporting period
    - Generated on
    - Report Type
    - Data Source
    - Prepared using 
    - company name
    - report title
    - Number of sales record analyzed
    - Data quality notes
"""

#############################################################
#   Method Name : report_cover()
#   Description : This Method parse's all details needed for 
#                 section 1 -> "Report cover and Information"
#                 and returns it in dictionary format.
#   Parameters  : data -> dictionary
#                 company_name -> string
#                 report_title -> string
#                 file_path -> string
#                 data_quality_notes -> list of string
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 12-10-2026
#############################################################

def report_cover(
                    data,                           # dictionary
                    company_name,                   # string
                    report_title,                   # string
                    file_path,                      # string
                    data_quality_notes              # list of string
                ):
    
    first_date = data["overall_kpis"]["first_date"]
    last_date = data["overall_kpis"]["last_date"]

    reporting_period = f"{first_date} to {last_date}"

    generated_on = datetime.now().strftime("%d %b %Y")

    report_type = "Sales Performance Report"

    data_source = Path(file_path).name

    prepared_using = "SaleFlow v1.0.0"

    number_of_sales_record = data["overall_kpis"]["number_of_sales_records"]

    report_cover = {
        "reporting_period" : reporting_period,
        "generated_on" : generated_on,
        "report_type" : report_type,
        "data_source" : data_source,
        "prepared_using" : prepared_using,
        "company_name" : company_name,
        "report_title" : report_title,
        "number_of_sales_record" : number_of_sales_record,
        "data_quality_notes" : data_quality_notes
    }

    return report_cover



"""
Section 2 : Executive Summary
        - Total revenue
        - Total units sold
        - Number of products
        - overall revenue growth
        - one or two important findings
        - a brief overall performance summary.

        << The AI component can eventually generate the 
        written summary using the verified metrics from your Analyzer.>>
"""

#############################################################
#   Method Name : executive_summary()
#   Description : This Method parse's all details needed for 
#                 section 2 -> "Executive Summary"
#                 and returns it in dictionary format.
#   Parameters  : data -> dictionary
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 14-10-2026
#############################################################

def executive_summary(data):

    total_revenue = data["overall_kpis"]["total_revenue"]

    total_units_sold = data["overall_kpis"]["total_units_sold"]

    number_of_products = data["overall_kpis"]["number_of_products"]

    overall_revenue_growth = data["growth_analysis"]["growth_summary"]["overall_revenue_growth_percentage"]

    return {
        "total_revenue" : total_revenue,
        "total_units_sold" : total_units_sold,
        "number_of_products" : number_of_products,
        "overall_revenue_growth" : overall_revenue_growth
    }


"""
Section 3 : Overall Sales Performance
        ~ How did the business sell and how did it perform.

        - Total revenue
        - Total Units sold
        - Number of Products
        - Number of Sales Record
        - Average Unit Price

        - visuals : 
            A monthly revenue summary table.
            KPI cards or a compact KPI table.  
"""

#############################################################
#   Method Name : overall_sales_performance()
#   Description : This Method parse's all details needed for 
#                 section 3 -> "overall_sales_performance"
#                 and returns it in dictionary format.
#   Parameters  : data -> dictionary
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 14-10-2026
#############################################################

def overall_sales_performance(data):

    total_revenue = data["overall_kpis"]["total_revenue"]

    total_units_sold = data["overall_kpis"]["total_units_sold"]

    number_of_products = data["overall_kpis"]["number_of_products"]

    number_of_sales_records = data["overall_kpis"]["number_of_sales_records"]

    average_selling_price = data["overall_kpis"]["average_revenue_per_record"]

    monthly_revenue_summary = data["time_analysis"]["monthly_analysis"]

    highest_month = max( monthly_revenue_summary, key=lambda month: monthly_revenue_summary[month]["total_revenue"] )
    highest_revenue_month = {
        "month": highest_month,
        "month_in_word": datetime.strptime( highest_month, "%Y-%m" ).strftime("%B"),
        "total_revenue": monthly_revenue_summary[highest_month]["total_revenue"] 
        }

    lowest_month = min( monthly_revenue_summary, key=lambda month: monthly_revenue_summary[month]["total_revenue"] ) 
    lowest_revenue_month = { 
        "month": lowest_month,
        "month_in_word": datetime.strptime( lowest_month, "%Y-%m" ).strftime("%B"),
        "total_revenue": monthly_revenue_summary[lowest_month]["total_revenue"] 
        }

    return {
        "total_revenue" : total_revenue,
        "total_units_sold" : total_units_sold,
        "number_of_products" : number_of_products,
        "number_of_sales_records" : number_of_sales_records,
        "average_selling_price" : average_selling_price,
        "monthly_revenue_summary" : monthly_revenue_summary,
        "highest_revenue_month" : highest_revenue_month,
        "lowest_revenue_month" : lowest_revenue_month
    }


"""
Section 4 : Product Performance analysis

        ~ Which products are contributing most to sales, and which are contributing least?

        - Visuals : 

            1. Revenue by product
            (A bar chart showing which products generate the most revenue.)

            2. Revenue Contribution
            (A table or chart showing each product's share of total revenue.)

            3. Product Ranking
            (A table ranking products by revenue and quantity sold.)

        - Ai Components
"""

#############################################################
#   Method Name : product_performance_analysis()
#   Description : This Method parse's all details needed for 
#                 section 4 -> "product_performance_analysis"
#                 and returns it in dictionary format.
#                 dictionary contaning charts.
#   Parameters  : data -> dictionary
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 17-10-2026
#############################################################

def product_performance_analysis(data):
    # --- Chart 1: Revenue by Product ---
    products_data = data["product_analysis"]
    products = list(products_data.keys())
    revenues = [products_data[p]["total_revenue"] for p in products]
    percentages = [products_data[p]["revenue_contribution_percentage"] for p in products]

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    bars = ax1.barh(products, revenues, color="steelblue")

    for bar, rev, pct in zip(bars, revenues, percentages):
        ax1.text(bar.get_width() + 500, bar.get_y() + bar.get_height()/2,
                 f"₹{rev:,} | {pct:.1f}%", va="center", fontsize=10)

    ax1.set_title("Revenue by Product", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Revenue (₹)")
    plt.tight_layout()

    buffer1 = BytesIO()
    plt.savefig(buffer1, format="png", dpi=300)
    plt.close(fig1)
    buffer1.seek(0)

    # --- Chart 2: Performance Ranking ---
    perf = data["performance_analysis"]

    # Example: revenue ranking chart
    rev_rank_products = [item["Product"] for item in perf["revenue_ranking"]]
    rev_rank_values = [item["Revenue"] for item in perf["revenue_ranking"]]

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bars2 = ax2.bar(rev_rank_products, rev_rank_values, color="darkorange")

    for bar, val in zip(bars2, rev_rank_values):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 500,
                 f"₹{val:,}", ha="center", va="bottom", fontsize=10)

    ax2.set_title("Revenue Ranking", fontsize=14, fontweight="bold")
    ax2.set_ylabel("Revenue (₹)")
    plt.tight_layout()

    buffer2 = BytesIO()
    plt.savefig(buffer2, format="png", dpi=300)
    plt.close(fig2)
    buffer2.seek(0)

    # Return both charts as buffers
    return {
        "revenue_chart": buffer1,
        "performance_chart": buffer2
    }

"""
Section 5 : Time and Trend Analysis

        ~ How did sales change over time?

        - Monthly revenue.
        - Monthly units sold.
        - Month-over-month revenue.
        - Month-over-month quantity changes.
        - Highest-revenue month.
        - Lowest-revenue month.

        Visuals : 
            line chart showing monthly revenue
            chart for units sold
        
        - Ai component
"""

#############################################################
#   Method Name : monthly_performance_analysis()
#   Description : This Method parse's all details needed for 
#                 section 5 -> "monthly_performance_analysis"
#                 and returns it in dictionary format.
#                 dictionary contaning charts.
#   Parameters  : data -> dictionary
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 17-10-2026
#############################################################

def monthly_performance_analysis(data):
    monthly_data = data["time_analysis"]["monthly_analysis"]

    # Extract months and values
    months = list(monthly_data.keys())
    revenues = [monthly_data[m]["total_revenue"] for m in months]
    quantities = [monthly_data[m]["total_quantity"] for m in months]

    # --- Chart 1: Monthly Revenue (Line Chart) ---
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(months, revenues, marker="o", color="steelblue", linewidth=2)

    for x, y in zip(months, revenues):
        ax1.text(x, y + 1000, f"₹{y:,}", ha="center", fontsize=10)

    ax1.set_title("Monthly Revenue", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Revenue (₹)")
    plt.tight_layout()

    buffer1 = BytesIO()
    plt.savefig(buffer1, format="png", dpi=300)
    plt.close(fig1)
    buffer1.seek(0)

    # --- Chart 2: Monthly Units Sold (Bar Chart) ---
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    bars = ax2.bar(months, quantities, color="darkorange")

    for bar, qty in zip(bars, quantities):
        ax2.text(bar.get_x() + bar.get_width()/2, qty + 50,
                 f"{qty:,}", ha="center", va="bottom", fontsize=10)

    ax2.set_title("Monthly Units Sold", fontsize=14, fontweight="bold")
    ax2.set_ylabel("Units Sold")
    plt.tight_layout()

    buffer2 = BytesIO()
    plt.savefig(buffer2, format="png", dpi=300)
    plt.close(fig2)
    buffer2.seek(0)

    comparison_data = data["time_analysis"]["time_comparison"]

    # Convert to DataFrame for easier plotting
    df = pd.DataFrame.from_dict(comparison_data, orient="index")
    df.index.name = "Month Range"
    df.reset_index(inplace=True)

    # --- Create Table Plot ---
    fig3, ax3 = plt.subplots(figsize=(8, 3))
    ax3.axis("off")  # Hide axes

    # Build table
    table = ax3.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    ax3.set_title("Month-over-Month Movement", fontsize=14, fontweight="bold")

    # Save to buffer
    buffer3 = BytesIO()
    plt.savefig(buffer3, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig3)
    buffer3.seek(0)

    daily_revenue_summary = data["time_analysis"]["daily_analysis"]

    highest_day = max( daily_revenue_summary, key=lambda day: daily_revenue_summary[day]["total_revenue"] )
    highest_revenue_day = {
        "day": highest_day,
        "day_in_words": datetime.strptime(highest_day, "%Y-%m-%d").strftime("%A"),
        "total_revenue": daily_revenue_summary[highest_day]["total_revenue"] 
        }

    lowest_day = min( daily_revenue_summary, key=lambda month: daily_revenue_summary[month]["total_revenue"] ) 
    lowest_revenue_day = { 
        "day": lowest_day,
        "day_in_words": datetime.strptime(lowest_day, "%Y-%m-%d").strftime("%A"),
        "total_revenue": daily_revenue_summary[lowest_day]["total_revenue"] 
        }

    # Return both charts
    return {
        "monthly_revenue_chart": buffer1,
        "monthly_units_chart": buffer2,
        "month-over-month-table" : buffer3,
        "highest_revenue_day" : highest_revenue_day,
        "lowest_revenue_day" : lowest_revenue_day
    }

"""
Section 6 : Growth Analysis

        ~ Is the business growing or declining, and which products 
          are experiencing the largest changes?

        - overall revenue change
        - average monthly revenue growth
        - overall quantity growth
        - highest growth product
        - lowest growth product

        - Written analysis (Ai component)
"""

#############################################################
#   Method Name : growth_analysis()
#   Description : This Method parse's all details needed for 
#                 section 6 -> "Growth Analysis"
#                 and returns it in dictionary format.
#                 dictionary conatining data and charts.
#   Parameters  : data -> dictionary
#   Returns     : pandas.DataFrame
#   Author      : Sumit Shastri
#   Date        : 17-10-2026
#############################################################

def growth_analysis(data):

    # LATEST MoM REVENUE GROWTH

    monthly_comparison_data = data["time_analysis"]["time_comparison"]

    raw_date_value = next(reversed(monthly_comparison_data))

    date_str1, date_str2 = raw_date_value.split(" to ")

    date1 = datetime.strptime(date_str1, "%Y-%m")
    prev_month = date1.strftime("%B %Y")

    date2 = datetime.strptime(date_str2, "%Y-%m")
    next_month = date2.strftime("%B %Y")

    revenue_growth_value = monthly_comparison_data[raw_date_value]["revenue_change_percentage"]

    latest_MoM_growth = {
        "latest_MoM_growth_revenue": (
            f"{revenue_growth_value:+.2f}%"
            if revenue_growth_value is not None
            else None
        ),
        "prev_month": prev_month,
        "next_month": next_month
    }

    #REVENUE CHANGE
    revenue_change_data = data["growth_analysis"]["monthly_revenue_growth"]
    r_prev_m, r_next_m = [
    month["revenue"]
    for month in list(revenue_change_data.values())[-2:]
    ]

    revenue_change = r_next_m - r_prev_m

    # QUANTITY GROWTH

    quantity_change_data = data["growth_analysis"]["monthly_quantity_growth"]
    q_prev_m, q_next_m = [
    month["quantity"]
    for month in list(quantity_change_data.values())[-2:]
    ]

    quantity_change = q_next_m - q_prev_m
    quantity_growth_percentage = list(
                    quantity_change_data.values()
                )[-1]["growth_percentage"]

    quantity_growth = {
        "unit_change" : quantity_change,
        "percentage" : quantity_growth_percentage
    }

    # AVG MONTHLY REVENUE GROWTH

    avg_monthly_revenue_growth = data["growth_analysis"]["growth_summary"]["average_monthly_revenue_growth_percentage"]

    # Product Revenue Growth Chart

    product_data = data["time_analysis"]["product_time_analysis"]

    rows = []
    for product, months in product_data.items():
        # Get last two months only
        sorted_months = sorted(months.keys())
        if len(sorted_months) < 2:
            continue  # skip if not enough data

        last_two = sorted_months[-2:]
        prev, curr = last_two[0], last_two[1]

        prev_rev = months[prev]["total_revenue"]
        curr_rev = months[curr]["total_revenue"]
        prev_qty = months[prev]["total_quantity"]
        curr_qty = months[curr]["total_quantity"]

        rev_change = curr_rev - prev_rev
        qty_change = curr_qty - prev_qty

        rev_growth_pct = (rev_change / prev_rev * 100) if prev_rev else 0
        qty_growth_pct = (qty_change / prev_qty * 100) if prev_qty else 0

        rows.append([
            product,
            f"₹{prev_rev:,.2f}",
            f"₹{curr_rev:,.2f}",
            f"{'+' if rev_change>=0 else ''}₹{rev_change:,.2f}",
            f"{rev_growth_pct:+.1f}%",
            f"{qty_growth_pct:+.1f}%"
        ])

    # Build DataFrame
    df = pd.DataFrame(rows, columns=[
        "Product", prev, curr,
        "Revenue change", "Revenue growth", "Unit growth"
    ])

    # --- Create Table Plot ---
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    ax.set_title("Product Revenue Growth (Last 2 Months)", fontsize=14, fontweight="bold")

    # Save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)

    highest_revenue_growth_product = data["growth_analysis"]["growth_summary"]["highest_revenue_growth_product"]
    highest_revenue_growth_rate = data["growth_analysis"]["growth_summary"]["highest_revenue_growth_rate"]

    lowest_revenue_growth_product = data["growth_analysis"]["growth_summary"]["lowest_revenue_growth_product"]
    lowest_revenue_growth_rate = data["growth_analysis"]["growth_summary"]["lowest_revenue_growth_rate"]


    return {
        "latest_MoM_revenue_growth" : latest_MoM_growth,
        "revenue_change" : revenue_change,
        "quantity_growth" : quantity_growth,
        "avg_monthly_revenue_growth" : avg_monthly_revenue_growth,
        "product_revenue_growth_table" : buffer,
        "highest_revenue_growth_product" : highest_revenue_growth_product,
        "highest_revenue_growth_rate" : highest_revenue_growth_rate,
        "lowest_revenue_growth_product" : lowest_revenue_growth_product,
        "lowest_revenue_growth_rate" : lowest_revenue_growth_rate
    }


def run_full_report_parser(data, company_name, report_title, file_path, date_quality_notes):

    return {
        "report_cover" : report_cover(data, company_name, report_title, file_path, date_quality_notes),
        "executive_summary" : executive_summary(data),
        "overall_sales_performance" : overall_sales_performance(data),
        "product_performance_analysis" : product_performance_analysis(data),
        "monthly_performance_analysis" : monthly_performance_analysis(data),
        "growth_analysis" : growth_analysis(data)
    }