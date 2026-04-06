import pandas as pd
import json
import re
import os
from groq import Groq
from dotenv import load_dotenv

# ── LOAD API KEY ───────────────────────────────────────
load_dotenv("E:/HYDAI/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── LOAD CLEANED DATA ──────────────────────────────────
df = pd.read_csv("E:/HYDAI/data/hydai_cleaned.csv")
print(f"Records to structure: {len(df)}")

# ── EXTRACTION FUNCTION ────────────────────────────────
def extract_structure(complaint, area, issue_type):
    prompt = f"""
You are a data extraction assistant for an urban issue monitoring system in Hyderabad, India.

Extract structured information from this complaint and return ONLY valid JSON.
No explanation. No markdown. Just the JSON object.

Complaint: "{complaint}"
Known area: "{area}"
Known issue type: "{issue_type}"

Return this exact JSON structure:
{{
  "location": "standardized area name in Hyderabad",
  "issue_category": "one of: garbage, traffic, waterlogging, pothole, streetlight, water_supply, other",
  "severity": "one of: low, medium, high",
  "duration_days": <number or null if not mentioned>,
  "landmark": "specific landmark if mentioned or null",
  "summary": "one clean sentence describing the issue"
}}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=200,
        )
        raw = response.choices[0].message.content.strip()

        # Clean any accidental markdown
        raw = re.sub(r"```json|```", "", raw).strip()

        # Sometimes model adds extra text — find JSON object within response
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw)

    except Exception as e:
        print(f"  Error on complaint: {complaint[:40]} → {e}")
        return {
            "location"      : area,
            "issue_category": "unknown",
            "severity"      : "unknown",
            "duration_days" : None,
            "landmark"      : None,
            "summary"       : complaint[:100]
        }

# ── RUN EXTRACTION ON ALL RECORDS ─────────────────────
results = []
for idx, row in df.iterrows():
    print(f"Processing {idx+1}/{len(df)} — {row['area']}...")

    structured = extract_structure(
        complaint  = row["raw_complaint"],
        area       = row["area"],
        issue_type = row["issue_type"]
    )

    # Merge original row with extracted fields
    results.append({
        "id"              : row["id"],
        "original_area"   : row["area"],
        "issue_type_raw"  : row["issue_type"],
        "raw_complaint"   : row["raw_complaint"],
        "days_reported"   : row["days"],
        "source"          : row["source"],
        "location"        : structured.get("location"),
        "issue_category"  : structured.get("issue_category"),
        "severity"        : structured.get("severity"),
        "duration_days"   : structured.get("duration_days"),
        "landmark"        : structured.get("landmark"),
        "summary"         : structured.get("summary"),
    })

# ── SAVE STRUCTURED DATA ───────────────────────────────
df_structured = pd.DataFrame(results)
df_structured.to_csv("E:/HYDAI/data/hydai_structured.csv", index=False)

print(f"\nDone. Structured records: {len(df_structured)}")
print(f"Saved to: E:/HYDAI/data/hydai_structured.csv")

# ── PREVIEW ────────────────────────────────────────────
print("\n── SAMPLE OUTPUT ──────────────────────────────")
print(df_structured[["location","issue_category",
                      "severity","duration_days",
                      "summary"]].head(10).to_string())