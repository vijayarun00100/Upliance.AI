# AI Judge – Rock Paper Scissors Plus

## Overview

This project implements a prompt-driven **AI Judge** for a simple game variant called **Rock–Paper–Scissors Plus**.  
The goal is **not** to build a full game engine, but to design a system where an LLM evaluates user moves written in free-form natural language and produces clear, explainable judgments.

The focus of this assignment is on:
- Prompt design
- Instruction clarity
- Handling ambiguity
- Explainability of decisions

All core game logic lives inside the **prompt**, not in the application code.

---

## What the AI Judge Does

For each round, the system:
1. Reads a user’s move written in natural language
2. Interprets the user’s intent
3. Checks validity against the game rules
4. Resolves the round outcome
5. Explains *why* the decision was made
6. Updates minimal game state (round number, bomb usage)

The AI acts purely as a **judge**, not as a player.

---

## Game Rules (As Enforced by the Prompt)

- Valid moves:
  - rock
  - paper
  - scissors
  - bomb (can only be used once per player per game)
- bomb beats rock, paper, and scissors
- bomb vs bomb results in a draw
- Ambiguous or unclear moves are marked as **UNCLEAR**
- INVALID or UNCLEAR moves waste the turn

---

## Architecture & Design Choices

### Prompt-First Logic

All reasoning and decision-making is handled inside the prompt:
- Intent detection
- Validity checks
- Rule enforcement
- Winner determination
- Explanation generation

The Python code **does not** contain any game logic or hard-coded rules.  
It only passes state to the model and parses structured output.

---

### Separation of Responsibilities

| Component | Responsibility |
|--------|---------------|
| Prompt | Rules, reasoning, explanations |
| AI Judge class | State tracking and orchestration |
| LLM (Gemini) | Interpretation and judgment |
| Code | Minimal glue, no decision logic |

This keeps the system easy to reason about and aligned with real-world LLM usage.

---

## State Management

Only minimal state is stored:
- Current round number
- Whether the user has already used the bomb

This state is passed into the prompt each round so the model can enforce constraints like one-time bomb usage.

No database or external storage is used.

---

## Why This Approach

- Keeps logic transparent and explainable
- Avoids brittle if-else or regex-based parsing
- Makes behavior easy to modify by updating the prompt
- Reflects how LLMs are actually used in judging or moderation systems

---

## Failure Cases Considered

- Ambiguous language (e.g., “something sharp”)
- Metaphorical inputs (e.g., “nuclear option”)
- Multiple interpretations in one input
- Reusing bomb after it has already been used
- Inputs that don’t clearly map to any valid move

In all such cases, the judge prioritizes **correctness over guessing**.

---

## How to Run

1. Install dependencies:
   ```bash
   pip install google-genai
   ```
  
2. Set your Gemini API key:

   ```bash
    export GEMINI_API_KEY="your_api_key_here"
   ```

3. Run the script:

   ```bash
   python ai_judge_rps_plus_gemini.py
   ```
