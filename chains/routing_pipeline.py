# Routes single or batch tasks to a light/heavy LLM by complexity, returns answer and develloper metadata.

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from scoring.complexity_scorer import check_complexity_score

load_dotenv()

SCORE_THRESHOLD = int(os.getenv("SCORE_THRESHOLD", 5))

heavy_model = ChatOpenAI(
    model="openai/gpt-oss-120b",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    openai_api_base="https://api.groq.com/openai/v1",
    temperature=0.7,
)

light_model = ChatOpenAI(
    model="openai/gpt-oss-20b",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    openai_api_base="https://api.groq.com/openai/v1",
    temperature=0.7,
)

str_parser = StrOutputParser()
prompt = PromptTemplate(template="{task}", input_variables=["task"])

# approximate per-1K-token pricing in USD.
HEAVY_COST_PER_1K = 0.0009
LIGHT_COST_PER_1K = 0.0001


def calculate_cost(token_count: int, cost_per_1k: float) -> float:
    """
        Returns cost in USD for token_count tokens at the given per-1K rate.
    """
    return (token_count / 1000) * cost_per_1k


def run_routing_pipeline(task: str) -> dict:
    """
        Scores the task's complexity, routes it to the light or heavy model, and returns the answer with cost metadata.
    """
    scoring_result = check_complexity_score(task)
    score = scoring_result["score"]
    matched_rules = scoring_result["matched_rules"]

    use_heavy = score >= SCORE_THRESHOLD

    if use_heavy:
        chain = prompt | heavy_model | str_parser
        answer = chain.invoke({"task": task})
        model_used = "openai/gpt-oss-120b"
        display_model = "Advanced"

        token_estimate = len(task.split()) + len(answer.split())
        cost_value = calculate_cost(token_estimate, HEAVY_COST_PER_1K)

        dev_metadata = {
            "model_used": model_used,
            "display_model": display_model,
            "complexity_score": score,
            "matched_rules": matched_rules,
            "estimated_cost": f"${cost_value:.6f}",
            "hypothetical_heavy_cost": None,
            "estimated_savings": None,
        }
    else:
        chain = prompt | light_model | str_parser
        answer = chain.invoke({"task": task})
        model_used = "openai/gpt-oss-20b"
        display_model = "Fast"

        token_estimate = len(task.split()) + len(answer.split())
        light_cost_value = calculate_cost(token_estimate, LIGHT_COST_PER_1K)
        heavy_cost_value = calculate_cost(token_estimate, HEAVY_COST_PER_1K)
        savings_value = heavy_cost_value - light_cost_value

        dev_metadata = {
            "model_used": model_used,
            "display_model": display_model,
            "complexity_score": score,
            "matched_rules": matched_rules,
            "estimated_cost": f"${light_cost_value:.6f}",
            "hypothetical_heavy_cost": f"${heavy_cost_value:.6f}",
            "estimated_savings": f"${savings_value:.6f}",
        }

    return {
        "task": task,
        "answer": answer,
        "dev_metadata": dev_metadata,
    }


def run_batch_routing_pipeline(tasks: list[str]) -> list[dict]:
    """
        Runs the routing pipeline on each task in the list and returns their results.
    """
    return [run_routing_pipeline(task) for task in tasks]