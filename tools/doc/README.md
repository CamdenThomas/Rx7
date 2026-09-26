# tools/doc — the playbooks and the long descriptions

`CLAUDE.md` holds every rule that binds every run. These files hold the rest, read on demand
(plan P24, 2026-09-26): `python3 tools/rx7.py playbook <name>` prints one playbook,
`python3 tools/rx7.py doc <topic>` one description. They were the sections of CLAUDE.md v3
that a run needed only when it was that kind of run; moving them out took the file every turn
loads from about 10,800 tokens to about 3,600.

| Print with | File | Was |
| --- | --- | --- |
| `rx7.py playbook plan` | `playbooks/plan.md` | §6.1 Plan |
| `rx7.py playbook apply` | `playbooks/apply.md` | §6.2 Apply his answers |
| `rx7.py playbook source` | `playbooks/source.md` | §6.3 Source |
| `rx7.py playbook build` | `playbooks/build.md` | §6.4 Build |
| `rx7.py playbook review` | `playbooks/review.md` | §6.5 Review |
| `rx7.py playbook complete` | `playbooks/complete.md` | §6.6 Complete |
| `rx7.py playbook service` | `playbooks/service.md` | §6.7 Log a service act |
| `rx7.py playbook new` | `playbooks/new.md` | §6.8 New project |
| `rx7.py playbook parts` | `playbooks/parts.md` | §6.9 A parts round |
| `rx7.py doc record` | `record.md` | §1 in full: pages, the Manual, drawings, tracks, the tool |
| `rx7.py doc work` | `work.md` | the two tracks and the car coming apart once |
| `rx7.py doc blocks` | `blocks.md` | §4 in full |
| `rx7.py doc ids` | `ids.md` | how block ids were renumbered |
| `rx7.py doc machine` | `machine.md` | §9: the machine, the toolchains, what is left of v2 |

The rules in CLAUDE.md win over anything here; a playbook says how, never whether.
