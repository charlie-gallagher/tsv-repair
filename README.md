# TSV Repair
## Tests
To run the tests, update the main method in `test_repair.py` so that it imports
your module's repair method. The repair method must have the following
signature:

```py
def repair(input_file: str, output_file: str) -> None:
    ...
```

It should read `input_file` and write to `output_file`. You can also run the
tests using this one liner:

```
python3 -c "from test_repair import main; from MY_MODULE import repair; main(repair)"
```

## Performance benchmarks
Generate a large TSV file with random newlines using `generate_large_file.py`.

```
python3 generate_large_file.py
```

This is configurable, but I ran my benchmarks against the defaults. See `python3 generate_large_file.py --help` for more information. This also has the current defaults.

If you want a **progress bar** you can install `tqdm` and the file will pick up on it and use that to show progress as rows are generated.

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
