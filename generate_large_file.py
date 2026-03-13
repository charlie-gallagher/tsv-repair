import random
import itertools

N_COLUMNS = 50
N_ROWS = 1000
NEWLINE_PCT = 0.001

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
    "clop"
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
    "twelve"
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
    "quest"
]

HEADERS = [x + y + z for x, y, z in itertools.product(_header_part1, _header_part2, _header_part3)]
COLUMN_VALUES = _header_part1 + _header_part2 + _header_part3

def generate_file(filename: str, ncol: int, nrow: int, newline_likelihood: float) -> None:
    with open(filename, "w") as fout:
        header = _generate_header(ncol=ncol)
        fout.write(header + "\n")
        for i in range(nrow):
            row = _generate_row(ncol=ncol, newline_likelihood=newline_likelihood)
            fout.write(row + "\n")

def _generate_header(ncol: int) -> str:
    if ncol > len(HEADERS):
        raise ValueError(f"Cannot create data with this many columns: `{ncol}` (max: {len(HEADERS)})")
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


if __name__ == "__main__":
    generate_file(filename="large_file.tsv", ncol=N_COLUMNS, nrow=N_ROWS, newline_likelihood=NEWLINE_PCT)

