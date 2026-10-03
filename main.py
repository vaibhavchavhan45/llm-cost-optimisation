# CLI entry point.

import argparse

from cli.handlers import run_single, run_batch


def main():
    """
        Parses CLI args and runs single or batch mode based on the --batch flag.
    """
    parser = argparse.ArgumentParser(description="LLM cost optimization router")
    parser.add_argument("--batch", action="store_true", help="Run in batch mode")
    args = parser.parse_args()

    if args.batch:
        run_batch()
    else:
        run_single()


if __name__ == "__main__":
    main()