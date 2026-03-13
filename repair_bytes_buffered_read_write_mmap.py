import io
import mmap


def repair(input_file: str, output_file: str) -> None:
    with open(input_file, "rb") as fin_raw, open(output_file, "wb") as fout_raw:
        with mmap.mmap(fin_raw.fileno(), 0, access=mmap.ACCESS_READ) as mm_in:
            with io.BufferedWriter(fout_raw, buffer_size=256 * 1024) as fout:

                # Start by copying header
                header = mm_in.readline()
                fout.write(header)

                expected_tabs = header.count(b"\t")

                # Then, iterate over the lines, repairing as you go
                while True:
                    line = mm_in.readline()
                    if not line:
                        break
                    line_tabs = line.count(b"\t")
                    if line_tabs == expected_tabs:
                        fout.write(line)
                        continue

                    # Line repair
                    # Grab next line and see if it complements
                    _need_to_write = True
                    while line_tabs < expected_tabs:
                        continuation_line = mm_in.readline()
                        if not continuation_line:
                            break
                        cline_tabs = continuation_line.count(b"\t")
                        if line_tabs + cline_tabs <= expected_tabs:
                            line = line.rstrip(b"\n") + b" " + continuation_line
                            line_tabs += cline_tabs
                        else:
                            # Adding these lines would create a row with
                            # too many fields
                            fout.write(line)
                            fout.write(continuation_line)
                            _need_to_write = False
                            break
                    if _need_to_write:
                        fout.write(line)


if __name__ == "__main__":
    import sys

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    print(f"Reader {input_file} and writing to {output_file}")
    repair(input_file, output_file)
