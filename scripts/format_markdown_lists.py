#!/usr/bin/env python3
"""
format_markdown_lists.py - Ensures Markdown lists are preceded by blank lines.

In Markdown (specifically Python-Markdown used by MkDocs / Zensical), lists
must be separated from preceding paragraphs or block elements by an empty line;
otherwise, they are treated as plain inline text inside the same paragraph.

Usage:
  python3 scripts/format_markdown_lists.py [--check] [--fix] [FILES...]
"""

import argparse
import glob
import os
import re
import sys


def process_content(content: str) -> str:
    lines = content.splitlines(keepends=True)
    new_lines = []
    in_code = False
    in_list = False

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # Check code fence
        if stripped.startswith("```"):
            in_code = not in_code
            in_list = False
            new_lines.append(line)
            continue

        if in_code:
            new_lines.append(line)
            continue

        # Extract quote prefix (e.g. "> " or ">")
        qm = re.match(r"^(\s*(?:>\s*)+)(.*)$", line)
        if qm:
            quote_prefix = qm.group(1)
            remainder = qm.group(2)
        else:
            quote_prefix = ""
            remainder = line

        rem_strip = remainder.strip()

        if rem_strip == "":
            in_list = False
            new_lines.append(line)
            continue

        if (
            rem_strip.startswith("#")
            or rem_strip.startswith("|")
            or rem_strip.startswith("<!--")
            or rem_strip.startswith("---")
            or rem_strip.startswith("***")
        ):
            in_list = False
            new_lines.append(line)
            continue

        # Check list item marker
        lm = re.match(r"^(\s*)([-*+]|\d+[.)])(\s+.*)?$", remainder)
        if lm:
            if not in_list:
                # Transitioning into list: check preceding line
                if len(new_lines) > 0:
                    prev = new_lines[-1]
                    pqm = re.match(r"^(\s*(?:>\s*)+)(.*)$", prev)
                    if pqm:
                        p_prefix = pqm.group(1)
                        p_rem = pqm.group(2).strip()
                    else:
                        p_prefix = ""
                        p_rem = prev.strip()

                    # Standard text (outside blockquote)
                    if quote_prefix == "" and p_prefix == "":
                        if (
                            p_rem != ""
                            and not p_rem.startswith("#")
                            and not p_rem.startswith("|")
                            and not p_rem.startswith("<!--")
                            and not p_rem.startswith("---")
                            and not p_rem.startswith("***")
                        ):
                            new_lines.append("\n")
                    # Inside blockquote
                    elif quote_prefix != "" and p_prefix != "":
                        if (
                            p_rem != ""
                            and not p_rem.startswith("|")
                            and not p_rem.startswith("<!--")
                            and not p_rem.startswith("---")
                        ):
                            sep = quote_prefix.rstrip() + "\n"
                            if not sep.startswith(">"):
                                sep = "> " + sep
                            new_lines.append(sep)

            in_list = True
            new_lines.append(line)
            continue

        # Check indented continuation
        rem_indent = len(remainder) - len(remainder.lstrip())
        if in_list and rem_indent >= 2:
            new_lines.append(line)
        else:
            in_list = False
            new_lines.append(line)

    return "".join(new_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Format and lint Markdown list blank line spacing."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether files need formatting without modifying them. Exits with 1 if changes needed.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Format files in place.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to check/format (defaults to docs/*/*.md excluding docs/superpowers/**)",
    )

    args = parser.parse_args()

    target_files = args.files
    if not target_files:
        all_md = glob.glob("docs/**/*.md", recursive=True)
        target_files = sorted(
            [
                f
                for f in all_md
                if not f.startswith("docs/superpowers/")
                and "/superpowers/" not in f
            ]
        )

    if not target_files:
        print("No markdown files found.")
        sys.exit(0)

    files_needing_fix = []
    total_added_lines = 0

    for filepath in target_files:
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

        formatted = process_content(original)
        if original != formatted:
            diff_lines = len(formatted.splitlines()) - len(
                original.splitlines()
            )
            files_needing_fix.append((filepath, diff_lines))
            total_added_lines += diff_lines

            if args.fix:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(formatted)
                print(f"[FIXED] {filepath} (+{diff_lines} lines)")

    if args.check:
        if files_needing_fix:
            print(
                f"[FAIL] Found {len(files_needing_fix)} files with missing blank lines before lists (+{total_added_lines} total lines needed):"
            )
            for f, d in files_needing_fix:
                print(f"  - {f} (+{d} blank lines)")
            print("\nRun `python3 scripts/format_markdown_lists.py --fix` to automatically format them.")
            sys.exit(1)
        else:
            print("[PASS] All Markdown lists have proper blank line spacing.")
            sys.exit(0)
    elif not args.fix:
        if files_needing_fix:
            print(
                f"Found {len(files_needing_fix)} files that need formatting (+{total_added_lines} total lines):"
            )
            for f, d in files_needing_fix:
                print(f"  - {f} (+{d} blank lines)")
            print("\nPass --fix to format files in place, or --check for CI checking.")
        else:
            print("All files are properly formatted.")


if __name__ == "__main__":
    main()
