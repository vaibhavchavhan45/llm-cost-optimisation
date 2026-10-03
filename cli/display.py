# presentation file for printing the CLI output for single and batch results

import json

DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_single_result(result: dict):
    """
        Prints the answer and dev metadata for a single task, same format as original main.py.
    """
    print(f"\n{BOLD}{DIM}Answer :{RESET}")
    print(result["answer"])

    print(f"\n{DIM}Metadata for Developers :{RESET}")
    print(json.dumps(result["dev_metadata"], indent=2))


def print_batch_results(results: list[dict], light_count: int, heavy_count: int, total_savings: float):
    """
        Prints each task's question, answer, dev metadata, and the session summary, same format as original main.py.
    """
    for i, result in enumerate(results, start=1):
        print(f"\n{BOLD}{DIM}Task {i} Question : {RESET}\n{result['task']}")
        print(f"\n{BOLD}{DIM}Task {i} Answer : {RESET}")
        print(result["answer"])
        print(f"\n{DIM}Task {i} Dev Metadata : {RESET}")
        print(json.dumps(result["dev_metadata"], indent=2))

    print(f"\n{DIM}Session Summary : {RESET}")
    print(f"Fast model used: {light_count} times")
    print(f"Advanced model used: {heavy_count} times")
    print(f"Total estimated savings this session: ${total_savings:.6f}")