from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq
from supabase import create_client, Client
import os

app = FastAPI()

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("api/index.html", "r") as f:
        return f.read()

@app.get("/api/audit")
def audit(idea: str = "No idea provided"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # NEW STRATEGIC FRAMEWORK INTEGRATION
    system_instruction = (
        "You are AVA, a ruthless Lead Partner at an activist hedge fund. "
        "Your goal is to destroy weak business logic using two primary frameworks:\n"
        "1. TIM WOODS: Identify Lean Wastes (Transport, Inventory, Motion, Waiting, Over-processing, Over-production, Defects, Skills).\n"
        "2. SWOT Analysis: Provide a high-pressure assessment of Strengths, Weaknesses, Opportunities, and Threats.\n"
        "Be direct, adversarial, and intellectually high-pressure. Avoid fluff."
    )
    
    user_prompt = (
        f"Perform a forensic audit on this hypothesis: {idea}. \n\n"
        "Structure your response exactly as follows:\n"
        "### 1. TIM WOODS LEAN AUDIT (Operational Inefficiencies)\n"
        "### 2. STRATEGIC SWOT ANALYSIS (Competitive Positioning)\n"
        "### 3. RIVAL PREDATOR ATTACK (How a competitor kills this idea)"
    )

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": 'system', "content": system_instruction},
                {"role": 'user', "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        ai_result = completion.choices[0].message.content

        # Log the data to Supabase
        try:
            data = {
                "user_query": idea,
                "ai_response": ai_result,
                "business_idea_title": idea[:50]
            }
            supabase.table("audits").insert(data).execute()
        except Exception as db_error:
            print(f"DB Error: {db_error}")

        return {"result": ai_result}
    except Exception as e:
        return {"result": f"Execution Error: {str(e)}"}
