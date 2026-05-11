from fastapi import FastAPI
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
import os

app = FastAPI()

@app.get("/api/audit")
def audit(idea: str = "No idea provided"):
    # Secure key retrieval
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        return {"result": "Error: GROQ_API_KEY is not set in Vercel Environment Variables."}

    try:
        llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
        
        prompt = f"Audit this business idea: {idea}. Provide 3 flaws and a competitive counter-attack."
        
        response = llm.invoke([
            SystemMessage(content="You are the AVA Strategic Orchestrator."),
            HumanMessage(content=prompt)
        ])
        
        return {"result": response.content}
    except Exception as e:
        return {"result": f"AI Engine Error: {str(e)}"}
