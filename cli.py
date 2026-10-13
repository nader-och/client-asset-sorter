"""Orena Asset Sorter - command-line entry point.

Sorts a client's WhatsApp dump folder into Orena Studio's standard
delivery structure (Images, Videos, Branding, Menu, ...).
Preview is the default; nothing moves without --apply.

Usage:
    python cli.py organize SOURCE DEST [--apply] [--config FILE] [--verbose]
    python cli.py stats SOURCE [--config FILE]
"""