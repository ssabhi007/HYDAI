import pandas as pd
import re

# ── LOAD ───────────────────────────────────────────────
df = pd.read_csv("E:/HYDAI/data/hydai_raw_150.csv")
print(f"Before cleaning: {len(df)} records")

# ── STEP 1: Drop exact duplicates ─────────────────────
df = df.drop_duplicates()
print(f"After dropping exact duplicates: {len(df)} records")

# ── STEP 2: Drop rows where raw_complaint is useless ──
# First replace fake nulls with real NaN
junk_values = ["null", "n/a", "na", "none", "test", 
               "nan", "N/A", "NULL", "None"]

df["raw_complaint"] = df["raw_complaint"].astype(str).str.strip()
df["raw_complaint"] = df["raw_complaint"].replace(junk_values, pd.NA)

# Drop whitespace-only complaints
df["raw_complaint"] = df["raw_complaint"].apply(
    lambda x: pd.NA if str(x).strip() == "" else x
)

# Drop rows where complaint is still missing
before = len(df)
df = df.dropna(subset=["raw_complaint"])
print(f"After dropping junk complaints: {len(df)} records "
      f"(dropped {before - len(df)})")

# ── STEP 3: Drop rows with no area ────────────────────
before = len(df)
df = df.dropna(subset=["area"])
df = df[df["area"].astype(str).str.strip() != ""]
print(f"After dropping missing areas: {len(df)} records "
      f"(dropped {before - len(df)})")

# ── STEP 4: Remove emojis from raw_complaint ──────────
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002700-\U000027BF"  # dingbats
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub("", str(text)).strip()

df["raw_complaint"] = df["raw_complaint"].apply(remove_emojis)

# ── STEP 5: Normalize text case ───────────────────────
df["area"]          = df["area"].astype(str).str.strip().str.lower()
df["raw_complaint"] = df["raw_complaint"].astype(str).str.strip().str.lower()
df["issue_type"]    = df["issue_type"].astype(str).str.strip()
df["severity"]      = df["severity"].astype(str).str.strip()
df["source"]        = df["source"].astype(str).str.strip()
df["name"]          = df["name"].astype(str).str.strip()

# ── STEP 6: Fix extra whitespace in complaints ─────────
df["raw_complaint"] = df["raw_complaint"].apply(
    lambda x: re.sub(r"\s+", " ", x).strip()
)

# ── STEP 7: Fill missing values ───────────────────────
df["name"]       = df["name"].replace("nan", "Anonymous").fillna("Anonymous")
df["severity"]   = df["severity"].replace("nan", "Unknown").fillna("Unknown")
df["source"]     = df["source"].replace("nan", "Unknown").fillna("Unknown")
df["landmark"]   = df["landmark"].fillna("Not specified")
df["days"]       = df["days"].fillna(0).astype(int)
df["issue_type"] = df["issue_type"].replace("nan", "Unknown").fillna("Unknown")

# ── STEP 8: Standardize area spellings ────────────────
area_map = {
    "kondpur"        : "kondapur",
    "kukatpaly"      : "kukatpally",
    "hi tech city"   : "hitech city",
    "jublee hills"   : "jubilee hills",
    "jublie hills"   : "jubilee hills",
    "medhipatnam"    : "mehdipatnam",
    "lbnagar"        : "lb nagar",
    "tolichoki"      : "tolichowki",
    "dilshuknagar"   : "dilsukhnagar",
    "hayath nagar"   : "hayathnagar",
    "vanastalipuram" : "vanasthalipuram",
    "himayat nagar"  : "himayatnagar",
    "manikoda"       : "manikonda",
}
df["area"] = df["area"].replace(area_map)

# ── STEP 9: Flag suspicious days values ───────────────
df["days_flag"] = df["days"].apply(
    lambda x: "suspicious" if x > 365 else "ok"
)
suspicious_days = df[df["days_flag"] == "suspicious"]
if len(suspicious_days) > 0:
    print(f"\nSuspicious days values (>365):")
    print(suspicious_days[["id", "area", "days"]].to_string())

# ── STEP 10: Reset index and add cleaned timestamp ────
df = df.reset_index(drop=True)
df["cleaned"] = True

# ── SAVE ──────────────────────────────────────────────
df.to_csv("E:/HYDAI/data/hydai_cleaned.csv", index=False)
print(f"\nFinal cleaned records: {len(df)}")
print(f"Saved to: E:/HYDAI/data/hydai_cleaned.csv")

# ── FINAL REPORT ──────────────────────────────────────
print("\n" + "=" * 50)
print("CLEANING SUMMARY")
print("=" * 50)
print(f"Null counts after cleaning:")
print(df.isnull().sum())
print(f"\nTop areas after standardization:")
print(df["area"].value_counts().head(10))
print(f"\nIssue type distribution:")
print(df["issue_type"].value_counts())
# Cap days at 365 — anything above is unreliable
df["days"] = df["days"].apply(lambda x: 365 if x > 365 else x)