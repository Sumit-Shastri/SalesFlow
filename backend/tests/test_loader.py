from app.services.loader import load_sales_file  # isort: skip


file_path = "../data/sample_sales.csv"
emptyone = "../data/empyty.csv"
dirty_realworld_mix = "../data/dirty_realworld_mix.csv"
ecommerce_orders_mixed_dates = "../data/ecommerce_orders_mixed_dates.csv"
field_sales_mobile_app = "../data/field_sales_mobile_app.csv"
multi_curency_sales = "../data/multi_curency_sales.csv"
promotions_and_discounts = "../data/promotions_and_discounts.csv"
retail_pos_clean = "../data/retail_pos_clean.csv"

df = load_sales_file(promotions_and_discounts)

print(df)
print()
print("Rows:", len(df))
print("Columns:", list(df.columns))