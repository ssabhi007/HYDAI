import os
import pandas as pd
from dotenv import load_dotenv
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import chromadb
from chromadb.utils import embedding_functions

load_dotenv("E:/HYDAI/.env")

# ── LLM SETUP ──────────────────────────────────────────
llm = ChatGroq(
    model       = "llama-3.1-8b-instant",
    api_key     = os.getenv("GROQ_API_KEY"),
    temperature = 0.2
)

# ── LOAD DATA ──────────────────────────────────────────
df = pd.read_csv("E:/HYDAI/data/hydai_structured.csv")
df["issue_category"] = df["issue_category"].str.lower().str.strip()
df["location"]       = df["location"].str.lower().str.strip()
df["severity"]       = df["severity"].str.lower().str.strip()
df["issue_category"] = df["issue_category"].replace({
    "garbage / waste not cleared": "garbage",
    "traffic congestion"         : "traffic",
})
df = df.fillna("Unknown")

# ── CHROMADB SETUP ─────────────────────────────────────
print("Setting up ChromaDB vector store...")
chroma_client = chromadb.Client()
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name               = "hydai_complaints",
    embedding_function = ef
)

# Add complaints to vector store
docs  = df["summary"].tolist()
ids   = [f"complaint_{i}" for i in range(len(docs))]
metas = df[["location","issue_category","severity","duration_days"]].to_dict(orient="records")

collection.add(documents=docs, ids=ids, metadatas=metas)
print(f"Added {len(docs)} complaints to ChromaDB")

# ── RAG RETRIEVAL ──────────────────────────────────────
def retrieve_relevant(query: str, n: int = 5) -> str:
    results = collection.query(query_texts=[query], n_results=n)
    docs    = results["documents"][0]
    metas   = results["metadatas"][0]
    context = ""
    for doc, meta in zip(docs, metas):
        context += f"- [{meta['location']} | {meta['issue_category']} | {meta['severity']} | {meta['duration_days']} days] {doc}\n"
    return context

# ── GRAPH STATE ────────────────────────────────────────
class HYDAIState(TypedDict):
    query       : str
    context     : str
    intent      : str
    answer      : str
    quality     : str
    retry_count : int

# ── NODE 1: RAG RETRIEVER ──────────────────────────────
def rag_node(state: HYDAIState) -> HYDAIState:
    print(f"\n[RAG] Retrieving relevant complaints for: {state['query']}")
    context = retrieve_relevant(state["query"])
    print(f"[RAG] Found relevant context")
    return {**state, "context": context}

# ── NODE 2: ROUTER ─────────────────────────────────────
def router_node(state: HYDAIState) -> HYDAIState:
    print(f"[ROUTER] Classifying query intent...")
    messages = [
        SystemMessage(content="""Classify this urban complaint query into exactly one category.
Reply with ONLY one word from: garbage, traffic, waterlogging, pothole, streetlight, water_supply, general"""),
        HumanMessage(content=state["query"])
    ]
    intent = llm.invoke(messages).content.strip().lower()
    if intent not in ["garbage","traffic","waterlogging","pothole","streetlight","water_supply"]:
        intent = "general"
    print(f"[ROUTER] Intent: {intent}")
    return {**state, "intent": intent}

# ── NODE 3: SPECIALIST AGENTS ──────────────────────────
SPECIALIST_PROMPTS = {
    "garbage": """You are a waste management specialist for Hyderabad GHMC.
Answer questions about garbage and waste collection issues using the provided complaint data.
Be specific about areas, durations, and urgency. Always recommend actionable steps.""",

    "traffic": """You are a traffic management expert for Hyderabad traffic police.
Answer questions about traffic congestion, signal failures, and road blockages.
Mention specific roads, peak hours, and traffic management solutions.""",

    "waterlogging": """You are a drainage and flood management specialist for Hyderabad.
Answer questions about waterlogging, flooding, and drainage issues.
Reference specific areas, duration of flooding, and infrastructure solutions.""",

    "pothole": """You are a road maintenance engineer for GHMC Hyderabad.
Answer questions about potholes and road damage.
Mention specific roads, accident risks, and repair priority.""",

    "streetlight": """You are an electrical infrastructure specialist for GHMC.
Answer questions about streetlight failures and dark roads.
Focus on safety risks and maintenance schedules.""",

    "water_supply": """You are a water supply engineer for Hyderabad Metro Water.
Answer questions about water supply issues, pipe bursts, and water quality.
Reference specific areas and supply schedules.""",

    "general": """You are HYDAI, an urban intelligence assistant for Hyderabad.
Answer any question about urban issues using the complaint data provided.
Be concise, specific, and always cite area names and numbers."""
}

def specialist_node(state: HYDAIState) -> HYDAIState:
    intent  = state.get("intent", "general")
    prompt  = SPECIALIST_PROMPTS.get(intent, SPECIALIST_PROMPTS["general"])
    print(f"[SPECIALIST:{intent.upper()}] Generating answer...")

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"""
Question: {state['query']}

Relevant complaint data:
{state['context']}

Answer specifically based on this data.
""")
    ]
    answer = llm.invoke(messages).content.strip()
    print(f"[SPECIALIST] Answer generated")
    return {**state, "answer": answer}

# ── NODE 4: VALIDATOR ──────────────────────────────────
def validator_node(state: HYDAIState) -> HYDAIState:
    print(f"[VALIDATOR] Checking answer quality...")
    retry_count = state.get("retry_count", 0)

    messages = [
        SystemMessage(content="""You are a quality checker for urban intelligence reports.
Check if the answer properly addresses the question with specific data.
Reply with ONLY: GOOD or POOR"""),
        HumanMessage(content=f"""
Question: {state['query']}
Answer: {state['answer']}
""")
    ]
    quality = llm.invoke(messages).content.strip().upper()
    if "GOOD" in quality:
        quality = "GOOD"
    else:
        quality = "POOR"

    print(f"[VALIDATOR] Quality: {quality} | Retries: {retry_count}")
    return {**state, "quality": quality, "retry_count": retry_count + 1}

# ── ROUTING LOGIC ──────────────────────────────────────
def should_retry(state: HYDAIState) -> Literal["specialist", "end"]:
    if state["quality"] == "POOR" and state.get("retry_count", 0) < 2:
        print("[VALIDATOR] Poor quality — retrying...")
        return "specialist"
    return "end"

# ── BUILD THE GRAPH ────────────────────────────────────
graph = StateGraph(HYDAIState)

graph.add_node("rag",        rag_node)
graph.add_node("router",     router_node)
graph.add_node("specialist", specialist_node)
graph.add_node("validator",  validator_node)

graph.set_entry_point("rag")
graph.add_edge("rag",        "router")
graph.add_edge("router",     "specialist")
graph.add_edge("specialist", "validator")

graph.add_conditional_edges(
    "validator",
    should_retry,
    {"specialist": "specialist", "end": END}
)

app = graph.compile()
print("\nLangGraph compiled successfully")

# ── RUN THE AGENT ──────────────────────────────────────
def ask_hydai(question: str) -> str:
    result = app.invoke({
        "query"      : question,
        "context"    : "",
        "intent"     : "",
        "answer"     : "",
        "quality"    : "",
        "retry_count": 0
    })
    return result["answer"]

# ── INTERACTIVE CHAT ───────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  HYDAI — LangGraph + RAG Intelligence System")
    print("=" * 55)
    print("  Type 'exit' to quit\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("HYDAI: Goodbye!")
            break
        if not query:
            continue
        print("\nHYDAI: ", end="", flush=True)
        answer = ask_hydai(query)
        print(answer)
        print()