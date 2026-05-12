@app.get("/api/audit")
def audit(idea: str = "No idea provided"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # This is the "Strategic Partner" prompt logic
    system_instruction = (
        "You are AVA, a ruthless Lead Partner at an activist hedge fund and a Systems Architect. "
        "Your goal is to destroy weak business logic. Do not use generic 'startup fluff' language. "
        "Be direct, adversarial, and intellectually high-pressure."
    )
    
    user_prompt = (
        f"Perform a forensic audit on this hypothesis: {idea}. \n\n"
        "1. Identify 3 'Operational Death-Traps' (Structural or economic failures, not just 'marketing' issues).\n"
        "2. Identify a 'Unit Economic Reality Check' (Where does the money leak?).\n"
        "3. Provide a 'Rival Predator Attack' (As a competitor, how do I engineer a moat-breach to kill this business?)."
    )

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7 # Keeps it creative but focused
        )
        return {"result": completion.choices[0].message.content}
    except Exception as e:
        return {"result": f"Execution Error: {str(e)}"}
