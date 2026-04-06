import os
import pandas as pd
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# ── LOAD ENV ───────────────────────────────────────────
load_dotenv("E:/HYDAI/.env")

# ── CONFIGURE LLM (Groq) ───────────────────────────────
llm = LLM(
    model = "groq/llama-3.3-70b-versatile",
    api_key  = os.getenv("GROQ_API_KEY"),
    temperature = 0.2
)

import time

# ── LOAD DATA FOR AGENTS TO USE ────────────────────────
df_raw        = pd.read_csv("E:/HYDAI/data/hydai_raw_150.csv")
df_cleaned    = pd.read_csv("E:/HYDAI/data/hydai_cleaned.csv")
df_structured = pd.read_csv("E:/HYDAI/data/hydai_structured.csv")

# Normalize
df_structured["issue_category"] = df_structured["issue_category"].str.lower().str.strip()
df_structured["location"]       = df_structured["location"].str.lower().str.strip()
df_structured["severity"]       = df_structured["severity"].str.lower().str.strip()
df_structured["issue_category"] = df_structured["issue_category"].replace({
    "garbage / waste not cleared": "garbage",
    "traffic congestion"         : "traffic",
})
df_structured["location"] = df_structured["location"].replace({
    "chandana nagar": "chandanagar",
    "hayath nagar"  : "hayathnagar",
    "hitec city"    : "hitech city",
})

# ── DATA SUMMARIES FOR AGENT CONTEXT ───────────────────
raw_summary = f"""
Raw dataset: {len(df_raw)} records
Null counts: {df_raw.isnull().sum().to_dict()}
Sample: {df_raw['raw_complaint'].dropna().head(3).tolist()}
"""


cleaning_summary = f"""
Before: {len(df_raw)} records
After: {len(df_cleaned)} records  
Removed: {len(df_raw) - len(df_cleaned)} records
"""

analysis_summary = f"""
Total records: {len(df_structured)}
Top areas: {df_structured['location'].value_counts().head(5).to_dict()}
Issues: {df_structured['issue_category'].value_counts().head(5).to_dict()}
Severity: {df_structured['severity'].value_counts().to_dict()}
Top hotspot: {df_structured.groupby(['location','issue_category']).size().sort_values(ascending=False).head(3).to_dict()}
Most urgent: Nagole traffic 59 days, Nampally traffic 55 days, Vanasthalipuram garbage 50 days
"""
# ══════════════════════════════════════════════════════
# AGENT 1 — DATA INSPECTOR
# ══════════════════════════════════════════════════════
inspector = Agent(
    role = "Senior Data Quality Analyst",
    goal = (
        "Inspect the raw HYDAI dataset and produce a detailed "
        "data quality report listing every problem found."
    ),
    backstory = (
        "You are a meticulous data analyst with 20 years of experience "
        "auditing urban datasets for Indian municipal corporations. "
        "You never miss a data quality issue."
    ),
    llm     = llm,
    verbose = True
)

task_inspect = Task(
    description = f"""
Analyse this raw dataset summary and produce a structured 
data quality report.

RAW DATA SUMMARY:
{raw_summary}

Your report must cover:
1. Total records and columns
2. Missing value problems (which columns, how many)
3. Data consistency issues (mixed case, spelling errors)
4. Suspected duplicate records
5. Junk or invalid records (NULL, test, empty)
6. Overall data quality score out of 10
""",
    expected_output = (
        "A structured data quality report with sections for each "
        "problem type, specific counts, and an overall quality score."
    ),
    agent = inspector
)

# ══════════════════════════════════════════════════════
# AGENT 2 — DATA CLEANER
# ══════════════════════════════════════════════════════
cleaner = Agent(
    role = "Data Engineering Specialist",
    goal = (
        "Review the data quality report and document exactly "
        "what was cleaned and how, producing a cleaning audit log."
    ),
    backstory = (
        "You are a data engineer who has cleaned millions of records "
        "for smart city projects across India. You document every "
        "transformation precisely so it can be reproduced."
    ),
    llm     = llm,
    verbose = True
)

