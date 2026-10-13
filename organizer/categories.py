"""Category rules: default extension and keyword maps, client config
loading and validation, and deciding which category a file belongs to.
"""

import json
import os
import re

from organizer.scanner import get_extension

DEFAULT_EXTENSIONS = {
    "Images": ["jpg", "jpeg", "png", "webp", "heic", "gif"],
    "Videos": ["mp4", "mov", "3gp", "mkv"],
    "Audio": ["mp3", "m4a", "opus", "ogg", "wav"],
    "Documents": ["pdf", "docx", "doc", "txt", "xlsx", "pptx"],
    "Design": ["svg", "psd", "ai", "eps"],
    "Archives": ["zip", "rar", "7z"],
}

# Checked before the extension. The first matching keyword wins.
DEFAULT_KEYWORDS = {
    "logo": "Branding",
    "menu": "Menu",
}

MAX_CONFIG_SIZE = 100 * 1024  # 100 KB
ALLOWED_KEYS = ("client", "extensions", "keywords")
CATEGORY_PATTERN = r"[A-Za-z0-9][A-Za-z0-9 _-]{0,39}"
EXTENSION_PATTERN = r"[a-z0-9]{1,10}"
KEYWORD_PATTERN = r"[a-z0-9_-]{1,30}"


def build_extension_map(extensions):
    """Turn {category: [ext, ...]} into {ext: category} for fast lookup."""
    ext_map = {}
    for category, ext_list in extensions.items():
        for ext in ext_list:
            ext_map[ext] = category
    return ext_map


def get_category(filename, ext_map, keywords):
    """Return the category: keyword rules first, then extension, then Other."""
    name = filename.lower()
    for keyword, category in keywords.items():
        if keyword in name:
            return category
    return ext_map.get(get_extension(filename), "Other")


def is_valid_category_name(name):
    """Return True if name is a safe folder name: no slashes, dots or ../"""
    if not isinstance(name, str):
        return False
    return re.fullmatch(CATEGORY_PATTERN, name) is not None


def read_extensions(raw):
    """Validate the "extensions" section and return it with lowercase names."""
    if not isinstance(raw, dict):
        raise ValueError('"extensions" must look like {"Images": ["jpg"]}.')
    result = {}
    for category, ext_list in raw.items():
        if not is_valid_category_name(category):
            raise ValueError(f"Invalid category name: {category!r}")
        if not isinstance(ext_list, list):
            raise ValueError(f"Extensions for {category!r} must be a list.")
        clean = []
        for ext in ext_list:
            if not isinstance(ext, str):
                raise ValueError(f"Invalid extension in {category!r}: {ext!r}")
            ext = ext.lower()
            if not re.fullmatch(EXTENSION_PATTERN, ext):
                raise ValueError(f"Invalid extension in {category!r}: {ext!r}")
            clean.append(ext)
        result[category] = clean
    return result


def read_keywords(raw):
    """Validate the "keywords" section; return it with lowercase keywords."""
    if not isinstance(raw, dict):
        raise ValueError('"keywords" must look like {"logo": "Branding"}.')
    result = {}
    for keyword, category in raw.items():
        if not re.fullmatch(KEYWORD_PATTERN, keyword.lower()):
            raise ValueError(f"Invalid keyword: {keyword!r}")
        if not is_valid_category_name(category):
            raise ValueError(f"Invalid category for {keyword!r}: {category!r}")
        result[keyword.lower()] = category
    return result


def load_config(path):
    """Read a client config file and return (ext_map, keywords).

    Client rules are added on top of the defaults; on a conflict the
    client wins. Raises ValueError with a clear message on any bad input.
    """
    if not os.path.isfile(path):
        raise ValueError(f"Config file not found: {path}")
    if os.path.getsize(path) > MAX_CONFIG_SIZE:
        raise ValueError("Config file is too large (max 100 KB).")
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except UnicodeDecodeError:
        raise ValueError("Config file must be UTF-8 text.")
    except json.JSONDecodeError as error:
        raise ValueError(f"Config is not valid JSON: {error.msg} "
                         f"(line {error.lineno})")

    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON object: { ... }")
    for key in data:
        if key not in ALLOWED_KEYS:
            raise ValueError(f"Unknown config key: {key!r}")
    if not isinstance(data.get("client", ""), str):
        raise ValueError('"client" must be text.')

    client_extensions = read_extensions(data.get("extensions", {}))
    client_keywords = read_keywords(data.get("keywords", {}))

    ext_map = build_extension_map(DEFAULT_EXTENSIONS)
    ext_map.update(build_extension_map(client_extensions))
    keywords = dict(DEFAULT_KEYWORDS)
    keywords.update(client_keywords)
    return ext_map, keywords