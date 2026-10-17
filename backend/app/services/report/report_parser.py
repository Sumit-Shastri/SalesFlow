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