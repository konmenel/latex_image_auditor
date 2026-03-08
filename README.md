# LaTeX Image Auditor

A zero-dependency utility that finds and manipulates unused images in LaTeX projects.

## Installation

```bash
git clone https://github.com/konmenel/latex_image_auditor.git
cd latex_image_auditor
pip install .
```

## Running

```bash
latex-image-auditor [root]
```

or

```bash
latexaudit [root]
```

For an up-to-date help run

```bash
latexaudit -h
```

Output:

```console
usage: latexaudit [-h] [-e EXTENSIONS [EXTENSIONS ...]] [--include INCLUDE [INCLUDE ...]]
                  [--exclude EXCLUDE [EXCLUDE ...]] [-m DIR] [-d] [--dry-run] [-y] [-v]
                  [root]

LaTeX Image Auditor Pro - PhD Grade Asset Management

positional arguments:
  root                  The root directory of the LaTeX project (default: current directory)

options:
  -h, --help            show this help message and exit
  -e, --extensions EXTENSIONS [EXTENSIONS ...]
                        Space-separated list of image extensions to check (e.g. .png .pdf)
  --include INCLUDE [INCLUDE ...]
                        Patterns of .tex files to include (e.g. main.tex chapters/*.tex)
  --exclude EXCLUDE [EXCLUDE ...]
                        Patterns of .tex files or directories to exclude (e.g. build/*
                        old_versions/*)
  -m, --move-to DIR     Move unused images to this directory instead of just listing them
  -d, --delete          Permanently delete unused images from the disk
  --dry-run             Show what would happen without making any changes to the filesystem
  -y, --yes             Skip confirmation prompt when using --delete
  -v, --verbose         Display detailed scanning information
```

