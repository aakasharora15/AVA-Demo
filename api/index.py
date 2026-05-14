from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
import re

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"

SABOTEUR_SYSTEM = """You are AGENT 01 — THE SABOTEUR. Forensic Auditor. Internal threat detection specialist.

You perform a deep forensic audit of the venture's internal architecture across four dimensions.
Your tone is clinical, adversarial, and precise. No hedging. UK English.

CRITICAL: Return ONLY raw JSON. No markdown. No backticks. No code fences. No preamble. Start your response with { and end with }

Schema:
{
  "executive_risk_summary": "150-200 word executive overview. Lead with the single most dangerous structural flaw. Dense prose.",
  "operational_risks": "120-160 word TIM WOODS waste scan. Name waste categories inline. End with the one defect most likely to cause failure.",
  "financial_risks": "120-160 word analysis of cash flow, burn rate, margin fragility, scaling traps, CAC/LTV dangers.",
  "failure_probability_indicators": "100-140 word brutally honest failure signals. Reference founder execution, timing, structural defects."
}"""

PREDATOR_SYSTEM = """You are AGENT 02 — THE PREDATOR. Market Rival. External offensive strategist.

You weaponise Agent 01's internal audit from the outside. Think like the smartest hostile incumbent who wants this venture dead.
Tone: predatory, cold, strategic. UK English.

CRITICAL: Return ONLY raw JSON. No markdown. No backticks. No code fences. No preamble. Start your response with { and end with }

Schema:
{
  "market_saturation_analysis": "120-160 word analysis of market crowding and positioning weakness.",
  "regional_geographic_challenges": "120-160 word location-specific threats, regulatory barriers, geographic limitations.",
  "competitor_attack_analysis": "120-160 word adversarial SWOT-A. Name attacker archetype, attack vector, timeline, and the question the founder is not asking.",
  "customer_psychology_risks": "100-140 word analysis of why the target customer will resist, hesitate, or abandon."
}"""

ORCHESTRATOR_SYSTEM = """You are AGENT 03 — THE SYNTHESIS ORCHESTRATOR. Strategic Partner. Executive governance layer.

Synthesise Agent 01 and Agent 02 into an investor-grade verdict.
Tone: authoritative, direct, strategic. UK English.

CRITICAL: Return ONLY raw JSON. No markdown. No backticks. No code fences. No preamble. Start your response with { and end with }

Schema:
{
  "resilience_score": <integer 0-100, most ventures score 30-60, reserve 80+ for genuinely defensible architectures>,
  "investor_perspective": "140-180 word investor analysis. Cover scalability, defensibility, timing, margin, single biggest reason a VC would pass.",
  "strategic_recommendations": "140-180 word Pivot Roadmap. Highest-leverage move addressing both internal defect and external attack. End with Pivot: or Hold: or Kill: directive."
}"""


def call_claude(system, user_content):
    payload = {
        "model": MODEL,
        "max_tokens": 1500,
        "system": system,
        "messages": [
            {"role": "user", "content": user_content}
        ]
    }
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["content"][0]["text"]


def parse_json(raw):
    text = raw.strip()
    # Strip markdown fences
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    text = text.strip()
    # Find JSON object
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    return json.loads(text)


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
            if not ANTHROPIC_KEY:
                self._respond(500, {"error": "ANTHROPIC_API_KEY environment variable not set."})
                return

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            hypothesis = body.get("hypothesis", "").strip()

            if len(hypothesis) < 20:
                self._respond(400, {"error": "Hypothesis too thin. Minimum 20 characters."})
                return

            # AGENT 01
            raw1 = call_claude(SABOTEUR_SYSTEM, f"VENTURE HYPOTHESIS:\n\n{hypothesis}")
            try:
                agent1 = parse_json(raw1)
            except Exception:
                agent1 = {
                    "executive_risk_summary": raw1[:500],
                    "operational_risks": "Parse error — raw output received.",
                    "financial_risks": "Parse error — raw output received.",
                    "failure_probability_indicators": "Parse error — raw output received."
                }

            # AGENT 02
            raw2 = call_claude(
                PREDATOR_SYSTEM,
                f"VENTURE HYPOTHESIS:\n\n{hypothesis}\n\n---\n\nAGENT 01 INTERNAL AUDIT:\n{json.dumps(agent1, indent=2)}"
            )
            try:
                agent2 = parse_json(raw2)
            except Exception:
                agent2 = {
                    "market_saturation_analysis": raw2[:500],
                    "regional_geographic_challenges": "Parse error — raw output received.",
                    "competitor_attack_analysis": "Parse error — raw output received.",
                    "customer_psychology_risks": "Parse error — raw output received."
                }

            # AGENT 03
            raw3 = call_claude(
                ORCHESTRATOR_SYSTEM,
                f"VENTURE HYPOTHESIS:\n\n{hypothesis}\n\n---\n\nAGENT 01 (SABOTEUR):\n{json.dumps(agent1, indent=2)}\n\n---\n\nAGENT 02 (PREDATOR):\n{json.dumps(agent2, indent=2)}"
            )
            try:
                agent3 = parse_json(raw3)
            except Exception:
                agent3 = {
                    "resilience_score": 50,
                    "investor_perspective": raw3[:500],
                    "strategic_recommendations": "Parse error — raw output received."
                }

            score = max(0, min(100, int(agent3.get("resilience_score", 50))))

            self._respond(200, {
                "score": score,
                "agent1": agent1,
                "agent2": agent2,
                "agent3": agent3
            })

        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8") if e.fp else str(e)
            self._respond(500, {"error": f"Anthropic API error: {err}"})
        except Exception as e:
            self._respond(500, {"error": f"Server error: {str(e)}"})

    def _respond(self, status, payload):
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))
