"""Orena Asset Sorter - command-line entry point.

Sorts a client's WhatsApp dump folder into Orena Studio's standard
delivery structure (Images, Videos, Branding, Menu, ...).
Preview is the default; nothing moves without --apply.

Usage:
    python cli.py organize SOURCE DEST [--apply] [--config FILE] [--verbose]
    python cli.py stats SOURCE [--config FILE]
"""

import argparse
import sys

from organizer.categories import (DEFAULT_EXTENSIONS, DEFAULT_KEYWORDS,
                                  build_extension_map)
from organizer.mover import check_paths, execute_plan, plan_moves


def build_parser():
    """Create the argument parser with one subcommand per action."""
    parser = argparse.ArgumentParser(
        description="Sort a client's WhatsApp dump into Orena Studio folders.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize = subparsers.add_parser(
        "organize", help="preview or move files into category folders")
    organize.add_argument("source", help="the client's dump folder")
    organize.add_argument("dest", help="where the sorted folders are created")
    organize.add_argument("--apply", action="store_true",
                          help="really move the files (default: preview only)")
    organize.add_argument("--verbose", action="store_true",
                          help="print every file that is moved")
    return parser


def run_organize(args, ext_map, keywords):
    """Check the paths, build the plan, then preview or apply it."""
    check_paths(args.source, args.dest)
    plan = plan_moves(args.source, args.dest, ext_map, keywords)
    if not plan:
        print("No files found.")
        return

    if args.apply:
        print("Moving files...")
    else:
        print("Preview - nothing moved. Add --apply to run.")
    counts = execute_plan(plan, args.apply, args.verbose)

    if args.apply:
        print(f"Moved: {counts['moved']}   Skipped: {counts['skipped']}   "
              f"Failed: {counts['failed']}")
    else:
        print(f"Planned: {counts['planned']}   Skipped: {counts['skipped']}")


def main():
    """Parse the arguments and run the chosen command."""
    parser = build_parser()
    args = parser.parse_args()
    ext_map = build_extension_map(DEFAULT_EXTENSIONS)
    keywords = DEFAULT_KEYWORDS

    try:
        if args.command == "organize":
            run_organize(args, ext_map, keywords)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()