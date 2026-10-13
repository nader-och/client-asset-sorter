# Client Asset Sorter

This project is built for a digital agency in Casablanca, Morocco, that creates QR digital menus, NFC smart cards and social media content for restaurants and shops. Clients send their material over WhatsApp, so every new client arrives as one messy folder of photos, videos, voice notes, logos, menus and documents (`IMG-20261003-WA0012.jpg`, `VID-20261003-WA0004.mp4`, `PTT-20261002-WA0001.opus`, `LOGO.PNG`, `menu_final_v3.pdf`, ...).

**Client Asset Sorter** is a command-line tool that turns that dump folder into a standard delivery structure (`Images`, `Videos`, `Audio`, `Documents`, `Design`, `Archives`, `Branding`, `Menu`, `Other`). It **previews every move before touching anything**, never overwrites a file, reports what the client sent, and supports client-specific rules through a JSON config file.

## Installation

- Python 3 (developed and tested with Python 3.11)
- No external packages: standard library only (`argparse`, `os`, `shutil`, `json`, `re`, `sys`)

```
git clone https://github.com/nader-och/client-asset-sorter.git
cd client-asset-sorter
python cli.py --help
```

## Usage

### Preview (the default: nothing is moved)

```
python cli.py organize demo demo_out
```
```
Preview - nothing moved. Add --apply to run.
  demo\IMG-20261003-WA0012.jpg -> demo_out\Images\IMG-20261003-WA0012.jpg
  demo\LOGO.PNG -> demo_out\Branding\LOGO.PNG
  demo\PTT-20261002-WA0001.opus -> demo_out\Audio\PTT-20261002-WA0001.opus
  demo\VID-20261003-WA0004.mp4 -> demo_out\Videos\VID-20261003-WA0004.mp4
  demo\logo-white.svg -> demo_out\Branding\logo-white.svg
  demo\menu with spaces.pdf -> demo_out\Menu\menu with spaces.pdf
  demo\menu_final_v3.pdf -> demo_out\Menu\menu_final_v3.pdf
  demo\notes -> demo_out\Other\notes
  demo\story_promo.mp4 -> demo_out\Videos\story_promo.mp4
Planned: 9   Skipped: 0
```

### Apply (really move the files)

```
python cli.py organize demo demo_out --apply --verbose
```
```
Moving files...
  Moved: demo\IMG-20261003-WA0012.jpg -> demo_out\Images\IMG-20261003-WA0012.jpg
  ...
Moved: 9   Skipped: 0   Failed: 0
```

Without `--verbose`, only skipped and failed files are listed, followed by the summary line.

### Use a client config

```
python cli.py organize demo demo_out --config config.example.json
```
With the example config, `story_promo.mp4` goes to `demo_out\Social\` instead of `Videos`, because the client's keyword rule `"story": "Social"` is checked first.

### Statistics

```
python cli.py stats demo
```
```
Category     Files   Share        Size
Branding         2   22.2%       0.0 B
Videos           2   22.2%     2.9 MiB
Menu             2   22.2%   244.1 KiB
Images           1   11.1%       0.0 B
Audio            1   11.1%    43.9 KiB
Other            1   11.1%       0.0 B
Total            9             3.1 MiB
```
`stats` also accepts `--config FILE`.

### Help

```
python cli.py --help
python cli.py organize --help
python cli.py stats --help
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (including "No files found." for an empty folder) |
| 1 | Invalid input: bad paths or bad config. One `Error: ...` line is printed to stderr |
| 2 | Invalid command-line arguments (reported by argparse) |

## Config file format

`config.example.json`:
```json
{
  "client": "Example Cafe",
  "extensions": { "Images": ["jpg", "png"], "Menu": ["pdf"] },
  "keywords": { "logo": "Branding", "story": "Social" }
}
```

| Key | Type | Rules |
|---|---|---|
| `client` | text (optional) | the client's name |
| `extensions` | object: category → list of extensions | category: 1–40 characters, letters, digits, space, `_` or `-`, starting with a letter or digit. Extension: 1–10 letters or digits, no dot (`"jpg"`, not `".jpg"`) |
| `keywords` | object: keyword → category | keyword: 1–30 characters, letters, digits, `_` or `-`; category follows the rule above |

