"""Deliver the committed front page for news-image-20261122.

The graded program does exactly one thing: it takes the finished
``entry.png`` that lives beside this file in the repository and places
a byte-identical copy at ``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output``
when the variable is unset). It never draws, rebuilds, or writes into
the repository directory, so it runs cleanly when the repository is
mounted read-only.
"""

from __future__ import annotations

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    print(f"delivered {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
