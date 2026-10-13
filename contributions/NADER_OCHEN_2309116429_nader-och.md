# Contributions: Nader Ochen

- **Student ID:** 2309116429
- **GitHub:** nader-och
- **Role:** developer and presenter

## How we worked

I built this project together with Taha Yağız Kalender on one laptop (mine), pair programming. Because of this, the code commits were made from my account (nader-och). The commits we made together from the README onward carry a `Co-authored-by` line for Taha.

## What we built

| Module | Functions and features |
|---|---|
| `organizer/scanner.py` | `get_extension` (lowercase extension with `os.path.splitext`), `scan_directory` (sorted regular files only; skips hidden files, symlinks and folders) |
| `organizer/categories.py` | Default extension and keyword rules (dictionaries), `build_extension_map` (inverts category → extensions into extension → category), `get_category` (keyword rules first, then `dict.get(ext, "Other")`), JSON config loading with strict validation (`load_config`, `read_extensions`, `read_keywords`, `is_valid_category_name`) |
| `organizer/mover.py` | `check_paths` (source/destination safety checks), `plan_moves` (list of `(source, target)` tuples, touches nothing), `execute_plan` (preview or apply, collision skip, per-file exception handling, returns a counts dictionary) |
| `organizer/report.py` | `format_size`, `build_stats` (accumulator pattern with nested dictionaries), `print_report` (aligned f-string table sorted by file count) |
| `cli.py` | `argparse` with `organize` and `stats` subcommands, `--apply`, `--verbose` and `--config` options, central error handling with exit code 1, `if __name__ == "__main__":` guard |
| `config.example.json` | Example client config |
| `README.md`, `.gitignore` | Documentation and repository hygiene |

## Design decisions

- **Preview is the default.** Moving files is a real filesystem change, so `--apply` must be typed on purpose.
- **Plan, then execute.** `plan_moves` only builds a list of tuples; `execute_plan` is the only function that changes the disk. This keeps the preview and the real run identical.
- **Dictionaries instead of if/elif chains.** The rules are data, so a client config can extend them without changing the code.
- **Keywords before extensions.** For an agency, a logo is a branding asset whatever its file format (`logo-white.svg` goes to `Branding`, not `Design`).
- **Functions return data instead of printing.** `execute_plan` and `build_stats` return dictionaries; `cli.py` decides how to display them.
- **Strict validation of outside input.** The config file is untrusted, so every type is checked and every name is validated with `re.fullmatch` before it can become a folder name.

## Robustness tests performed

- Source missing or a file → clear error, exit 1, no destination created
- Source and destination the same (also as `DEMO`, a full path and `demo\..\demo`), destination inside source, source inside destination → refused
- Destination is a file → refused
- Target already exists → skipped, never overwritten
- Hidden files and subfolders → skipped
- No extension (`notes`), double extension (`a.tar.gz`), uppercase (`LOGO.PNG`) → `Other`, `gz`, `png`
- Spaces and Arabic filenames → handled, names preserved
- Locked file during `--apply` → counted as failed, the run continued
- A file named like a category folder in the destination → counted as failed, the run continued
- Broken JSON, wrong types, unknown key, file over 100 KB, missing file, category names `../../Desktop` and `/etc` → clear `ValueError` message, exit 1
- Empty source folder → "No files found.", exit 0
- Missing arguments, misspelled options, unknown subcommand → argparse error

## Course topics used

Functions with docstrings and return values; dictionaries (`.get` with a default, `.items()`, `.update()`, nested dictionaries); lists and tuples; loops with `continue`; f-strings with alignment and percentages; `os`, `os.path` and `shutil`; `try/except` with specific exceptions and `raise`; `argparse` with subcommands; `json`; `re`; modules and packages; the `__name__` guard.

## Commit history

1. Set up project structure with module docstrings and .gitignore
2. Add get_extension helper and keyword-first get_category
3. Add scan_directory that skips hidden files, symlinks and folders
4. Add mover with path safety checks, dry-run plan and collision skip
5. Add CLI with organize subcommand, preview by default and clean errors
6. Add stats command with per-category counts, sizes and aligned report
7. Add JSON client config with strict regex validation and --config
8. Add README and contributions files, make project description generic (co-authored with Taha)