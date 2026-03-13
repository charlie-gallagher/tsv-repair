# TSV Repair
In this repo, you can test a repair function for correctness and benchmark it.

To get started, you need a python module with a `repair` function. The repair must have the following signature:

```py
def repair(input_file: str, output_file: str) -> None:
    ...
```

It should read `input_file` and write the repaired version to `output_file`.

## Tests
To run the tests, run the `test_repair.py` script with your python file as the argument.

```
python test_repair.py repair_basic.py
```

## Performance benchmarks
Generate a large TSV file with random newlines using `generate_large_file.py`.

```
python3 generate_large_file.py
```

This is configurable, but I ran my benchmarks against the defaults. See `python3 generate_large_file.py --help` for more information. If you want a **progress bar** you can install `tqdm` and the file will pick up on it and use that to show progress as rows are generated.

Once you have a large file, you use the `benchmark_repair.py` script just like the `test_repair.py` script.

```
python benchmark_repair.py repair_basic.py
```

This will write results to stdout and record them in the file `perf_log.txt` so you can keep track of your optimizations over time.

# Problem description
Using pure python (stdlib), repair a large (10GB), utf-8 encoded TSV file with a
known number of fields by (a) identifying incomplete lines, (b) combining
successive incomplete lines until they form a complete line, and (c) not
combining lines if the result is a row with too many fields. A single row may
have one or more newlines, i.e.  a row might be spread across one or more lines
of the file. The lines that form a row are always ordered correctly, successive
and contiguous. Newlines are LF only, not CRLF.

To make things simpler, even if a field is quoted, you can still join successive
split lines.

In the end, the file should look like this:

```
id	name	comment	score
0	charlie	normal	20
1	alice	this is a multiline comment	10
2	bob	normal	8
```

i.e. replace the newline character with a space. If there are multiple newline
characters in a row (`hello\n\nworld`), replace each one with a space. If a
field starts or ends with a newline, you can still replace newlines with a
space.

A few categories for results:

- Single- vs multi-threaded
- cPython vs other interpreters
- Pure python vs other libraries vs external code (but then you could just write
  it in C, and that's no fun).

---

Charlie Gallagher, March 2026
