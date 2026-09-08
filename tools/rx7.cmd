@echo off
rem rx7 — the Rx7 launcher for the PyCharm terminal (tools\ is on the path once you run  tools\rx7 setup  once).
rem   rx7 status | check | build | lint [project] | triggers [--auto] | answers-list | tables <project> | find <project> <text>
rem   rx7 propose <name> --kind <kind> "<goal>"   rx7 plan <project> [--cycles N]   rx7 answers [project]   rx7 criticize <project>
rem   rx7 clean [project]   rx7 shop <project> "<what happened>"   rx7 complete <project> --system <name>   rx7 log "<what you did>"
rem   rx7 diff   rx7 chat        (a workflow opens Claude Code with its slash command; the rest run the tool directly)
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
if "%~1"=="" goto help
if /i "%~1"=="setup"    goto setup
if /i "%~1"=="status"   python tools\rx7.py status & goto :eof
if /i "%~1"=="check"    python tools\rx7.py -a check & goto :eof
if /i "%~1"=="build"    python tools\rx7.py -a build & goto :eof
if /i "%~1"=="lint"     if "%~2"=="" (python tools\rx7.py -a lint) else (python tools\rx7.py -p %2 lint) & goto :eof
if /i "%~1"=="triggers" python tools\triggers.py %2 & goto :eof
if /i "%~1"=="answers-list" python tools\answers.py & goto :eof
if /i "%~1"=="tables"   python tools\rx7.py -p %2 tables & goto :eof
if /i "%~1"=="find"     python tools\rx7.py -p %2 find %3 %4 %5 %6 & goto :eof
if /i "%~1"=="chat"     claude & goto :eof
if /i "%~1"=="shop"     claude "/rx7-build %2 %3 %4 %5 %6 %7 %8 %9" & goto :eof
claude "/rx7-%~1 %2 %3 %4 %5 %6 %7 %8 %9"
goto :eof
:setup
git config core.hooksPath .githooks
echo pre-commit hook installed (core.hooksPath = .githooks)
where claude >nul 2>nul || echo Claude Code is not on PATH — install it: npm install -g @anthropic-ai/claude-code
python -c "import wireviz" 2>nul || echo WireViz missing — pip install wireviz  (and Graphviz: winget install Graphviz.Graphviz)
goto :eof
:help
type "%~f0" | findstr /b "rem "
