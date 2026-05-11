import streamlit as st
import os
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq

# 1. SETUP
st.set_page_config(page_title="AVA | Strategic Lab", layout="wide")
st.title("🛡️ AVA: Adversarial Venture Architect")

# 2. CLOUD CONFIG (Pulling from Streamlit Secrets)
if "GROQ_API_KEY" in st.secrets:
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
    os.environ["OPENAI_API_KEY"] = st.secrets["GROQ_API_KEY"]

# 3. INTERFACE
user_idea = st.text_area("Drop your business strategy here:", 
                         placeholder="e.g., A hyper-curated book subscription box for C-suite executives...")

if st.button("🚀 Execute War-Game"):
    if not user_idea:
        st.warning("Please enter an idea.")
    else:
        with st.status("Executing Adversarial Simulation...", expanded=True) as status:
            llm = ChatGroq(api_key=os.environ["OPENAI_API_KEY"], model_name="llama-3.3-70b-versatile")
            
            saboteur = Agent(role='Forensic Strategy Auditor', goal='Find flaws', backstory='VC Auditor', llm=llm)
            rival = Agent(role='Market Rival CEO', goal='Crush startup', backstory='Competitor', llm=llm)
            
            t1 = Task(description=f"Audit: {user_idea}", agent=saboteur, expected_output="3 Flaws")
            t2 = Task(description="Counter-attack plan.", agent=rival, expected_output="3 Steps")
            
            crew = Crew(agents=[saboteur, rival], tasks=[t1, t2], process=Process.sequential)
            final_result = crew.kickoff()
            status.update(label="Simulation Complete!", state="complete")
        
        st.success("Strategic Audit Complete")
        st.info(final_result)
