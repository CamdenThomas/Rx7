# Playbook: session - one hour of the library's parsing (05-library, D-574, D-575, D-576)

Camden starts a fresh chat and says something like "begin the next hour of the library". You
run **one** session of `run_session.py`, check what it did, and report. You read no PDF, launch no
subagent and do no parsing yourself - the script and its `claude -p` workers do all of it. The
whole plan is `rx7.py doc library`; you do not need to read it for a normal session.

## 1. Start (CLAUDE.md §0)

```
git pull --rebase
python3 tools/rx7.py status -p 02-PROJECTS/05-library
```

**L8 open?** Camden asking you to begin is his go: record it once, with his words -
`python3 tools/rx7.py set 02-PROJECTS/05-library work L8 state=done "result=<his words, verbatim>"`.

## 2. Look before you spend

```
python3 02-PROJECTS/05-library/tools/run_session.py --dry
```

It prints the items an hour would take, the predicted dollars and the worst case (every
worker at its cap). If he named limits ("30 minutes", "only Haiku", "$5 max"), they map to
`--minutes`, `--model haiku` and `--max-usd 5`. Otherwise use the defaults below.

## 3. Run it - in the background, once

One Bash call with `run_in_background: true` (the session outlives a foreground call's
10-minute limit):

```
python3 02-PROJECTS/05-library/tools/run_session.py --minutes 60 --workers 6 > /tmp/rx7-session.log 2>&1
```

Then **wait for the notification that it finished. Do not poll, do not sleep, do not read the log
while it runs** - every look re-reads your context and costs tokens for nothing. If Camden asks
how it is going, `tail -5 /tmp/rx7-session.log` once.

The script itself: claims the next item (most valuable first), hands it to a fresh `claude -p`
worker of the item's model (Haiku at low effort, Sonnet at medium) capped at the item's
`cap_usd`, writes the answer as facts and page statuses, records tokens and dollars, and after
the minutes starts nothing new, lets the running workers finish, runs `check`, commits, pushes,
and writes a log row.

## 4. After it ends (a few calls, no more)

1. `tail -20 /tmp/rx7-session.log` - the ledger: items done and failed, facts, dollars.
2. `git log --oneline -1` and `git status --short` - the session's commit is there and pushed. If
   the log says check refused or the push failed: `python3 tools/rx7.py check`, fix the rows it
   names (usually one bad fact - `rx7.py set` or `del` it), then commit
   `00-CAR/data 02-PROJECTS/05-library/data` and push.
3. Prediction against reality, by model:
   `python3 tools/rx7.py sql 02-PROJECTS/05-library "select model, count(*) n, round(sum(est_usd),3) est, round(sum(cost_usd),3) actual from queue where cost_usd<>'' group by model"`.
   If actual / est for a model is above 1.4 or under 0.6, adjust `FACT_TOKENS` / `THINK` (Haiku) or
   the image constant (Sonnet) in `build_queue.py`, then `python3 02-PROJECTS/05-library/tools/build_queue.py --reprice`.
4. Failed items: `python3 02-PROJECTS/05-library/tools/build_queue.py --review` (each becomes a Sonnet review item).
5. Spot-check two finished items: pick two `done` items from this session, print one page of each
   (`page.py text DOC-… N`) and its facts (`rx7.py sql 02-PROJECTS/05-library "select item,value,unit,context from facts where page='DOC-…'"`).
   A fact the page does not say, or a page's figures missing, is a defect in the worker text: fix
   `tools/doc/playbooks/parse.md` below its `---` and say so in the report.
6. Commit anything steps 3-5 changed (pathspecs, D-575 in the subject), push.

## 5. Report (CLAUDE.md §8)

```
DID        session sNNNN: N items done, N failed, N facts; queue N open of 1,229
SPENT      $actual against $predicted (Haiku x.xx, Sonnet x.xx)
CHANGED    cost model / worker text, if you changed them
RECORD     valid / N problems
PUSHED     the commits
NEXT       the next hour: --dry's forecast
```

## Never

- Never launch subagents (the Agent tool) - the workers are `claude -p` processes the script starts.
- Never run `run_session.py` twice at once, nor a second session before the first one's notification.
- Never edit `queue.csv`, `facts.csv` or `pages.csv` by hand; never re-run an item yourself.
- Never merge facts into 00-CAR (D-576: the overhaul, L3, is a separate task).
- Never start it from the Rx7 app's run button: an app-started run may run only `rx7.py`, so the script would be refused. A Claude Code chat or a terminal.
- Camden can also run step 3's command himself in a terminal; then do only §4 and §5.
