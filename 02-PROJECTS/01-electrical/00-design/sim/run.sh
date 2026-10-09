#!/bin/sh
# Run every sim deck (Y2). Each *.cir judges itself in its .control block and ends with
# `quit 0` (every corner within its limits) or `quit 1` (a corner out of limits, printed
# as "FAIL <deck> <corner> <measure>"). This script branches on those exit codes and on
# nothing else (CLAUDE.md R9). Exit 0 = every deck passed; 1 = a deck failed; 3 = ngspice
# missing. Needs ngspice (Fedora: sudo dnf install ngspice; Mac: brew install ngspice).
#
# Models: models/generic.lib holds the stand-in models every deck uses (each confirm
# against the vendor's file); the vendors' own files live under 01-REFERENCE/model/library/
# spice (not in git) and are listed, not included, in models/active.lib, which this writes.
cd "$(dirname "$0")" || exit 3
command -v ngspice >/dev/null 2>&1 || { echo "ngspice not found - Fedora: sudo dnf install ngspice · Mac: brew install ngspice"; exit 3; }

VENDOR=../../../../01-REFERENCE/model/library/spice
{
  echo "* active.lib - written by run.sh; do not edit"
  echo ".include generic.lib"
  if [ -d "$VENDOR" ]; then
    echo "* vendor models on this machine (01-REFERENCE sources S-491.., not included: their"
    echo "* subcircuit names and PSpice syntax differ; a deck that wants one includes it by name):"
    for f in "$VENDOR"/*/*; do case "$f" in *SOURCE.txt) ;; *) echo "*   $f";; esac; done
  fi
} > models/active.lib

rc=0
passed=0
total=0
for deck in *.cir; do
  [ -f "$deck" ] || continue
  echo "== $deck"
  if ngspice -b "$deck" 2>&1 | grep -E "^(PASS|FAIL|INFO)"; then :; fi
  ngspice -b "$deck" >/dev/null 2>&1
  r=$?
  total=$((total + 1))
  if [ "$r" -eq 0 ]; then echo "   passed"; passed=$((passed + 1)); else echo "   FAILED (ngspice rc $r)"; rc=1; fi
done
# the last result, for `rx7.py status` (Y9): passed total date - not in git
echo "$passed $total $(date +%Y-%m-%d)" > .results
exit $rc
