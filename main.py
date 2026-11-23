"""Hand the finished front page to the grader.

The image for this entry is already drawn and stored in this repository
as entry.png. All this program does is place a copy of that file where
the grader expects it. It creates nothing, draws nothing, and never
writes into the repository, so it runs fine on a read-only checkout.
"""

import os
import shutil

# The finished image, kept beside this file in the repository.
SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def deliver():
    """Copy the committed image into the grader's output folder."""
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(folder, exist_ok=True)
    destination = os.path.join(folder, "entry.png")
    shutil.copyfile(SOURCE, destination)
    print("delivered", destination)


if __name__ == "__main__":
    deliver()
