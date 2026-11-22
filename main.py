#!/usr/bin/env python3
"""Hand over the finished front page.

The grading sandbox mounts this repository read-only, so this program must
not create, rewrite, or rebuild anything inside the repository. Its only job
is to take the image that is already committed here and place an identical
copy in the writable directory the harness points at with
MAKEFUN_OUTPUT_DIR ("/output" when the variable is not set).

The picture itself is drawn by make_image.py during the build, never here.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_NAME = "entry.png"


def main() -> int:
    source = os.path.join(HERE, SOURCE_NAME)
    if not os.path.isfile(source):
        print("missing committed image: %s" % source, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, SOURCE_NAME)
    shutil.copyfile(source, target)
    print("delivered %s" % target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
