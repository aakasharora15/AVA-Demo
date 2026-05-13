import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq
from supabase import create_client, Client

app = FastAPI()

# Configuration from Vercel Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("api/index.html", "r") as f:
        return f.read()

@app.get("/api/audit")
def audit(idea: str = "No idea provided", user_id: str = None):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Proprietary Forensic Instruction Set
    system_instruction = (
        "You are AVA, a ruthless Lead Partner at an activist hedge fund. "
        "Analyze using the WOODS-SWOT Protocol: 1. TIM WOODS (Lean Wastes) and 2. Adversarial SWOT. "
        "Identify structural death-traps and competitive vulnerabilities. Be adversarial and professional."
    )
    
    user_prompt = (
        f"Perform a forensic audit on this hypothesis: {idea}. \n\n"
        "Structure your response exactly as follows: \n"
        "### 1. TIM WOODS OPERATIONAL AUDIT\n"
        "### 2. ADVERSARIAL SWOT ANALYSIS\n"
        "### 3. PREDATOR EXPLOITATION RISK"
    )

    try:
        # 1. Execute Adversarial Reasoning
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6
        )
        ai_result = completion.choices[0].message.content

        # 2. Secure Data Persistence
        if user_id:
            data = {
                "user_query": idea,
                "ai_response": ai_result,
                "business_idea_title": idea[:50],
                "user_id": user_id
            }
            supabase.table("audits").insert(data).execute()

        return {"result": ai_result}
    except Exception as e:
        return {"result": f"Protocol Error: {str(e)}"}
