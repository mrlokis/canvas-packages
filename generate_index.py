#!/usr/bin/env python3
"""
Generate a static site from the 'packages' folder:
- Copies all files and folders to public/packages
- Creates an index.html in every directory listing its contents
- Creates a root index.html that points to public/packages/
"""

import os
import shutil
import pathlib
from datetime import datetime

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

def generate_index(directory_path, output_dir):
    """
    Generate index.html inside output_dir for the given directory_path.
    directory_path: absolute or relative path to the source directory (inside packages)
    output_dir: absolute path where the index.html will be written (inside public/packages)
    """
    # Get the list of items in the source directory
    items = []
    for item in sorted(directory_path.iterdir()):
        if item.name.startswith('.'):
            continue
        items.append(item)

    # Build the HTML
    html_lines = []
    html_lines.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory listing</title>
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
    <h1>📦 Contents of <code>{}</code></h1>
    <ul>
""".format(str(directory_path.relative_to(pathlib.Path("packages")))))

    for item in items:
        rel_name = item.name
        if item.is_dir():
            icon = "📁"
            css_class = "folder"
            href = f"{rel_name}/"
            # Count items in subfolder (optional)
            try:
                sub_count = sum(1 for _ in item.iterdir() if not _.name.startswith('.'))
                size_info = f" ({sub_count} item{'s' if sub_count != 1 else ''})" if sub_count else " (empty)"
            except OSError:
                size_info = ""
        else:
            icon = "📄"
            css_class = "file"
            href = rel_name
            size_bytes, mod_time = get_file_info(item)
            size_info = format_size(size_bytes) if size_bytes is not None else ""
            if mod_time:
                size_info += f" – {mod_time.strftime('%Y-%m-%d %H:%M')}"

        html_lines.append(f"""
        <li class="{css_class}">
            <span class="icon">{icon}</span>
            <a href="{href}">{rel_name}</a>
            <span class="meta">{size_info}</span>
        </li>""")

    html_lines.append("""
    </ul>
</div>
</body>
</html>""")

    # Write the index.html file
    output_index = output_dir / "index.html"
    with open(output_index, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

def main():
    # Define paths
    packages_src = pathlib.Path("packages")
    public_root = pathlib.Path("public")
    packages_dest = public_root / "packages"

    # Clean and prepare output directory
    if public_root.exists():
        shutil.rmtree(public_root)
    public_root.mkdir()

    if not packages_src.exists() or not packages_src.is_dir():
        # No packages folder – create a simple placeholder
        with open(public_root / "index.html", "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html><html><body><h1>No packages folder found</h1></body></html>""")
        return

    # Copy the entire packages tree to public/packages
    shutil.copytree(packages_src, packages_dest, dirs_exist_ok=True)

    # Walk the copied tree and generate index.html in every directory
    for root, dirs, files in os.walk(packages_dest):
        root_path = pathlib.Path(root)
        # Corresponding source path (to get file metadata and relative path for title)
        rel_path = root_path.relative_to(public_root)
        src_root = packages_src / rel_path.relative_to("packages") if rel_path != pathlib.Path("packages") else packages_src
        generate_index(src_root, root_path)

    # Generate root index.html (pointing to packages/)
    root_index = public_root / "index.html"
    with open(root_index, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Packages</title>
    <meta http-equiv="refresh" content="0; url=packages/">
    <style>
        body {{ font-family: sans-serif; margin: 2rem; }}
        a {{ color: #0366d6; }}
    </style>
</head>
<body>
    <p>Redirecting to <a href="packages/">packages/</a>...</p>
</body>
</html>""")

if __name__ == "__main__":
    main()