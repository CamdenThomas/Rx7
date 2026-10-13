"""Where the found models' files live on this PC, for the scripts beside this file.

The scripts are 05-cad's (06-intake T2); the files they read and write are still in the
reference's folder, out of git, until 06-intake T3 moves them. These two lines name those
folders and nothing else does: T3 changes them and no other line.

Owns no table and no fact.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # the tree: found, model, 05-cad, 02-PROJECTS

LIBRARY = ROOT / "01-INTAKE/model/library"  # the free CAD library, one folder per cad row (D-418)
SA = ROOT / "01-INTAKE/model"  # the bought SA model (S-037) and what is built from it: out/, rx7-fb.glb


def rel(p) -> str:
    """A path as the record and the READMEs write it: from the tree root, forward slashes."""
    return Path(p).relative_to(ROOT).as_posix()
