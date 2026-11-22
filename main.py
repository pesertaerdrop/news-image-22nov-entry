"""Deliver the Sunday 22 November 2026 front page.

The picture is drawn once, by hand, and committed as entry.png next to
this file. At grade time this program only carries that committed file
into the writable output directory (MAKEFUN_OUTPUT_DIR, or /output by
default). It never draws, never rebuilds and never writes into its own
directory, because the grader mounts the repository read-only.
No network, no randomness, no arguments.
"""

import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
PICTURE = os.path.join(BASE, "entry.png")


def deliver():
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")
    shutil.copyfile(PICTURE, target)
    print("delivered", target)


if __name__ == "__main__":
    deliver()
