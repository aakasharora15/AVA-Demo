from fastapi import FastAPI
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import os

app = FastAPI()

@app.get("/api/audit")
def audit(idea: str):
    # Config
    api_key = os.environ.get("GROQ_API_KEY")
    llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
    
    # 1. THE AUDITOR PHASE
    auditor_prompt = f"You are a ruthless VC Auditor. Identify 3 lethal flaws in this business idea: {idea}. Be harsh and specific."
    audit_res = llm.invoke([SystemMessage(content="You are a Forensic Strategy Auditor."), HumanMessage(content=auditor_prompt)])
    
    # 2. THE RIVAL PHASE
    rival_prompt = f"Based on these flaws: {audit_res.content}, plan a 3-step competitive counter-attack to crush this startup."
    rival_res = llm.invoke([SystemMessage(content="You are an Aggressive Market Rival."), HumanMessage(content=rival_prompt)])
    
    # Combined Output
    final_output = f"AUDITOR'S FINDINGS:\n{audit_res.content}\n\nREACTION FROM COMPETITION:\n{rival_res.content}"
    return {"result": final_output}
