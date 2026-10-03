# Business logic for the CLI: single task and batch task flows.

from chains.routing_pipeline import run_routing_pipeline, run_batch_routing_pipeline
from validations.input_validation import validate_task_input
from cli.display import print_single_result, print_batch_results


def parse_cost(value):
    """
        Converts a cost value to a float.
    """
    if value is None:
        return 0.0
    return float(value.replace("$", ""))


def run_single():
    """
        Asks the user for a single task, validates it, runs it through the routing pipeline.
        Prints the answer as plain text and dev metadata as JSON.
    """
    task = input("Enter your task : ").strip()

    valid, message = validate_task_input(task)
    while not valid:
        print(message)
        task = input("Enter your task : ").strip()
        valid, message = validate_task_input(task)

    try:
        result = run_routing_pipeline(task)
    except Exception as e:
        print(f"\n Something went wrong : {e}")
        return

    print_single_result(result)


def run_batch():
    """
        Asks the user for up to 10 tasks, runs them through the batch routing pipeline.
        Prints each answer with dev metadata and session summary of model usage and total savings.
    """
    MAX_BATCH_SIZE = 10
    print(f"Enter tasks one by one (max {MAX_BATCH_SIZE}). Type 'done' when finished.")
    tasks = []
    while True:
        if len(tasks) >= MAX_BATCH_SIZE:
            print(f"Reached max batch size of {MAX_BATCH_SIZE}. Processing now.")
            break
        task = input(f"Task {len(tasks) + 1}: ").strip()
        if task.lower() == "done":
            break
        valid, message = validate_task_input(task)
        if not valid:
            print(message)
            continue
        tasks.append(task)

    if not tasks:
        print("No tasks entered.")
        return

    try:
        results = run_batch_routing_pipeline(tasks)
    except Exception as e:
        print(f"\n Something went wrong : {e}")
        return

    light_count = sum(1 for r in results if r["dev_metadata"]["display_model"] == "Fast")
    heavy_count = sum(1 for r in results if r["dev_metadata"]["display_model"] == "Advanced")
    total_savings = sum(parse_cost(r["dev_metadata"].get("estimated_savings")) for r in results)

    print_batch_results(results, light_count, heavy_count, total_savings)