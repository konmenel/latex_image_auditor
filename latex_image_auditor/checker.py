#!/bin/env python3
import argparse
import shutil
import fnmatch
from pathlib import Path

# ANSI Color codes for zero-dependency styling
CLR = {
    "HEADER": "\033[95m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "WARNING": "\033[93m",
    "FAIL": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "BLUE": "\033[94m",
}


def create_parser():
    """Creates the argument parser with support for root path, custom extensions,
    verbose logging, file quarantining, and deletion.
    """
    parser = argparse.ArgumentParser(
        description=(
            f"{CLR['BOLD']}LaTeX Image Auditor Pro{CLR['ENDC']} - PhD Grade Asset Management (AI-generated)."
            "\nFinds and manipulates unused images in tex files. The program expects the images in "
            "'Images' or 'images' directory by default."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="The root directory of the LaTeX project (default: current directory)",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        nargs="+",
        default=[".png", ".jpg", ".jpeg", ".pdf", ".svg", ".eps", ".tikz"],
        help="Space-separated list of image extensions to check (e.g. .png .pdf)",
    )
    parser.add_argument(
        "--img-dirs",
        nargs="+",
        default=["Images", "images"],
        help="Space-separated list of directories to search for images",
    )
    parser.add_argument(
        "--include",
        nargs="+",
        help="Patterns of .tex files to include (e.g. main.tex chapters/*.tex)",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Patterns of .tex files or directories to exclude (e.g. build/* old_versions/*)",
    )
    parser.add_argument(
        "-m",
        "--move-to",
        metavar="DIR",
        help="Move unused images to this directory instead of just listing them",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Permanently delete unused images from the disk",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making any changes to the filesystem",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation prompt when using --delete",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display detailed scanning information",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"{CLR['FAIL']}Error: '{root}' is not a valid directory.{CLR['ENDC']}")
        return 1

    # Feature Completion: Resolve all valid image directories and collect images
    found_img_dirs = []
    all_images = []
    exts = {
        e.lower() if e.startswith(".") else f".{e.lower()}" for e in args.extensions
    }

    for folder_name in args.img_dirs:
        target_path = root / folder_name
        if target_path.is_dir():
            found_img_dirs.append(target_path)
            # Find images within this specific directory
            all_images.extend(
                [p for p in target_path.rglob("*") if p.suffix.lower() in exts]
            )

    if not found_img_dirs:
        print(
            f"{CLR['FAIL']}Error: None of the specified image directories {args.img_dirs} found in {root}{CLR['ENDC']}"
        )
        return 1

    if not all_images:
        print(
            f"{CLR['WARNING']}No files with extensions {exts} found in {args.img_dirs}{CLR['ENDC']}"
        )
        return 0

    # Read the tex files
    all_tex_files = list(root.rglob("*.tex"))
    filtered_tex = []

    for tf in all_tex_files:
        rel_path = str(tf.relative_to(root))

        if args.include:
            if not any(fnmatch.fnmatch(rel_path, pat) for pat in args.include):
                continue

        if args.exclude:
            if any(fnmatch.fnmatch(rel_path, pat) for pat in args.exclude):
                continue

        filtered_tex.append(tf)

    if not filtered_tex:
        print(
            f"{CLR['FAIL']}Error: No .tex files found after applying filters.{CLR['ENDC']}"
        )
        return 1

    tex_content = ""
    if args.verbose:
        print(f"{CLR['BLUE']}Reading {len(filtered_tex)} LaTeX files...{CLR['ENDC']}")

    for tf in filtered_tex:
        try:
            tex_content += tf.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            if args.verbose:
                print(f"{CLR['WARNING']}Skipped {tf.name}: {e}{CLR['ENDC']}")

    # Perform the check
    unused = []
    print(
        f"{CLR['CYAN']}Auditing {len(all_images)} assets across {len(found_img_dirs)} directories...{CLR['ENDC']}\n"
    )

    for img in all_images:
        if img.stem not in tex_content and img.name not in tex_content:
            unused.append(img)

    # Report and post-check actions
    if not unused:
        print(
            f"{CLR['GREEN']}{CLR['BOLD']}Success:{CLR['ENDC']} Project is clean. All images are in use."
        )
        return 0

    print(f"{CLR['FAIL']}{CLR['BOLD']}Found {len(unused)} unused images:{CLR['ENDC']}")
    print("-" * 60)
    for item in sorted(unused):
        print(f" {CLR['WARNING']}UNUSED{CLR['ENDC']} {item.relative_to(root)}")
    print("-" * 60)

    if args.dry_run:
        print(
            f"{CLR['BLUE']}{CLR['BOLD']}DRY RUN MODE ENABLED - No changes will be saved.{CLR['ENDC']}"
        )

    if args.delete:
        if not args.yes and not args.dry_run:
            confirm = input(
                f"{CLR['BOLD']}{CLR['FAIL']}DANGER:{CLR['ENDC']} Delete {len(unused)} files? [y/N]: "
            ).lower()
            if confirm != "y":
                print(f"{CLR['BLUE']}Deletion aborted by user.{CLR['ENDC']}")
                return 0

        for item in unused:
            try:
                if args.dry_run:
                    print(
                        f" {CLR['CYAN']}[DRY-RUN]{CLR['ENDC']} Would delete: {item.relative_to(root)}"
                    )
                else:
                    item.unlink()
                    if args.verbose:
                        print(f" {CLR['FAIL']}DELETED{CLR['ENDC']} {item.name}")
            except Exception as e:
                print(
                    f" {CLR['FAIL']}ERROR{CLR['ENDC']} Could not process {item.name}: {e}"
                )

        if not args.dry_run:
            print(f"{CLR['GREEN']}Cleanup complete.{CLR['ENDC']}")

    elif args.move_to:
        move_base = Path(args.move_to).resolve()
        for item in unused:
            try:
                # Find which specific img_dir this file belongs to to maintain relative structure
                parent_img_dir = next(d for d in found_img_dirs if d in item.parents)

                item_rel_to_root = item.relative_to(root)
                item_rel_to_img_dir = item.relative_to(parent_img_dir)

                # If multiple img_dirs exist, we nest them in the destination to avoid collisions
                if len(found_img_dirs) > 1:
                    dest_path = move_base / parent_img_dir.name / item_rel_to_img_dir
                else:
                    dest_path = move_base / item_rel_to_img_dir

                if args.dry_run:
                    print(
                        f" {CLR['CYAN']}[DRY-RUN]{CLR['ENDC']} Would move: {item_rel_to_root} -> {dest_path}"
                    )
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(dest_path))
                    if args.verbose:
                        print(
                            f" {CLR['GREEN']}MOVED{CLR['ENDC']} {item_rel_to_root} -> {dest_path}"
                        )
            except Exception as e:
                print(
                    f" {CLR['FAIL']}ERROR{CLR['ENDC']} Could not move {item.name}: {e}"
                )

        if not args.dry_run:
            print(
                f"{CLR['GREEN']}Quarantine complete: structure preserved in {move_base}{CLR['ENDC']}"
            )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
