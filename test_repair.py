#!/usr/bin/env python3
"""
Testing utility for clickstream repair functions.

Tests a function with signature (input_file: str, output_file: str) by running it
on each input file in test_files/ and comparing the output to the corresponding
golden file (suffix _repaired before extension).
"""

from pathlib import Path
import tempfile
from typing import Callable

# Default directory containing test files (input and _repaired golden files)
DEFAULT_TEST_DIR = Path(__file__).resolve().parent / "test_files"


def get_test_pairs(test_dir: Path) -> list[tuple[Path, Path]]:
    """
    Discover (input_file, golden_file) pairs in test_dir.

    Input files are those for which a matching *_repaired.* file exists.
    Returns list of (input_path, golden_path) tuples.
    """
    pairs: list[tuple[Path, Path]] = []
    for golden_path in test_dir.iterdir():
        if not golden_path.is_file() or not golden_path.stem.endswith("_repaired"):
            continue
        # e.g. basic_repaired.tsv -> basic.tsv
        input_stem = golden_path.stem.removesuffix("_repaired")
        input_path = golden_path.parent / f"{input_stem}{golden_path.suffix}"
        if input_path.exists():
            pairs.append((input_path, golden_path))
    return sorted(pairs)


def run_tests(
    repair_fn: Callable[[str, str], None],
    test_dir: Path | None = None,
) -> tuple[int, int]:
    """
    Run repair_fn on each input test file and compare output to golden files.

    Args:
        repair_fn: Function (input_file: str, output_file: str) that writes
                   repaired content to output_file.
        test_dir: Directory containing test files. Defaults to test_files/.

    Returns:
        (passed_count, total_count).
    """
    test_dir = test_dir or DEFAULT_TEST_DIR
    if not test_dir.is_dir():
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    pairs = get_test_pairs(test_dir)
    if not pairs:
        print("No test pairs found (no *_repaired files with matching input files).")
        return 0, 0

    passed = 0
    for input_path, golden_path in pairs:
        name = input_path.name
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=input_path.suffix,
            delete=False,
        ) as f:
            out_path = Path(f.name)
        try:
            repair_fn(str(input_path), str(out_path))
            with open(golden_path, "rb") as g:
                expected = g.read()
            with open(out_path, "rb") as o:
                actual = o.read()
            if actual == expected:
                print(f"  PASS  {name}")
                passed += 1
            else:
                print(f"  FAIL  {name} (output differs from {golden_path.name})")
        except Exception as e:
            print(f"  ERROR {name}: {e}")
        finally:
            out_path.unlink(missing_ok=True)

    return passed, len(pairs)


def main(
    repair_fn: Callable[[str, str], None] | None = None,
    test_dir: Path | None = None,
) -> bool:
    """
    Run tests and print a summary. Returns True if all tests passed.

    If repair_fn is None, prints usage and returns False.
    """
    if repair_fn is None:
        print(
            "Usage: Pass your repair function to run_tests() or main().\n"
            "Example:\n"
            "  from test_repair import run_tests\n"
            "  run_tests(my_repair_function)\n"
            "Or run with a concrete implementation:\n"
            "  python test_repair.py  # after setting REPAIR_FN below"
        )
        return False

    test_dir = test_dir or DEFAULT_TEST_DIR
    print(f"Testing repair function against golden files in {test_dir}\n")
    passed, total = run_tests(repair_fn, test_dir)
    print(f"\n{passed}/{total} tests passed.")
    return passed == total


if __name__ == "__main__":
    try:
        from repair_optimized import repair as REPAIR_FN
    except ImportError:
        REPAIR_FN = None
    ok = main(REPAIR_FN)
    exit(0 if ok else 1)
