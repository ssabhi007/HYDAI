import pandas as pd

# Load the raw dataset
df = pd.read_csv("E:/HYDAI/data/hydai_raw_150.csv")

# ── INSPECTION 1: Basic shape ──────────────────────────
print("=" * 50)
print("SHAPE (rows, columns):")
print(df.shape)

# ── INSPECTION 2: Column names ─────────────────────────
print("\n" + "=" * 50)
print("COLUMN NAMES:")
print(df.columns.tolist())

# ── INSPECTION 3: Data types ───────────────────────────
print("\n" + "=" * 50)
print("DATA TYPES:")
print(df.dtypes)

# ── INSPECTION 4: First 5 rows ─────────────────────────
print("\n" + "=" * 50)
print("FIRST 5 ROWS:")
print(df.head())

# ── INSPECTION 5: Null counts ──────────────────────────
print("\n" + "=" * 50)
print("NULL COUNTS PER COLUMN:")
print(df.isnull().sum())

# ── INSPECTION 6: Empty string counts ─────────────────
print("\n" + "=" * 50)
print("EMPTY STRING COUNTS PER COLUMN:")
for col in df.columns:
    empty = (df[col].astype(str).str.strip() == "").sum()
    print(f"  {col}: {empty}")

# ── INSPECTION 7: Unique values in key columns ─────────
print("\n" + "=" * 50)
print("UNIQUE ISSUE TYPES:")
print(df["issue_type"].value_counts())

print("\n" + "=" * 50)
print("UNIQUE AREAS (top 15):")
print(df["area"].value_counts().head(15))

# ── INSPECTION 8: Suspicious complaint values ──────────
print("\n" + "=" * 50)
print("SUSPICIOUS COMPLAINT VALUES:")
suspicious = df[df["raw_complaint"].astype(str).str.strip().isin(
    ["NULL", "N/A", "NA", "none", "test", "", "nan"]
)]
print(f"Count: {len(suspicious)}")
print(suspicious[["id", "area", "raw_complaint"]].to_string())