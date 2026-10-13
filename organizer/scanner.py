"""Reading the source folder: listing regular files and getting
file extensions.
"""

import os


def get_extension(filename):
    """Return the extension without the dot, in lowercase ("" if none)."""
    extension = os.path.splitext(filename)[1]
    return extension[1:].lower()