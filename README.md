# LLM Cost Optimization Router

## Problem
This project builds a system that decides which LLM should handle a given task, based on how complex the task is. Simple tasks are sent to a smaller, cheaper model, and complex tasks are sent to a more powerful, expensive one, so cost is only spent where it's actually needed.


## What It Does
Given a task (a prompt or question), the system:
1. Scores its complexity using a set of rules (no LLM call involved in this decision).
2. Sends it to a light model (cheap, fast) if simple, or a heavy model (expensive, more capable) if complex.
3. Returns the actual answer to the user.
4. Separately returns developer-facing data: which model was used, why (which rules matched), and if the light model was used, how much cost was saved compared to using the heavy model.


## Model
- Heavy model: `openai/gpt-oss-120b`
- Light model: `openai/gpt-oss-20b`
Both accessed via Groq's OpenAI-compatible API (through `langchain-openai`'s `ChatOpenAI` class).


## Why No LLM Call for Choosing the Model
The routing decision (light vs heavy) is made using pure rules, not an LLM call. This is deliberate: the whole point of this project is to save cost, so spending an extra LLM call just to decide which model to use would go against that goal. Rules are free and instant.


## Scoring Rules
Complexity is calculated using 9 rules, split by what they push toward.

Push toward the light model:
1. Simple task override, for example "brief", "one-liner", "short", "summarize". This instantly marks the task as LOW complexity and skips all other checks.
2. Simple question type, for example starts with "what is" or "define".
3. Simple task keywords: convert, translate, list, format, extract, proofread, rewrite, fix, grammar.

Push toward the heavy model:
4. Complex question type, for example starts with "design", "build", "implement", "architect".
5. Technical keywords: architecture, algorithm, database, distributed, concurrency, security, scalability, migration, refactor, optimize, system.
6. Multi-part task detection: multiple tasks joined by "and", "also", "then", or a numbered list.
7. Code-related detection: write a function, debug, fix this code, regex.
8. Vague or open-ended detection: help me with, thoughts on, ideas for.
9. Constraint or edge-case detection: edge case, constraint, trade-off, under load, considering.

Tie-breaker only:
Text length is only used to nudge a borderline score, never as a main factor on its own.

The score is compared against a configurable threshold (default 5). At or above, it goes to the heavy model. Below, it goes to the light model.


## Cost Visibility (Developer-Facing Only)
Every response includes a `dev_metadata` object with:
- `model_used`: the actual model name, for example `openai/gpt-oss-20b`
- `display_model`: a generic label shown in user-facing contexts instead, either "Fast" or "Advanced", so internal model names aren't exposed unnecessarily
- `complexity_score` and `matched_rules`: explains why this routing decision was made
- `estimated_cost`: cost for this request
- `hypothetical_heavy_cost` and `estimated_savings`: only filled in when the light model was used, showing what it would have cost on the heavy model and how much was saved

This data is not shown to end users in the plain text response. It exists purely for developer visibility, either in the CLI printout or the JSON API response, separate from the plain text only endpoints.


## Input Validation
Simple, rule-based checks only, with no LLM call, consistent with the project's own cost-saving principle. Rejects empty input or input with no real words.


## Batch Mode
Both CLI and API accept multiple tasks in one call. Each task is scored and routed independently, with no shared context between them, this isn't a chat feature. Every result includes its task text alongside the answer, so you know which answer belongs to which task.

Batch size is capped at 10 tasks per request to avoid overly large or costly calls. This limit applies on both the API and the CLI.


## Two Ways to Run
- CLI: `main.py` is just the entry point (arg parsing). Actual logic lives in `cli/handlers.py` (single/batch flow, validation loop, pipeline calls), and all terminal output is handled separately in `cli/display.py`. Single task mode by default, or `--batch` for multiple tasks with a session summary showing total requests per model and total estimated savings for that run only, not saved anywhere.
- API (`app.py`): a FastAPI backend with JSON and plain text endpoints for both single and batch tasks. Comes with an interactive `/docs` page (Swagger UI).


## API Endpoints
- POST `/route-task`: single task, returns JSON with `task`, `answer`, `dev_metadata`.
- POST `/route-task/batch`: up to 10 tasks, returns a JSON list of results.
- POST `/route-task/answer-text`: single task, returns plain text answer only.
- POST `/route-task/batch/answer-text`: up to 10 tasks, returns plain text with question and answer per task.

Hitting the base URL returns a JSON message with a direct link to `/docs`.


## Project Structure
llm-cost-optimization/
├── api/
│ ├── router_json_routes.py JSON response endpoints, single and batch
│ └── router_text_routes.py plain text response endpoints, single and batch
├── chains/
│ └── routing_pipeline.py scoring, routing, model call, cost calculation
├── cli/
│ ├── handlers.py CLI business logic, single and batch flow
│ └── display.py CLI output formatting/printing only
├── scoring/
│ └── complexity_scorer.py the 9-rule scoring logic
├── schemas/
│ ├── pipeline_schemas.py response models
│ └── request_schemas.py API request and response models, including batch limit
├── validations/
│ └── input_validation.py rule-based input checks
├── services/
│ └── formatter.py converts structured result to plain text
├── middleware/
│ └── error_handler.py centralized API error handling
├── main.py CLI entry point, arg parsing only
├── app.py FastAPI entry point
├── requirements.txt
├── .env.example
└── .gitignore


## Setup
1. Move into the project folder:
cd llm-cost-optimization

2. Create a virtual environment:
python3 -m venv venv

3. Activate it:
- macOS/Linux: `source venv/bin/activate`
- Windows: `venv\Scripts\activate`

4. Install dependencies:
pip install -r requirements.txt

5. Copy `.env.example` to `.env` and add:
GROQ_API_KEY=your_api_key_here
SCORE_THRESHOLD=5


## Run (CLI)
Single task:
python main.py

Batch mode, up to 10 tasks:
python main.py --batch


## Run (API)
Locally:
uvicorn app:app --reload

Then open `http://127.0.0.1:8000/docs` to test all endpoints interactively.

Live Link:
Open `https://llm-cost-optimisation.onrender.com/docs` to test all endpoints interactively, no local setup needed.

## Sample Request (Single Task)
```json
{
  "task": "Design a scalable backend architecture for a real-time chat application"
}
```

## Sample Response (Single Task)
```json
{
  "task": "Design a scalable backend architecture for a real-time chat application",
  "answer": "...",
  "dev_metadata": {
    "model_used": "openai/gpt-oss-120b",
    "display_model": "Advanced",
    "complexity_score": 7,
    "matched_rules": ["complex_question_type", "technical_keyword"],
    "estimated_cost": "$0.000187",
    "hypothetical_heavy_cost": null,
    "estimated_savings": null
  }
}
```

## Sample Request (Batch, max 10 tasks)
```json
{
  "tasks": [
    "What is REST API?",
    "Design a scalable backend for a chat app"
  ]
}
```


## Future Improvements
- Save cost and usage data in a real database, so a developer can check the total usage for any past day or month. This feature is helpful for high traffic.
- Use Jev (a fast, cheap confidence-scoring model) to help decide routing before falling back to the rules: ask Jev a yes/no question ("can the light model handle this task?"); if it answers yes with confidence at or above 0.9, route to light model directly; otherwise, or if Jev is unavailable, the existing rules decide. If Jev and the rules disagree, the task goes to the third model i.e. medium model.