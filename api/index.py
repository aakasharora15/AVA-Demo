from fastapi import FastAPI
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import os

app = FastAPI()

@app.get("/api/audit")
def audit(idea: str):
    api_key = os.environ.get("GROQ_API_KEY")
    # Using a high-speed versatile model
    llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
    
    # We combine the Auditor and Rival into one orchestrated prompt to save time
    orchestration_prompt = f"""
    AUDIT REQUEST: {idea}
    
    TASK 1: Act as a Ruthless VC Auditor. Identify 3 lethal flaws.
    TASK 2: Act as an Aggressive Market Rival. Plan a 3-step attack based on those flaws.
    
    FORMAT: Start with 'AUDITOR'S FINDINGS' then 'COMPETITIVE ATTACK'.
    """
    
    response = llm.invoke([
        SystemMessage(content="You are the AVA Strategic Orchestrator."),
        HumanMessage(content=orchestration_prompt)
    ])
    
    return {"result": response.content}