- Only these three keys are allowed. A typo such as `"extentions"` is reported as an error.
- The file must be valid UTF-8 JSON and at most 100 KB.
- Client rules are added **on top of** the default rules. If the client and the defaults disagree, **the client wins** (in the example, every PDF goes to `Menu`).

### Default rules

| Category | Extensions |
|---|---|
| Images | jpg, jpeg, png, webp, heic, gif |
| Videos | mp4, mov, 3gp, mkv |
| Audio | mp3, m4a, opus, ogg, wav |
| Documents | pdf, docx, doc, txt, xlsx, pptx |
| Design | svg, psd, ai, eps |
| Archives | zip, rar, 7z |

Default keywords: `logo` → `Branding`, `menu` → `Menu`.

**How a file's category is chosen:** keyword rules first (case-insensitive, in the order they are written; the first match wins), then the file extension, then `Other`.

## Project structure

| Path | Purpose |
|---|---|
| `cli.py` | Entry point. Builds the `argparse` parser with the `organize` and `stats` subcommands, loads the config or the defaults, runs the chosen command, and turns errors into one readable message with exit code 1. |
| `organizer/` | The package that holds the program's logic. |
| `organizer/__init__.py` | Marks `organizer` as a package so `cli.py` can import its modules. |
| `organizer/categories.py` | Default extension and keyword rules, `build_extension_map` (category → extensions becomes extension → category), `get_category`, and JSON config loading with strict validation. |
| `organizer/scanner.py` | Reads the source folder: `get_extension` and `scan_directory` (regular files only; skips folders, symlinks and hidden files). |
| `organizer/mover.py` | `check_paths` (refuses unsafe source/destination pairs), `plan_moves` (builds the plan without touching the disk) and `execute_plan` (preview or apply, collision skip, per-file error handling). |
| `organizer/report.py` | `format_size`, `build_stats` (count and size per category) and `print_report` (aligned table, biggest category first). |
| `config.example.json` | Example client config. |
| `contributions/` | Contribution file of each team member. |
| `.gitignore` | Keeps `__pycache__`, virtual environments, OS files and the `demo` test folders out of the repository. |

## Safety design

- **Preview by default.** Nothing moves unless `--apply` is given.
- **Path checks before scanning.** The source must be an existing folder; the destination must not be a file; source and destination must not be the same folder or inside each other. Paths are compared as real absolute paths (`os.path.realpath` + `os.path.commonpath`), case-insensitively on Windows, so `demo`, `DEMO` and `demo\..\demo` are recognised as the same folder.
- **Never overwrites.** If anything already exists at the target path (`os.path.lexists`), the file is skipped and reported.
- **Only regular files are moved.** Hidden files, symlinks and subfolders are skipped.
- **One bad file doesn't stop the run.** `FileNotFoundError`, `PermissionError` and other `OSError`s are caught per file, counted as failed, and the run continues.
- **Strict config validation.** Every type is checked, and names are validated with `re.fullmatch`, so `../../Desktop`, `/etc` or `C:\Windows` can never become a folder name. Oversized and invalid JSON files are rejected with a clear message.
- **Clean errors.** Invalid input gives one `Error: ...` line on stderr and exit code 1, never a traceback.

## Limitations

- Not recursive: only files directly inside the source folder are sorted.
- Only the last extension is used: `a.tar.gz` is treated as `gz` and goes to `Other`.
- Keywords are plain text matches and the first match wins: `menu_logo.png` goes to `Branding`. Keywords are limited to English letters and digits.
- Windows system files whose names don't start with a dot (such as `desktop.ini` or `Thumbs.db`) are sorted into `Other`.
- There is no undo command: use the preview before `--apply`.

## Team

- Nader Ochen ([nader-och](https://github.com/nader-och))
- Taha Yağız Kalender ([Taha-1-K](https://github.com/Taha-1-K))