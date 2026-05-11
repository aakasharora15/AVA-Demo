from fastapi import FastAPI
from groq import Groq
import os

app = FastAPI()

@app.get("/api/audit")
def audit(idea: str):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = f"Audit this business idea: {idea}. Provide 3 flaws and a competitive counter-attack."
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are the AVA Strategic Orchestrator."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return {"result": chat_completion.choices[0].message.content}
    except Exception as e:
        return {"result": f"Execution Error: {str(e)}"}
