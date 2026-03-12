"""
This is a more optimized version of the repair tool.

It memory maps the input file and doesn't decode the utf-8 bytes.
"""

import io
import mmap
import sys

def repair(input_file: str, output_file: str) -> None:
    """
    Repair the input file and write the output to the output file.
    """
    with open(input_file, "rb") as fin, open(output_file, "wb") as fout_raw:
        with io.BufferedWriter(fout_raw, buffer_size=256 * 1024) as fout:
            with mmap.mmap(fin.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                header = mm.readline()
                fout.write(header)
                if not header:
                    return
                header = header.rstrip(b"\n\r")
                expected_tabs = header.count(b"\t")
                buffer = bytearray()
                replacement_char = b" "
                n_rows = 0
                n_partial_lines = 0
                current_row_tabs = 0
                while True:
                    next_line = mm.readline()
                    if not next_line:
                        break

                    next_line_tabs = next_line.count(b"\t")

                    # Line join routine
                    if buffer:
                        n_partial_lines += 1
                        # Case: Current line is incomplete but joining with the next
                        # line would cause too many fields
                        if next_line_tabs + current_row_tabs > expected_tabs:
                            print("WARNING: joining would create too many tabs")
                            n_rows += 1
                            fout.write(buffer)
                            buffer.clear()
                            current_row_tabs = 0
                        else:
                            # Fix only the trailing newline (join boundary) in place.
                            # Append next_line with internal newlines escaped but trailing newline preserved.
                            if buffer.endswith(b"\r\n"):
                                del buffer[-2:]
                                buffer.extend(replacement_char)
                            elif buffer.endswith(b"\n"):
                                del buffer[-1:]
                                buffer.extend(replacement_char)
                            rest = next_line.rstrip(b"\n\r")
                            suffix = next_line[len(rest):]
                            buffer.extend(rest.replace(b"\n", replacement_char))
                            buffer.extend(suffix)
                            next_line = b""  # already appended

                    # Normally buffer is empty, but it also may contain a partial row
                    # that we need to join with the next line.
                    if next_line:
                        buffer.extend(next_line)
                    current_row_tabs += next_line_tabs

                    if current_row_tabs < expected_tabs:
                        continue

                    # Write buffer to output file
                    n_rows += 1
                    fout.write(buffer)

                    buffer.clear()
                    current_row_tabs = 0
                if buffer:
                    n_rows += 1
                    fout.write(buffer)
    print(f"Processed {n_rows} rows, {n_partial_lines} partial lines")


def main():
    repair(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")