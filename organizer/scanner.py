"""Reading the source folder: listing regular files and getting
file extensions.
"""

import os


def get_extension(filename):
    """Return the extension without the dot, in lowercase ("" if none)."""
    extension = os.path.splitext(filename)[1]
    return extension[1:].lower()


def scan_directory(path):
    """Return the sorted names of the regular files directly inside path.

    Skips hidden files (names starting with "."), symlinks and folders.
    """
    files = []
    for name in sorted(os.listdir(path)):
        full_path = os.path.join(path, name)
        if name.startswith("."):
            continue
        if os.path.islink(full_path):
            continue
        if not os.path.isfile(full_path):
            continue
        files.append(name)
    return files