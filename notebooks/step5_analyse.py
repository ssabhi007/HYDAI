import pandas as pd

# ── LOAD STRUCTURED DATA ───────────────────────────────
df = pd.read_csv("E:/HYDAI/data/hydai_structured.csv")
print(f"Total structured records: {len(df)}")

# Normalize issue categories
df["issue_category"] = df["issue_category"].str.lower().str.strip()
df["issue_category"] = df["issue_category"].replace({
    "garbage / waste not cleared": "garbage",
    "traffic congestion"         : "traffic",
    "unknown"                    : "Unknown"
})

# Normalize location names
df["location"] = df["location"].str.lower().str.strip()
df["location"] = df["location"].replace({
    "chandana nagar": "chandanagar",
    "hayath nagar"  : "hayathnagar",
    "hitec city"    : "hitech city",
    "jublie hills"  : "jubilee hills",
})

# ── ANALYSIS 1: Complaints per area ───────────────────
print("\n" + "=" * 50)
print("TOP 10 AREAS BY COMPLAINT COUNT:")
area_counts = df["location"].value_counts().head(10)
print(area_counts.to_string())

# ── ANALYSIS 2: Issue type distribution ───────────────
print("\n" + "=" * 50)
print("ISSUE TYPE DISTRIBUTION:")
issue_counts = df["issue_category"].value_counts()
print(issue_counts.to_string())

# ── ANALYSIS 3: Severity breakdown ────────────────────
print("\n" + "=" * 50)
print("SEVERITY BREAKDOWN:")
severity_counts = df["severity"].value_counts()
print(severity_counts.to_string())

# ── ANALYSIS 4: High severity by area ─────────────────
print("\n" + "=" * 50)
print("HIGH SEVERITY COMPLAINTS BY AREA:")
high_sev = df[df["severity"] == "high"]
print(high_sev["location"].value_counts().head(10).to_string())

# ── ANALYSIS 5: Average duration by issue type ────────
print("\n" + "=" * 50)
print("AVERAGE COMPLAINT DURATION (days) BY ISSUE TYPE:")
avg_duration = df.groupby("issue_category")["duration_days"].mean().round(1)
print(avg_duration.sort_values(ascending=False).to_string())

# ── ANALYSIS 6: Hotspot detection ─────────────────────
print("\n" + "=" * 50)
print("HOTSPOTS (area + issue with 2+ complaints):")
hotspots = df.groupby(["location","issue_category"]).size()
hotspots = hotspots[hotspots >= 2].sort_values(ascending=False)
print(hotspots.to_string())

# ── ANALYSIS 7: Most urgent complaints ────────────────
print("\n" + "=" * 50)
print("MOST URGENT (high severity + duration > 7 days):")
urgent = df[
    (df["severity"] == "high") &
    (df["duration_days"] > 7)
][["location","issue_category","duration_days","summary"]]
print(urgent.sort_values("duration_days", ascending=False).to_string())

# ── SAVE ANALYSIS RESULTS ──────────────────────────────
area_counts.to_csv("E:/HYDAI/data/analysis_area_counts.csv")
issue_counts.to_csv("E:/HYDAI/data/analysis_issue_counts.csv")
hotspots.to_csv("E:/HYDAI/data/analysis_hotspots.csv")
urgent.to_csv("E:/HYDAI/data/analysis_urgent.csv", index=False)

print("\n" + "=" * 50)
print("Analysis saved to E:/HYDAI/data/")
print("Files: analysis_area_counts.csv, analysis_issue_counts.csv")
print("       analysis_hotspots.csv, analysis_urgent.csv")