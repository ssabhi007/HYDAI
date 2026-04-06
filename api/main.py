from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import subprocess
import os
import sys
sys.path.append("E:/HYDAI")

app = FastAPI(title="HYDAI API", version="1.0.0")
# Load LangGraph once at startup
print("Loading LangGraph + RAG system...")
from agents.hydai_langgraph import ask_hydai
print("LangGraph ready.")

# ── CORS (allows React to talk to this API) ────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React Vite port
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "E:/HYDAI/data"

# ── HEALTH CHECK ───────────────────────────────────────
@app.get("/")
def root():
    return {"status": "HYDAI API is running"}

# ── GET ALL COMPLAINTS ─────────────────────────────────
@app.get("/complaints")
def get_complaints():
    df = pd.read_csv(f"{DATA_PATH}/hydai_structured.csv")
    df["issue_category"] = df["issue_category"].str.lower().str.strip()
    df["location"]       = df["location"].str.lower().str.strip()
    df = df.fillna("Unknown")
    return df.to_dict(orient="records")

# ── GET AREA STATS ─────────────────────────────────────
@app.get("/stats/areas")
def get_area_stats():
    df = pd.read_csv(f"{DATA_PATH}/hydai_structured.csv")
    df["location"] = df["location"].str.lower().str.strip()
    counts = df["location"].value_counts().head(10)
    return [{"area": k, "count": int(v)} for k, v in counts.items()]

# ── GET ISSUE STATS ────────────────────────────────────
@app.get("/stats/issues")
def get_issue_stats():
    df = pd.read_csv(f"{DATA_PATH}/hydai_structured.csv")
    df["issue_category"] = df["issue_category"].str.lower().str.strip()
    df["issue_category"] = df["issue_category"].replace({
        "garbage / waste not cleared": "garbage",
        "traffic congestion"         : "traffic",
    })
    counts = df["issue_category"].value_counts()
    return [{"issue": k, "count": int(v)} for k, v in counts.items()]

# ── GET HOTSPOTS ───────────────────────────────────────
@app.get("/stats/hotspots")
def get_hotspots():
    df = pd.read_csv(f"{DATA_PATH}/hydai_structured.csv")
    df["location"]       = df["location"].str.lower().str.strip()
    df["issue_category"] = df["issue_category"].str.lower().str.strip()
    df["issue_category"] = df["issue_category"].replace({
        "garbage / waste not cleared": "garbage",
        "traffic congestion"         : "traffic",
    })
    hotspots = df.groupby(["location","issue_category"]).size()
    hotspots = hotspots[hotspots >= 2].sort_values(ascending=False)
    return [
        {"area": k[0], "issue": k[1], "count": int(v)}
        for k, v in hotspots.items()
    ]

# ── GET URGENT COMPLAINTS ──────────────────────────────
@app.get("/stats/urgent")
def get_urgent():
    df = pd.read_csv(f"{DATA_PATH}/hydai_structured.csv")
    df["severity"]       = df["severity"].str.lower().str.strip()
    df["location"]       = df["location"].str.lower().str.strip()
    df["issue_category"] = df["issue_category"].str.lower().str.strip()
    df["duration_days"]  = pd.to_numeric(df["duration_days"], errors="coerce")
    urgent = df[
        (df["severity"] == "high") &
        (df["duration_days"] > 7)
    ].sort_values("duration_days", ascending=False)
    urgent = urgent.fillna("Unknown")
    return urgent[["location","issue_category",
                   "duration_days","summary"]].to_dict(orient="records")

# ── GET DAILY BRIEFING ─────────────────────────────────
@app.get("/briefing")
def get_briefing():
    path = f"{DATA_PATH}/hydai_daily_briefing.txt"
    if os.path.exists(path):
        with open(path, "r") as f:
            return {"briefing": f.read()}
    return {"briefing": "No briefing generated yet. Run the agents first."}

# ── PIPELINE TRIGGERS (for N8N to call) ───────────────
@app.post("/pipeline/clean")
def run_clean():
    result = subprocess.run(
        ["py", "-3.12", "E:/HYDAI/notebooks/step2_clean.py"],
        capture_output=True, text=True
    )
    return {"status": "done", "output": result.stdout[-500:]}

@app.post("/pipeline/structure")
def run_structure():
    result = subprocess.run(
        ["py", "-3.12", "E:/HYDAI/notebooks/step4_structure.py"],
        capture_output=True, text=True
    )
    return {"status": "done", "output": result.stdout[-500:]}

@app.post("/pipeline/analyse")
def run_analyse():
    result = subprocess.run(
        ["py", "-3.12", "E:/HYDAI/notebooks/step5_analyse.py"],
        capture_output=True, text=True
    )
    return {"status": "done", "output": result.stdout[-500:]}

@app.post("/pipeline/agents")
def run_agents():
    result = subprocess.run(
        ["py", "-3.12", "E:/HYDAI/agents/hydai_crew.py"],
        capture_output=True, text=True
    )
    return {"status": "done", "output": result.stdout[-500:]}
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    reply = ask_hydai(req.message)
    return {"reply": reply}