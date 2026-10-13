"""Statistics about a client folder: file count and total size
per category, printed as an aligned report.
"""

import os

from organizer.categories import get_category
from organizer.scanner import scan_directory


def format_size(size):
    """Return a byte count as a readable size (B, KiB, MiB, GiB, TiB)."""
    amount = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{amount:.1f} TiB"


def build_stats(source, ext_map, keywords):
    """Return file count and total size, overall and per category."""
    if not os.path.isdir(source):
        raise NotADirectoryError(f"Source is not an existing folder: {source}")

    stats = {"total_files": 0, "total_size": 0, "categories": {}}
    categories = stats["categories"]
    for name in scan_directory(source):
        size = os.path.getsize(os.path.join(source, name))
        category = get_category(name, ext_map, keywords)
        entry = categories.get(category, {"count": 0, "size": 0})
        entry["count"] += 1
        entry["size"] += size
        categories[category] = entry
        stats["total_files"] += 1
        stats["total_size"] += size
    return stats


def by_count(item):
    """Sort key: the file count of a (category, entry) pair."""
    return item[1]["count"]


def print_report(stats):
    """Print the stats as an aligned table, biggest category first."""
    total = stats["total_files"]
    if total == 0:
        print("No files found.")
        return

    print(f"{'Category':<12}{'Files':>6}{'Share':>8}{'Size':>12}")
    rows = sorted(stats["categories"].items(), key=by_count, reverse=True)
    for category, entry in rows:
        share = entry["count"] / total
        size = format_size(entry["size"])
        print(f"{category:<12}{entry['count']:>6}{share:>8.1%}{size:>12}")
    print(f"{'Total':<12}{total:>6}{'':>8}{format_size(stats['total_size']):>12}")