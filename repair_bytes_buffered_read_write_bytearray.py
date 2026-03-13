import io


def repair(input_file: str, output_file: str) -> None:
    with open(input_file, "rb") as fin_raw, open(output_file, "wb") as fout_raw:
        with io.BufferedReader(fin_raw, buffer_size=1 << 20) as fin, io.BufferedWriter(
            fout_raw, buffer_size=256 * 1024
        ) as fout:

            # Start by copying header
            header = fin.readline()
            fout.write(header)

            expected_tabs = header.count(b"\t")

            # Then, iterate over the lines, repairing as you go
            buffer = bytearray()
            while True:
                buffer.extend(fin.readline())
                if not buffer:
                    break
                line_tabs = buffer.count(b"\t")
                if line_tabs == expected_tabs:
                    fout.write(buffer)
                    buffer.clear()
                    continue

                # Line repair
                # Grab next line and see if it complements
                _need_to_write = True
                while line_tabs < expected_tabs:
                    continuation_line = fin.readline()
                    if not continuation_line:
                        break
                    cline_tabs = continuation_line.count(b"\t")
                    if line_tabs + cline_tabs <= expected_tabs:
                        buffer.pop(-1) # remove the newline
                        buffer.extend(b" " + continuation_line)
                        line_tabs += cline_tabs
                    else:
                        # Adding these lines would create a row with
                        # too many fields
                        fout.write(buffer)
                        fout.write(continuation_line)
                        buffer.clear()
                        _need_to_write = False
                        break
                if _need_to_write:
                    fout.write(buffer)
                    buffer.clear()


if __name__ == "__main__":
    import sys

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    print(f"Reader {input_file} and writing to {output_file}")
    repair(input_file, output_file)
