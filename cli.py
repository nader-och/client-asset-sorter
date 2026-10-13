"""Client Asset Sorter - command-line entry point.

Sorts a client's WhatsApp dump folder into a digital agency's standard
delivery structure (Images, Videos, Branding, Menu, ...).
Preview is the default; nothing moves without --apply.

Usage:
    python cli.py organize SOURCE DEST [--apply] [--config FILE] [--verbose]
    python cli.py stats SOURCE [--config FILE]
"""

import argparse
import sys

from organizer.categories import (DEFAULT_EXTENSIONS, DEFAULT_KEYWORDS,
                                  build_extension_map, load_config)
from organizer.mover import check_paths, execute_plan, plan_moves
from organizer.report import build_stats, print_report


def build_parser():
    """Create the argument parser with one subcommand per action."""
    parser = argparse.ArgumentParser(
        description="Sort a client's WhatsApp dump into agency folders.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize = subparsers.add_parser(
        "organize", help="preview or move files into category folders")
    organize.add_argument("source", help="the client's dump folder")
    organize.add_argument("dest", help="where the sorted folders are created")
    organize.add_argument("--apply", action="store_true",
                          help="really move the files (default: preview only)")
    organize.add_argument("--verbose", action="store_true",
                          help="print every file that is moved")
    organize.add_argument("--config", metavar="FILE",
                          help="client config file (JSON)")

    stats = subparsers.add_parser(
        "stats", help="report file count and size per category")
    stats.add_argument("source", help="the client's dump folder")
    stats.add_argument("--config", metavar="FILE",
                       help="client config file (JSON)")
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


def run_stats(args, ext_map, keywords):
    """Build the statistics for the source folder and print them."""
    stats = build_stats(args.source, ext_map, keywords)
    print_report(stats)


def main():
    """Parse the arguments and run the chosen command."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.config:
            ext_map, keywords = load_config(args.config)
        else:
            ext_map = build_extension_map(DEFAULT_EXTENSIONS)
            keywords = DEFAULT_KEYWORDS

        if args.command == "organize":
            run_organize(args, ext_map, keywords)
        elif args.command == "stats":
            run_stats(args, ext_map, keywords)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()