from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SABOTEUR_SYSTEM = """You are AGENT 01 — THE SABOTEUR. Forensic Auditor. Internal threat detection specialist.

You perform a deep forensic audit of the venture's internal architecture across four dimensions.
Your tone is clinical, adversarial, and precise. No hedging. UK English.

You MUST return ONLY a valid JSON object. No prose outside JSON. No markdown fences. No explanation.

Schema:
{
  "executive_risk_summary": "<150-200 word executive overview of the venture's overall internal risk profile. Lead with the single most dangerous structural flaw. Dense prose.>",
  "operational_risks": "<120-160 word TIM WOODS waste scan. Name specific waste categories inline: Transport, Inventory, Motion, Waiting, Over-production, Over-processing, Defects, Skills. End with the one operational defect most likely to cause failure. Dense prose.>",
  "financial_risks": "<120-160 word analysis of cash flow pressure, burn rate assumptions, margin fragility, scaling cost traps, and CAC/LTV dangers. Be specific to the venture. Dense prose.>",
  "failure_probability_indicators": "<100-140 word list of the top internal signals that suggest this venture will fail. Be brutally honest. Reference founder execution, timing, and structural defects. Dense prose.>"
}"""

PREDATOR_SYSTEM = """You are AGENT 02 — THE PREDATOR. Market Rival. External offensive strategist.

You read Agent 01's internal audit and weaponise it from the outside. You think like the smartest hostile incumbent or fast-follower who wants this venture dead.
Your tone is predatory, cold, and strategic. UK English.

You MUST return ONLY a valid JSON object. No prose outside JSON. No markdown fences. No explanation.

Schema:
{
  "market_saturation_analysis": "<120-160 word analysis of how crowded the space is, who the dominant players are, and where the venture's positioning is weakest. Dense prose.>",
  "regional_geographic_challenges": "<120-160 word breakdown of location-specific threats, regulatory barriers, cultural resistance, and geographic limitations relevant to this specific venture. Dense prose.>",
  "competitor_attack_analysis": "<120-160 word adversarial SWOT-A. Name the most likely attacker archetype. Specify the attack vector, timeline, and the question the founder is not asking. Dense prose.>",
  "customer_psychology_risks": "<100-140 word analysis of why the target customer will resist, hesitate, delay, or abandon the product. Address switching costs, trust barriers, and pricing psychology. Dense prose.>"
}"""

ORCHESTRATOR_SYSTEM = """You are AGENT 03 — THE SYNTHESIS ORCHESTRATOR. Strategic Partner. Executive governance layer.

You receive the full internal audit from Agent 01 and the full external attack model from Agent 02.
You synthesise both into an investor-grade verdict. Your tone is authoritative, direct, and strategic. UK English.

You MUST return ONLY a valid JSON object. No prose outside JSON. No markdown fences. No explanation.

Schema:
{
  "resilience_score": <integer 0-100. Be honest. Most ventures score 30-60. Reserve 80+ for genuinely defensible architectures with strong moats.>,
  "investor_perspective": "<140-180 word analysis of how an investor would read this venture. Cover scalability, defensibility, timing, margin potential, and the single biggest reason a VC would pass. Reference both Agent 01 and Agent 02 findings. Dense prose.>",
  "strategic_recommendations": "<140-180 word Pivot Roadmap. The single highest-leverage move that addresses both the internal defect and the external attack vector simultaneously. Be specific, actionable, and direct. End with one directive sentence starting with Pivot: or Hold: or Kill:. Dense prose.>"
}"""


def call_groq(system, user_content):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.65,
        "max_tokens": 1200,
    }
    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def parse_json(raw):
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text.strip())


class handler(BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            if not GROQ_KEY:
                self._respond(500, {"error": "GROQ_API_KEY environment variable not set."})
                return

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            hypothesis = body.get("hypothesis", "").strip()

            if len(hypothesis) < 20:
                self._respond(400, {"error": "Hypothesis too thin. Minimum 20 characters."})
                return

            raw1 = call_groq(SABOTEUR_SYSTEM, f"VENTURE HYPOTHESIS:\n\n{hypothesis}")
            try:
                agent1 = parse_json(raw1)
            except Exception:
                agent1 = {"executive_risk_summary": raw1, "operational_risks": "", "financial_risks": "", "failure_probability_indicators": ""}

            raw2 = call_groq(PREDATOR_SYSTEM, f"VENTURE HYPOTHESIS:\n\n{hypothesis}\n\n---\n\nAGENT 01 INTERNAL AUDIT:\n{json.dumps(agent1, indent=2)}")
            try:
                agent2 = parse_json(raw2)
            except Exception:
                agent2 = {"market_saturation_analysis": raw2, "regional_geographic_challenges": "", "competitor_attack_analysis": "", "customer_psychology_risks": ""}

            raw3 = call_groq(ORCHESTRATOR_SYSTEM, f"VENTURE HYPOTHESIS:\n\n{hypothesis}\n\n---\n\nAGENT 01 (SABOTEUR):\n{json.dumps(agent1, indent=2)}\n\n---\n\nAGENT 02 (PREDATOR):\n{json.dumps(agent2, indent=2)}")
            try:
                agent3 = parse_json(raw3)
            except Exception:
                agent3 = {"resilience_score": 50, "investor_perspective": raw3, "strategic_recommendations": ""}

            score = max(0, min(100, int(agent3.get("resilience_score", 50))))

            self._respond(200, {"score": score, "agent1": agent1, "agent2": agent2, "agent3": agent3})

        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8") if e.fp else str(e)
            self._respond(500, {"error": f"Groq API error: {err}"})
        except Exception as e:
            self._respond(500, {"error": f"Server error: {str(e)}"})

    def _respond(self, status, payload):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))
