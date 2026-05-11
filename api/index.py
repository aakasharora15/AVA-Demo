from fastapi import FastAPI
from groq import Groq
import os

app = FastAPI()

@app.get("/api/audit")
def audit(idea: str = "No idea provided"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Simple, high-speed adversarial prompt
    prompt = f"""
    Act as two distinct personas:
    1. A Ruthless VC Auditor: Find 3 lethal flaws in this idea: {idea}.
    2. A Market Rival CEO: Plan a 3-step attack to crush this startup.
    
    Provide the response in a clean, structured format.
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are the AVA Strategic Orchestrator."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return {"result": completion.choices[0].message.content}
    except Exception as e:
        return {"result": f"Execution Error: {str(e)}"}
