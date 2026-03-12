#!/usr/bin/env python3
"""
Memory-efficient repair for clickstream TSV files.

Processes input line-by-line without loading the whole file. Joins lines that
were split by unquoted newlines and writes output with embedded newlines
escaped as \\n. Suitable for multi-GB files.
"""


def repair(input_file: str, output_file: str) -> None:
    """
    Stream input_file, repair broken rows (join continuation lines), and write
    one line per row to output_file with newlines in fields as \\n.
    Uses only O(longest_line) memory plus a small row buffer.
    """
    with open(input_file, "r", newline="", errors="replace") as inf, open(
        output_file, "w", newline="\n"
    ) as out:
        header = inf.readline()
        if not header:
            return
        header = header.rstrip("\n\r")
        expected_tabs = header.count("\t")
        out.write(header + "\n")

        buffer: str | None = None
        first_row = True

        for line in inf:
            line = line.rstrip("\n\r")
            if buffer is None:
                buffer = line
                continue
            if buffer.count("\t") >= expected_tabs:
                # Buffer is already a complete row; never merge into it. Output and start new row.
                fields = buffer.split("\t")
                repaired = "\t".join(f.replace("\n", "\\n") for f in fields)
                if not first_row:
                    out.write("\n")
                out.write(repaired)
                first_row = False
                buffer = line
            elif line.count("\t") >= expected_tabs:
                # Buffer is incomplete but next line is complete: incomplete line starts a new row.
                # Output the partial row and start fresh with the complete line.
                fields = buffer.split("\t")
                repaired = "\t".join(f.replace("\n", "\\n") for f in fields)
                if not first_row:
                    out.write("\n")
                out.write(repaired)
                first_row = False
                buffer = line
            else:
                # Buffer incomplete and line incomplete: continuation of the same row
                buffer += "\n" + line

        if buffer is not None:
            fields = buffer.split("\t")
            repaired = "\t".join(f.replace("\n", "\\n") for f in fields)
            if not first_row:
                out.write("\n")
            out.write(repaired)

if __name__ == "__main__":
    import argparse
    import time
    parser = argparse.ArgumentParser(description="Repair clickstream TSV files")
    parser.add_argument("input_file", type=str, help="Input TSV file")
    parser.add_argument("output_file", type=str, help="Output TSV file")
    args = parser.parse_args()
    start_time = time.time()
    repair(args.input_file, args.output_file)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
