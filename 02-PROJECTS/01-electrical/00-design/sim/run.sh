#!/bin/sh
# Run every sim deck (Y2). Each *.cir judges itself in its .control block and ends with
# `quit 0` (every corner within its limits) or `quit 1` (a corner out of limits, printed
# as "FAIL <deck> <corner> <measure>"). This script branches on those exit codes and on
# nothing else (CLAUDE.md R9). Exit 0 = every deck passed; 1 = a deck failed; 3 = ngspice
# missing. Needs ngspice (Fedora: sudo dnf install ngspice; Mac: brew install ngspice).
#
# Models: 01-REFERENCE/model/library/spice/<part>/*.lib are the vendors' own files and
# stay out of git; models/generic.lib is the stand-in. The decks include models/active.lib,
# which this script writes: the vendor files where they exist, generic.lib otherwise.
cd "$(dirname "$0")" || exit 3
command -v ngspice >/dev/null 2>&1 || { echo "ngspice not found - Fedora: sudo dnf install ngspice · Mac: brew install ngspice"; exit 3; }

VENDOR=../../../../01-REFERENCE/model/library/spice
{
  echo "* active.lib - written by run.sh; do not edit"
  if [ -d "$VENDOR" ] && ls "$VENDOR"/*/*.lib >/dev/null 2>&1; then
    echo "* vendor models from $VENDOR"
    for f in "$VENDOR"/*/*.lib; do echo ".include $f"; done
  fi
  echo ".include generic.lib"
} > models/active.lib

rc=0
for deck in *.cir; do
  [ -f "$deck" ] || continue
  echo "== $deck"
  if ngspice -b "$deck" 2>&1 | grep -E "^(PASS|FAIL|INFO)"; then :; fi
  ngspice -b "$deck" >/dev/null 2>&1
  r=$?
  if [ "$r" -eq 0 ]; then echo "   passed"; else echo "   FAILED (ngspice rc $r)"; rc=1; fi
done
exit $rc
