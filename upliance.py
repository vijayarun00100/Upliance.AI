import os
import json
from typing import Dict
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

MODEL_NAME = "gemini-3-flash-preview"


SYSTEM_PROMPT = """
You are an AI Judge for a turn-based game called "Rock–Paper–Scissors Plus".
You are a neutral evaluator, not a player.
You judge user moves written in free-form natural language.
You must strictly follow the rules, handle ambiguity carefully,
track minimal state, and explain every decision.
"""

INSTRUCTION_PROMPT = """
GAME RULES
1. Valid moves:
   - rock
   - paper
   - scissors
   - bomb (usable only once per player per game)

2. bomb beats rock, paper, and scissors.
3. bomb vs bomb results in a draw.
4. Ambiguous or unclear inputs → UNCLEAR.
5. INVALID or UNCLEAR moves waste the turn.
6. Using bomb again after it was already used → INVALID.

JUDGING PIPELINE (STRICT):

Step 1: Intent Understanding
- Infer intended move from user text.
- If intent is metaphorical, vague, or has multiple meanings → UNCLEAR.

Step 2: Validity Check
- Decide VALID / INVALID / UNCLEAR.
- Enforce bomb usage using provided state.

Step 3: Round Resolution
- Compare user move vs bot move.
- Decide:
  User | Bot | Draw | None

Step 4: Explanation
- Clearly explain interpretation, validity, and outcome.

OUTPUT FORMAT (STRICT JSON ONLY):

{
  "round": <number>,
  "user_input": "<raw text>",
  "interpreted_user_move": "<rock | paper | scissors | bomb | null>",
  "bot_move": "<rock | paper | scissors | bomb>",
  "move_status": "<VALID | INVALID | UNCLEAR>",
  "round_winner": "<User | Bot | Draw | None>",
  "explanation": "<clear explanation>",
  "state_update": {
    "user_bomb_used": <true | false>
  }
}

IMPORTANT:
- Do NOT guess intent.
- Do NOT invent rules.
- Do NOT add extra fields.
"""


class AIJudge:
    def __init__(self):
        self.state = {
            "round": 1,
            "user_bomb_used": False
        }

    def judge_round(self, user_input: str, bot_move: str) -> Dict:
        """
        Runs one judging round.
        All logic lives in the prompt.
        """

        full_prompt = f"""
{SYSTEM_PROMPT}

{INSTRUCTION_PROMPT}

CURRENT GAME STATE
Round number: {self.state['round']}
User bomb already used: {self.state['user_bomb_used']}
Bot move: {bot_move}

USER INPUT:
\"{user_input}\"
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            raise RuntimeError("Model did not return valid JSON")

        # Minimal state update
        self.state["round"] += 1
        self.state["user_bomb_used"] = result["state_update"]["user_bomb_used"]

        return result



if __name__ == "__main__":
    judge = AIJudge()

    rounds = [
        ("I choose the nuclear option", "scissors"),  #bomb used !! 
        ("bomb again", "rock"), # bomb again used 
        ("something sharp maybe", "paper")
    ]

    for user_input, bot_move in rounds:
        result = judge.judge_round(user_input, bot_move)
        print(json.dumps(result, indent=2))