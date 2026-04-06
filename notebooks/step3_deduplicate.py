import pandas as pd
from rapidfuzz import fuzz

# ── LOAD CLEANED DATA ──────────────────────────────────
df = pd.read_csv("E:/HYDAI/data/hydai_cleaned.csv")
print(f"Records before deduplication: {len(df)}")

# ── NEAR-DUPLICATE DETECTION ───────────────────────────
# Compare every complaint against every other complaint
# If similarity > 85% AND same area = near duplicate

duplicates_to_drop = set()

complaints = df["raw_complaint"].tolist()
areas      = df["area"].tolist()
ids        = df["id"].tolist()

print("\nFinding near-duplicates (similarity > 85%, same area)...")
found = []

for i in range(len(complaints)):
    if i in duplicates_to_drop:
        continue
    for j in range(i + 1, len(complaints)):
        if j in duplicates_to_drop:
            continue

        # Only compare if same area
        if areas[i] != areas[j]:
            continue

        score = fuzz.ratio(complaints[i], complaints[j])

        if score > 85:
            duplicates_to_drop.add(j)  # keep i, drop j
            found.append({
                "kept_id"     : ids[i],
                "dropped_id"  : ids[j],
                "area"        : areas[i],
                "similarity"  : score,
                "complaint_1" : complaints[i][:60],
                "complaint_2" : complaints[j][:60],
            })

# ── SHOW WHAT WAS FOUND ────────────────────────────────
print(f"\nNear-duplicates found: {len(found)}")
print("=" * 60)
for f in found:
    print(f"\nSimilarity: {f['similarity']}%  |  Area: {f['area']}")
    print(f"  KEPT   (id {f['kept_id']}): {f['complaint_1']}")
    print(f"  DROPPED(id {f['dropped_id']}): {f['complaint_2']}")

# ── DROP NEAR-DUPLICATES ───────────────────────────────
df_deduped = df.drop(index=list(duplicates_to_drop)).reset_index(drop=True)
print(f"\nRecords after deduplication: {len(df_deduped)}")
print(f"Near-duplicates removed: {len(df) - len(df_deduped)}")

# ── SAVE ──────────────────────────────────────────────
df_deduped.to_csv("E:/HYDAI/data/hydai_cleaned.csv", index=False)
print(f"\nSaved to: E:/HYDAI/data/hydai_cleaned.csv")