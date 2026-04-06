import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv

# ── LOAD ───────────────────────────────────────────────
load_dotenv("E:/HYDAI/.env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

df = pd.read_csv("E:/HYDAI/data/hydai_structured.csv")

# Normalize
df["issue_category"] = df["issue_category"].str.lower().str.strip()
df["location"]       = df["location"].str.lower().str.strip()
df["severity"]       = df["severity"].str.lower().str.strip()

df["issue_category"] = df["issue_category"].replace({
    "garbage / waste not cleared": "garbage",
    "traffic congestion"         : "traffic",
})

df["location"] = df["location"].replace({
    "chandana nagar": "chandanagar",
    "hayath nagar"  : "hayathnagar",
    "hitec city"    : "hitech city",
})

# ── BUILD DATA SUMMARY FOR AGENT ───────────────────────
def build_context():
    total         = len(df)
    top_areas     = df["location"].value_counts().head(5).to_dict()
    top_issues    = df["issue_category"].value_counts().head(6).to_dict()
    high_sev      = df[df["severity"] == "high"]["location"].value_counts().head(5).to_dict()
    hotspots      = df.groupby(["location","issue_category"]).size()
    hotspots      = hotspots[hotspots >= 2].sort_values(ascending=False).head(8)
    urgent        = df[(df["severity"] == "high") & (df["duration_days"] > 7)]
    urgent_list   = urgent[["location","issue_category","duration_days","summary"]]\
                    .sort_values("duration_days", ascending=False)\
                    .head(5).to_dict(orient="records")

    context = f"""
You are HYDAI — an AI assistant for urban issue monitoring in Hyderabad, India.
You answer questions based ONLY on the real complaint data provided below.
Be concise, specific, and helpful. Always mention area names and numbers.

=== HYDAI DATA SUMMARY ===

Total complaints: {total}

Top areas by complaint count:
{top_areas}

Issue type distribution:
{top_issues}

Areas with most HIGH severity complaints:
{high_sev}

Hotspots (area + issue with 2+ complaints):
{hotspots.to_string()}

Most urgent issues (high severity + >7 days unresolved):
{urgent_list}
"""
    return context

# ── CHAT LOOP ──────────────────────────────────────────
print("=" * 55)
print("  HYDAI — Hyderabad Urban Issue Intelligence Agent")
print("=" * 55)
print("  Ask me anything about Hyderabad urban complaints.")
print("  Type 'exit' to quit.\n")

system_prompt = build_context()
conversation  = []

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("HYDAI: Goodbye! Stay safe Hyderabad 🙏")
        break

    if not user_input:
        continue

    conversation.append({
        "role"   : "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model    = "llama-3.1-8b-instant",
        messages = [
            {"role": "system", "content": system_prompt},
            *conversation
        ],
        temperature = 0.3,
        max_tokens  = 300,
    )

    reply = response.choices[0].message.content.strip()

    conversation.append({
        "role"   : "assistant",
        "content": reply
    })

    print(f"\nHYDAI: {reply}\n")