task_clean = Task(
    description = f"""
Based on the data quality report from the inspector, 
document the cleaning actions taken.

CLEANING RESULTS:
{cleaning_summary}

Cleaning steps that were applied:
1. Dropped junk complaints (NULL, N/A, blank, whitespace-only)
2. Dropped records with missing area (can't map without location)
3. Removed emojis from complaint text
4. Lowercased all text fields
5. Fixed extra whitespace
6. Standardized area spellings (kondpur→kondapur etc.)
7. Filled missing values (severity→Unknown, days→0 etc.)
8. Capped outlier days values at 365
9. Removed near-duplicates using fuzzy matching (>85% similarity)

Produce a cleaning audit log that documents:
1. Each cleaning step with before/after counts
2. Which specific issues were fixed
3. What data was lost and why it was acceptable to remove
4. Final data quality score after cleaning
""",
    expected_output = (
        "A detailed cleaning audit log with before/after counts "
        "for each step and justification for removed records."
    ),
    agent   = cleaner,
    context = [task_inspect]
)

# ══════════════════════════════════════════════════════
# AGENT 3 — ANALYSIS AGENT
# ══════════════════════════════════════════════════════
analyst = Agent(
    role = "Urban Intelligence Analyst",
    goal = (
        "Analyse Hyderabad complaint data to identify hotspots, "
        "patterns, and priority areas for municipal action."
    ),
    backstory = (
        "You are an urban data scientist who advises the GHMC "
        "(Greater Hyderabad Municipal Corporation) on where to "
        "deploy resources based on complaint intelligence."
    ),
    llm     = llm,
    verbose = True
)

task_analyse = Task(
    description = f"""
Analyse the structured HYDAI complaint data and produce 
an intelligence report for the GHMC.

ANALYSIS DATA:
{analysis_summary}

Your intelligence report must include:
1. Top 3 most affected areas and why they need attention
2. Most critical issue types across the city
3. Top 5 complaint hotspots (specific area + issue combinations)
4. Most urgent cases requiring immediate action (high severity + long duration)
5. Patterns you notice (e.g. which issues cluster together)
6. Recommended priority zones for municipal action
""",
    expected_output = (
        "A city intelligence report with specific area names, "
        "issue counts, urgency rankings, and actionable recommendations."
    ),
    agent   = analyst,
    context = [task_clean]
)

# ══════════════════════════════════════════════════════
# AGENT 4 — REPORT AGENT
# ══════════════════════════════════════════════════════
reporter = Agent(
    role = "City Intelligence Reporter",
    goal = (
        "Transform the technical analysis into a clear, "
        "actionable briefing document for city officials."
    ),
    backstory = (
        "You write intelligence briefings for the Hyderabad "
        "Commissioner's office. Your reports are concise, "
        "specific, and always lead with the most critical issues."
    ),
    llm     = llm,
    verbose = True
)

task_report = Task(
    description = """
Using the intelligence analysis, write a formal HYDAI 
Daily Briefing Report for Hyderabad city officials.

The report must be structured as:
1. EXECUTIVE SUMMARY (3 sentences max)
2. CRITICAL ALERTS (top 3 issues needing same-day action)
3. HOTSPOT MAP SUMMARY (top 5 area+issue combinations)
4. ISSUE CATEGORY BREAKDOWN (all categories with counts)
5. RECOMMENDED ACTIONS (specific, actionable steps)
6. DATA CONFIDENCE NOTE (quality of underlying data)

Write it as if the Commissioner will read it in the next 
10 minutes and needs to make resource allocation decisions.
""",
    expected_output = (
        "A formal city intelligence briefing document with all "
        "6 sections, specific area names, numbers, and clear "
        "action recommendations."
    ),
    agent   = reporter,
    context = [task_analyse]
)

# ══════════════════════════════════════════════════════
# ASSEMBLE AND RUN THE CREW
# ══════════════════════════════════════════════════════


def wait_between_steps(step):
    time.sleep(30)


crew = Crew(
    agents  = [inspector, cleaner, analyst, reporter],
    tasks   = [task_inspect, task_clean, task_analyse, task_report],
    process = Process.sequential,
    verbose = True
)

print("\n" + "=" * 60)
print("  HYDAI Multi-Agent System Starting...")
print("  4 Agents | 4 Tasks | Sequential Process")
print("=" * 60 + "\n")

result = crew.kickoff()

print("\n" + "=" * 60)
print("  FINAL BRIEFING REPORT")
print("=" * 60)
print(result)

# Save the report
with open("E:/HYDAI/data/hydai_daily_briefing.txt", "w") as f:
    f.write(str(result))
print("\nReport saved to E:/HYDAI/data/hydai_daily_briefing.txt")
