import io
from concurrent.futures import ProcessPoolExecutor, as_completed
import os


def repair(input_file: str, output_file: str, concat_files: bool = False) -> None:
    chunks = _get_chunks(input_file)
    n_field_delims = _get_n_field_delims(input_file)
    # In the first pass, each worker reads a chunk and reports the number of
    # tab characters in the chunk. Then, the master process collects the results
    # and determines the correct adjusted chunk offsets for each worker.
    with ProcessPoolExecutor(max_workers=len(chunks)) as executor:
        stats = list(
            zip(chunks, executor.map(gather_stats, [input_file] * len(chunks), chunks))
        )

        # I should be able to tell each worker to fast forward N tabs, then read
        # past their assigned end by M tabs
        tab_info = []
        prev_complement_tabs = 0
        for chunk, n_tabs in stats:
            skip_tabs = prev_complement_tabs
            # Calculate the number of additional tabs needed to make a complete record
            complement_tabs = (
                n_field_delims - (n_tabs - prev_complement_tabs) % n_field_delims
            )
            if complement_tabs == n_field_delims:
                complement_tabs = 0
            tab_info.append((chunk, n_tabs, skip_tabs))
            prev_complement_tabs = complement_tabs

        futures = []
        sub_output_files = []
        for chunk, n_tabs, skip_tabs in tab_info:
            sub_output_file = f"{chunk[0]}_{chunk[1]}_{output_file}"
            sub_output_files.append(sub_output_file)
            futures.append(
                executor.submit(
                    repair_chunk,
                    input_file,
                    chunk,
                    n_field_delims,
                    skip_tabs,
                    sub_output_file,
                )
            )
        for future in as_completed(futures):
            future.result()

    # Now stitch the files back together for debugging purposes
    if concat_files:
        with open(output_file, "wb") as fout:
            for sub_output_file in sub_output_files:
                with open(sub_output_file, "rb") as fin:
                    fout.write(fin.read())
                os.remove(sub_output_file)


def _get_chunks(input_file: str) -> list[tuple[int, int]]:
    def chunk_indices(length, n):
        k, m = divmod(length, n)
        return [(i * k + min(i, m), (i + 1) * k + min(i + 1, m)) for i in range(n)]

    num_processors = os.cpu_count()
    input_file_size = os.path.getsize(input_file)
    chunks = chunk_indices(input_file_size, num_processors)
    return chunks


def _get_n_field_delims(input_file: str) -> int:
    with open(input_file, "rb") as fin:
        header = fin.readline()
        return header.count(b"\t")


def gather_stats(input_file: str, input_range: tuple[int, int]) -> int:
    with open(input_file, "rb") as fin:
        with io.BufferedReader(fin, buffer_size=256 * 1024) as fin_buffered:
            fin_buffered.seek(input_range[0])
            section_tabs = 0
            while True:
                line = fin_buffered.readline()
                new_pos = fin_buffered.tell()
                if new_pos >= input_range[1]:
                    # Only count up through input_range[1]
                    line = line[: input_range[1] - new_pos]
                section_tabs += line.count(b"\t")
                if new_pos >= input_range[1]:
                    break
            return section_tabs


def repair_chunk(
    input_file: str,
    input_range: tuple[int, int],
    expected_tabs: int,
    skip_tabs: int,
    output_file: str,
) -> None:
    with open(input_file, "rb") as fin_raw, open(output_file, "wb") as fout_raw:
        with io.BufferedReader(fin_raw, buffer_size=1 << 20) as fin, io.BufferedWriter(
            fout_raw, buffer_size=256 * 1024
        ) as fout:

            fin.seek(input_range[0])
            if input_range[0] != 0:
                # Skip the correct number of tabs
                n_tabs = 0
                while n_tabs < skip_tabs:
                    next_byte = fin.read1(1)
                    if next_byte == b"\t":
                        n_tabs += 1
                # Now align to the next newline
                next_byte = fin.read1(1)
                while next_byte != b"\n":
                    next_byte = fin.read1(1)

            # Then, iterate over the lines, repairing as you go
            while True:
                if fin.tell() >= input_range[1]:
                    break
                line = fin.readline()
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
                    continuation_line = fin.readline()
                    if not continuation_line:
                        break
                    cline_tabs = continuation_line.count(b"\t")
                    if line_tabs + cline_tabs <= expected_tabs:
                        line = line.rstrip(b"\n") + b" " + continuation_line
                        line_tabs += cline_tabs
                    else:
                        # Adding these lines would create a row with too many fields
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
    print(f"Reading {input_file} and writing to {output_file}")
    repair(input_file, output_file)
