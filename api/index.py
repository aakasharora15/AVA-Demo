from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    # This reads the HTML file sitting right next to it in the api folder
    with open("api/index.html", "r") as f:
        return f.read()

@app.get("/api/audit")
def audit(idea: str = "No idea provided"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    prompt = f"Audit this business idea: {idea}. Provide 3 flaws and a competitive counter-attack."
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
