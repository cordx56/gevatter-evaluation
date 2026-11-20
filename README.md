# An Evaluation Artifact of [Gevatter](https://github.com/cordx56/gevatter)

Fetch N (default = 100) crates from crates.io and run `cargo gevatter check -- --workspace`.

## How to Run

```bash
python main.py
```

Fetched crates are saved in `crates/` directory.
Edited crates are saved in `edited/` directory if Gevatter suggests.

## Important Files

- `main.py`: Run experiment and output reports.
- `crates.json`: Lock file to pin the exact crate versions used in the experiment.
- `examples/*`: Example crates that shows how Gevatter improves their lifetime annotations.
