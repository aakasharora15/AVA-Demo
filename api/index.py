from fastapi import FastAPI
from crewai import Agent, Task, Crew, Process
import os

app = FastAPI()

@app.get("/api/audit")
def audit(idea: str):
    # Backend Configuration
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = os.environ.get("GROQ_API_KEY")
    
    # Define Adversarial Agents
    saboteur = Agent(
        role='Forensic Strategy Auditor',
        goal='Identify lethal flaws in business logic',
        backstory='You are a ruthless VC auditor.',
        verbose=True
    )
    rival = Agent(
        role='Market Rival CEO',
        goal='Plan a counter-attack to crush the startup',
        backstory='You are the market leader protecting your share.',
        verbose=True
    )
    
    # Define Tasks
    t1 = Task(description=f"Audit this idea: {idea}", agent=saboteur, expected_output="3 Fatal Flaws.")
    t2 = Task(description="Plan a competitive counter-attack based on those flaws.", agent=rival, expected_output="A tactical response plan.")
    
    # Execute Orchestration
    crew = Crew(agents=[saboteur, rival], tasks=[t1, t2], process=Process.sequential)
    final_result = crew.kickoff()
    
    return {"result": str(final_result)}
