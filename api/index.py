from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from groq import Groq
from supabase import create_client, Client
import os

app = FastAPI()

# Supabase Configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.get("/", response_class=HTMLResponse)
def home():
    with open("api/index.html", "r") as f:
        return f.read()

@app.get("/api/audit")
def audit(idea: str = "No idea provided"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    system_instruction = (
        "You are AVA, a ruthless Lead Partner at an activist hedge fund. "
        "Your goal is to destroy weak business logic. Be direct and adversarial."
    )
    
    user_prompt = (
        f"Perform a forensic audit on this hypothesis: {idea}. \n\n"
        "1. Identify 3 'Operational Death-Traps'.\n"
        "2. Identify a 'Unit Economic Reality Check'.\n"
        "3. Provide a 'Rival Predator Attack'."
    )

    try:
        # 1. Generate the AI Response
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        ai_result = completion.choices[0].message.content

        # 2. Log the data to Supabase
        # Note: For now, we use a placeholder user_id until we add Auth in the next step.
        # Ensure you have an 'audits' table in Supabase.
        data = {
            "user_query": idea,
            "ai_response": ai_result,
            "business_idea_title": idea[:50] # Taking first 50 chars as title
        }
        
        # This will fail if your 'audits' table isn't ready or RLS is too strict.
        # We will refine the 'user_id' once we add login.
        supabase.table("audits").insert(data).execute()

        return {"result": ai_result}
    except Exception as e:
        return {"result": f"Execution Error: {str(e)}"}
