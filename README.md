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

## Environment and Versions

We verified that this repo is working on the machine with NVIDIA GB10 (aarch64; 128 GB RAM) running Ubuntu 24.04.
The Gevatter version we used is [v0.1.3](https://github.com/cordx56/gevatter/releases/tag/v0.1.3).
