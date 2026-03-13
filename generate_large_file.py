import argparse
import random
import itertools

try:
    import tqdm
except ImportError:
    tqdm = None


def tqdm_wrap(iterable, **kwargs):
    if tqdm is not None:
        return tqdm.tqdm(iterable, **kwargs)
    return iterable


_header_part1 = [
    "monty",
    "python",
    "cheese",
    "store",
    "next",
    "time",
    "definitely",
    "nobody",
    "expects",
    "the",
    "spanish",
    "inquisition",
    "african",
    "swallow",
    "coconut",
    "clop",
]

_header_part2 = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
]

_header_part3 = [
    "alpha",
    "beta",
    "charlie",
    "delta",
    "epsilon",
    "foxtrot",
    "goose",
    "hare",
    "iota",
    "java",
    "kappa",
    "lambda",
    "mindreader",
    "nanner_nanner_pudding",
    "omega",
    "pit",
    "quest",
]

HEADERS = [
    x + y + z
    for x, y, z in itertools.product(_header_part1, _header_part2, _header_part3)
]
COLUMN_VALUES = _header_part1 + _header_part2 + _header_part3


def generate_file(
    filename: str, ncol: int, nrow: int, newline_likelihood: float
) -> None:
    with open(filename, "w") as fout:
        header = _generate_header(ncol=ncol)
        fout.write(header + "\n")
        for i in tqdm_wrap(range(nrow)):
            row = _generate_row(ncol=ncol, newline_likelihood=newline_likelihood)
            fout.write(row + "\n")


def _generate_header(ncol: int) -> str:
    if ncol > len(HEADERS):
        raise ValueError(
            f"Cannot create data with this many columns: `{ncol}` (max: {len(HEADERS)})"
        )
    # First column is "id"
    headers = ["id"]
    return "\t".join(headers + random.sample(HEADERS, ncol - 1))


def _generate_row(ncol: int, newline_likelihood: float) -> str:
    row = []
    for i in range(ncol):
        # The first row should be an ID
        if i == 0:
            # A random 10 digit number, repeats are ok
            row.append(str(random.randint(1000000000, 9999999999)))
            continue
        add_newline = (1 - newline_likelihood) < random.random()
        col_values = " ".join(random.sample(COLUMN_VALUES, 4))
        if add_newline:
            col_values = col_values.replace(" ", "\n", 1)
        row.append(col_values)
    return "\t".join(row)


def main() -> None:
    default_columns = 120
    default_rows = 10_000_000
    default_newline_pct = 0.002
    default_output_file = "large_file.tsv"
    parser = argparse.ArgumentParser(
        description="Generate a large TSV file with configurable size and newline probability."
    )
    parser.add_argument(
        "-o",
        "--output",
        default=default_output_file,
        help=f"Output filename (default: {default_output_file})",
    )
    parser.add_argument(
        "-c",
        "--columns",
        type=int,
        default=default_columns,
        help=f"Number of columns (default: {default_columns})",
    )
    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        default=default_rows,
        help=f"Number of rows (default: {default_rows})",
    )
    parser.add_argument(
        "--newline-likelihood",
        type=float,
        default=default_newline_pct,
        dest="newline_likelihood",
        help=f"Probability that a cell contains an embedded newline (default: {default_newline_pct})",
    )
    args = parser.parse_args()
    generate_file(
        filename=args.output,
        ncol=args.columns,
        nrow=args.rows,
        newline_likelihood=args.newline_likelihood,
    )


if __name__ == "__main__":
    main()
