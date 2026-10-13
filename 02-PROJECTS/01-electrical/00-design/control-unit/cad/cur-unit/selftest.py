"""The CUR mock-up's self-test, as its own command because freecadcmd takes a script's own
arguments only after `--pass`:

    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd selftest.py

Runs `make_unit.py --selftest`: every parameter set of `unit_params.SELFTEST` is rebuilt in memory
(no file is written) and held to the outcome stored with it - built clear, built with a failing
check, or refused in words. Exit 0 every set as expected; 1 an outcome differs; 3 a set crashed.
"""
import os
import runpy
import sys

sys.argv.append("--selftest")
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_unit.py"),
               run_name="__main__")
