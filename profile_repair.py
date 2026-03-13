#!/usr/bin/env python3
"""
Profile a repair function from a given Python module against large_file.tsv.
Uses cProfile and pstats to print a report of hotspots.
"""

import argparse
import cProfile
import importlib.util
import pstats
import sys
from pathlib import Path


LARGE_FILE = Path("large_file.tsv")
OUTPUT_FILE = Path("large_file_repaired.tsv")


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
        description="Profile a repair function from a Python module on large_file.tsv"
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
    parser.add_argument(
        "-n",
        "--lines",
        type=int,
        default=30,
        help="Number of lines to show in the report (default: 30)",
    )
    parser.add_argument(
        "-s",
        "--sort",
        choices=["cumulative", "tottime", "calls", "name"],
        default="cumulative",
        help="Sort key for the report (default: cumulative)",
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

    print(f"Profiling {args.module.stem} on {args.input}...")
    profiler = cProfile.Profile()
    profiler.enable()
    repair(str(args.input), str(args.output))
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats(args.sort)
    print(f"\n--- Top {args.lines} hotspots (sort: {args.sort}) ---\n")
    stats.print_stats(args.lines)


if __name__ == "__main__":
    main()
