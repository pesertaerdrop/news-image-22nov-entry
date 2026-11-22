"""Entry point for the news-image-20261122 entry.

Builds the front page with make_image.py and copies the result into the
output directory (MAKEFUN_OUTPUT_DIR, or /output by default).
Deterministic, no network.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import make_image  # noqa: E402

SRC = os.path.join(HERE, "entry.png")


def main():
    make_image.build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    print("wrote", dst)


if __name__ == "__main__":
    main()
