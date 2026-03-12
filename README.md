# TSV Repair
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

---

Charlie Gallagher, March 2026
