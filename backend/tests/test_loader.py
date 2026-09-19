from app.services.loader import load_sales_file  # isort: skip


file_path = "../data/sample_sales.csv"

df = load_sales_file(file_path)

print(df)
print()
print("Rows:", len(df))
print("Columns:", list(df.columns))