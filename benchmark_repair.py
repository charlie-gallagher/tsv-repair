#!/usr/bin/env python3
"""
Benchmark a repair function from a given Python module against large_file.tsv.
Logs start time, module name, and elapsed time to perf_log.txt.
"""

import argparse
import importlib.util
import sys
import time
from pathlib import Path


PERF_LOG = Path("perf_log.txt")
LARGE_FILE = Path("large_file.tsv")
OUTPUT_FILE = Path("large_file_repaired.tsv")
HEADER = "date_time\tmodule\telapsed_seconds\n"


def load_repair_from_file(module_path: Path):
    """Load the 'repair' function from a Python file."""
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "repair"):
        raise AttributeError(f"Module {module_path} has no 'repair' function")
    return getattr(module, "repair")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark a repair function from a Python module on large_file.tsv"
    )
    parser.add_argument(
        "module",
        type=Path,
        help="Path to the Python file defining a 'repair(input_file, output_file)' function",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=LARGE_FILE,
        help=f"Input TSV file (default: {LARGE_FILE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help=f"Output TSV file (default: {OUTPUT_FILE})",
    )
    args = parser.parse_args()

    if not args.module.exists():
        print(f"Error: Module file not found: {args.module}", file=sys.stderr)
        sys.exit(1)

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        print("Generate it by running: python generate_large_file.py", file=sys.stderr)
        sys.exit(1)

    try:
        repair = load_repair_from_file(args.module)
    except (ImportError, AttributeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure log file exists with header
    if not PERF_LOG.exists():
        PERF_LOG.write_text(HEADER, encoding="utf-8")

    module_name = args.module.stem
    start_wall = time.perf_counter()
    start_dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    repair(str(args.input), str(args.output))
    elapsed = time.perf_counter() - start_wall

    line = f"{start_dt}\t{module_name}\t{elapsed:.6f}\n"
    with open(PERF_LOG, "a", encoding="utf-8") as f:
        f.write(line)

    print(f"Repair completed in {elapsed:.3f}s (module: {module_name})")
    print(f"Logged to {PERF_LOG}")


if __name__ == "__main__":
    main()
