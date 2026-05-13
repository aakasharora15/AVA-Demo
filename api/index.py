from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq
from supabase import create_client, Client
import os

app = FastAPI()

# 1. Initialize Supabase Client
# These come from the variables you just saved in Vercel
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
    
    system_instruction = (
        "You are AVA, a ruthless Lead Partner at an activist hedge fund. "
        "Your goal is to destroy weak business logic. Be direct, adversarial, and intellectually high-pressure."
    )
    
    user_prompt = (
        f"Perform a forensic audit on this hypothesis: {idea}. \n\n"
        "1. Identify 3 'Operational Death-Traps'.\n"
        "2. Identify a 'Unit Economic Reality Check'.\n"
        "3. Provide a 'Rival Predator Attack'."
    )

    try:
        # 2. Execute AI Audit
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        ai_result = completion.choices[0].message.content

        # 3. Save to Supabase (The Intelligence Hub)
        # We are using a try/except here so the app doesn't crash if the DB is busy
        try:
            data = {
                "user_query": idea,
                "ai_response": ai_result,
                "business_idea_title": idea[:50]
            }
            # This logs the query into your 'audits' table
            supabase.table("audits").insert(data).execute()
        except Exception as db_error:
            print(f"Database Logging Error: {db_error}")

        return {"result": ai_result}
    except Exception as e:
        return {"result": f"Execution Error: {str(e)}"}
