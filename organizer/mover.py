"""Moving files safely: path checks, building a move plan,
and running it as a preview (dry-run) or for real (--apply).
"""

import os
import shutil

from organizer.categories import get_category
from organizer.scanner import scan_directory


def check_paths(source, dest):
    """Raise an error if source and dest are not safe to use together."""
    if not os.path.isdir(source):
        raise NotADirectoryError(f"Source is not an existing folder: {source}")
    if os.path.exists(dest) and not os.path.isdir(dest):
        raise ValueError(f"Destination exists and is not a folder: {dest}")

    real_source = os.path.normcase(os.path.realpath(source))
    real_dest = os.path.normcase(os.path.realpath(dest))
    try:
        common = os.path.commonpath([real_source, real_dest])
    except ValueError:
        return  # different drives on Windows, so they cannot overlap
    if common in (real_source, real_dest):
        raise ValueError("Source and destination must not be the same folder "
                         "or inside each other.")


def plan_moves(source, dest, ext_map, keywords):
    """Return a list of (src_path, target_path) tuples. Touches nothing."""
    plan = []
    for name in scan_directory(source):
        category = get_category(name, ext_map, keywords)
        src_path = os.path.join(source, name)
        target_path = os.path.join(dest, category, name)
        plan.append((src_path, target_path))
    return plan


def execute_plan(plan, apply, verbose):
    """Preview or perform the moves in plan and return the counts."""
    counts = {"planned": len(plan), "moved": 0, "skipped": 0, "failed": 0}
    for src_path, target_path in plan:
        if os.path.lexists(target_path):
            print(f"  Skip (already exists): {target_path}")
            counts["skipped"] += 1
            continue
        if not apply:
            print(f"  {src_path} -> {target_path}")
            continue
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.move(src_path, target_path)
            counts["moved"] += 1
            if verbose:
                print(f"  Moved: {src_path} -> {target_path}")
        except FileNotFoundError:
            print(f"  Failed (file disappeared): {src_path}")
            counts["failed"] += 1
        except PermissionError:
            print(f"  Failed (permission denied): {src_path}")
            counts["failed"] += 1
        except OSError as error:
            print(f"  Failed: {src_path} ({error})")
            counts["failed"] += 1
    return counts