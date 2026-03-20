#!/usr/bin/env python3
"""
Generate an HTML index page listing the contents of the 'packages' folder.
"""

import os
import pathlib
from datetime import datetime
import stat

def format_size(size_bytes):
    """Convert bytes to a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_file_info(path):
    """Return (size, modified_time) for a file."""
    try:
        s = os.stat(path)
        return s.st_size, datetime.fromtimestamp(s.st_mtime)
    except OSError:
        return None, None

def main():
    # HTML header
    print("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Packages listing</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            margin: 2rem;
            background: #f6f8fa;
            color: #24292f;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        h1 {
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3rem;
        }
        ul {
            list-style: none;
            padding-left: 0;
        }
        li {
            margin: 0.5rem 0;
            padding: 0.25rem 0;
            border-bottom: 1px solid #eaecef;
            display: flex;
            align-items: center;
        }
        .icon {
            font-size: 1.2rem;
            margin-right: 0.75rem;
            width: 1.5rem;
            text-align: center;
        }
        a {
            text-decoration: none;
            color: #0969da;
            flex: 1;
        }
        a:hover {
            text-decoration: underline;
        }
        .meta {
            font-size: 0.8rem;
            color: #57606a;
            margin-left: 1rem;
            white-space: nowrap;
        }
        .folder .icon { color: #e6a700; }
        .file .icon { color: #57606a; }
    </style>
</head>
<body>
<div class="container">
    <h1>📦 Contents of <code>packages/</code></h1>
    <ul>
""")

    packages_dir = pathlib.Path("packages")
    if not packages_dir.exists() or not packages_dir.is_dir():
        print("        <li>⚠️ The <code>packages</code> folder does not exist.</li>")
    else:
        # Gather items, ignoring hidden files/folders
        items = []
        for item in packages_dir.iterdir():
            if item.name.startswith('.'):
                continue
            items.append(item)

        # Sort: directories first, then files, alphabetically
        items.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

        for item in items:
            rel_path = item.name
            full_path = item
            if item.is_dir():
                icon = "📁"
                css_class = "folder"
                href = f"{rel_path}/"
                size_info = ""
                # Optionally count items in subfolder
                try:
                    sub_count = sum(1 for _ in item.iterdir() if not _.name.startswith('.'))
                    if sub_count:
                        size_info = f" ({sub_count} item{'s' if sub_count != 1 else ''})"
                    else:
                        size_info = " (empty)"
                except OSError:
                    size_info = ""
            else:
                icon = "📄"
                css_class = "file"
                href = rel_path
                size_bytes, mod_time = get_file_info(full_path)
                size_info = format_size(size_bytes) if size_bytes is not None else ""
                if mod_time:
                    size_info += f" – {mod_time.strftime('%Y-%m-%d %H:%M')}"

            print(f"""
        <li class="{css_class}">
            <span class="icon">{icon}</span>
            <a href="{href}">{rel_path}</a>
            <span class="meta">{size_info}</span>
        </li>""")

    print("""
    </ul>
</div>
</body>
</html>""")

if __name__ == "__main__":
    main()