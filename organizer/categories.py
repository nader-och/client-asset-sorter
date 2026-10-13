"""Category rules: default extension and keyword maps, client config
loading and validation, and deciding which category a file belongs to.
"""

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