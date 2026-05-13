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
    # Initialize Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # MBA-Level Adversarial Frameworks
    system_instruction = (
        "You are AVA, a ruthless Lead Partner at an activist hedge fund. "
        "Analyze using: 1. TIM WOODS (Lean Wastes) and 2. SWOT Analysis. "
        "Identify structural death-traps and competitive threats. Be adversarial."
    )
    
    user_prompt = (
        f"Perform a forensic audit on this hypothesis: {idea}. \n\n"
        "Structure: \n"
        "### 1. TIM WOODS LEAN AUDIT\n"
        "### 2. STRATEGIC SWOT ANALYSIS\n"
        "### 3. RIVAL PREDATOR ATTACK"
    )

    try:
        # 1. Generate Audit
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        ai_result = completion.choices[0].message.content

        # 2. Save to User's Private History
        # If user_id is provided, the RLS policies in image_2ca9df.jpg will link it.
        data = {
            "user_query": idea,
            "ai_response": ai_result,
            "business_idea_title": idea[:50],
            "user_id": user_id
        }
        
        supabase.table("audits").insert(data).execute()

        return {"result": ai_result}
    except Exception as e:
        return {"result": f"Execution Error: {str(e)}"}
