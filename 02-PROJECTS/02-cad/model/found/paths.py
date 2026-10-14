"""Where the found models' files live on this PC, for the scripts beside this file.

The scripts and the files they read and write are 02-cad's (D-573): both folders are under
02-cad/model, out of git. These two lines name those folders and nothing else does.

Owns no table and no fact.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # the tree: found, model, 02-cad, 02-PROJECTS

LIBRARY = ROOT / "02-PROJECTS/02-cad/model/library"  # the free CAD library, one folder per cad row (D-418)
SA = ROOT / "02-PROJECTS/02-cad/model/sa"  # the bought SA model (S-037) and what is built from it: out/, rx7-fb.glb


def rel(p) -> str:
    """A path as the record and the READMEs write it: from the tree root, forward slashes."""
    return Path(p).relative_to(ROOT).as_posix()
