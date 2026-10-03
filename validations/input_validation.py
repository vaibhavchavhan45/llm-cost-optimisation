# Rule-based validation for input task (no LLM call)

def validate_task_input(task: str) -> tuple[bool, str]:
    """
        Checks that the task has enough characters and contains real words or Not.
    """
    task = task.strip()

    if len(task) < 3:
        return False, "Task is too short to process."

    if not any(char.isalpha() for char in task):
        return False, "Task must contain actual words, not just symbols or numbers."

    return True, ""