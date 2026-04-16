#!/usr/bin/env python3
"""
_apply_sanitize.py — Apply sanitize.yaml replacements to plugin skills/

Usage: python3 _apply_sanitize.py <dest_dir> <sanitize.yaml>

Called by publish-plugin.sh. Not intended for direct invocation.
"""

import sys
import os
import re


def parse_replacements(sanitize_path):
    """Parse sanitize.yaml into a list of (from_str, to_str) tuples."""
    replacements = []
    current_from = None
    in_replacements = False

    with open(sanitize_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')

        if line.strip() == 'replacements:':
            in_replacements = True
            i += 1
            continue

        if not in_replacements:
            i += 1
            continue

        # Match `  - from: "..."`
        m = re.match(r'^[^\S\n]*-[^\S\n]+from:[^\S\n]*"(.*)"[^\S\n]*$', line)
        if m:
            # Unescape YAML double-quoted string sequences
            current_from = m.group(1).replace('\\"', '"').replace('\\\\', '\\')
            i += 1
            continue

        # Match `    to: "..."` after a from:
        if current_from is not None:
            m = re.match(r'^[^\S\n]+to:[^\S\n]*"(.*)"[^\S\n]*$', line)
            if m:
                current_to = m.group(1).replace('\\"', '"').replace('\\\\', '\\')
                replacements.append((current_from, current_to))
                current_from = None
                i += 1
                continue
            # Non-to line resets from state (comment, blank, etc.)
            current_from = None

        i += 1

    return replacements


def apply_replacements(dest_dir, replacements):
    """Apply all replacements to .md and .json files in dest_dir."""
    files_modified = 0

    for root, dirs, files in os.walk(dest_dir):
        for fname in files:
            if not (fname.endswith('.md') or fname.endswith('.json')):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            for from_str, to_str in replacements:
                if not from_str:
                    continue
                if to_str == '':
                    # Remove lines containing from_str
                    lines = content.split('\n')
                    new_lines = [l for l in lines if from_str not in l]
                    content = '\n'.join(new_lines)
                else:
                    content = content.replace(from_str, to_str)

            if content != original:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_modified += 1

    return files_modified


def main():
    if len(sys.argv) != 3:
        print("Usage: _apply_sanitize.py <dest_dir> <sanitize.yaml>", file=sys.stderr)
        sys.exit(1)

    dest_dir = sys.argv[1]
    sanitize_path = sys.argv[2]

    replacements = parse_replacements(sanitize_path)
    print(f"[publish] Parsed {len(replacements)} sanitization rules from sanitize.yaml")

    files_modified = apply_replacements(dest_dir, replacements)
    print(f"[publish] Applied rules to {files_modified} files.")

    # Print a summary of applied rules
    for from_str, to_str in replacements:
        if to_str == '':
            label = f"[publish]   remove: '{from_str[:70]}'"
        else:
            label = f"[publish]   '{from_str[:55]}' → '{to_str[:55]}'"
        print(label)


if __name__ == '__main__':
    main()
