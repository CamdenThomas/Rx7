---
name: rx7-overview
description: A short, broad design conversation about an Rx7 project or topic — for chat, not the CLI. Reads status and headings only, answers in a few sentences, writes nothing; a decision reached in chat is logged later by /rx7-answers. /rx7-overview <project|topic>.
---

# /rx7-overview `<project|topic>`

The one workflow that lives in the chat window. Its job is understanding — Camden's of the options, the agent's of the vision — not the record.

**Read:** `python tools/rx7.py status`; the project's `README.md` and the headings of `01-DESIGN/DESIGN.md` (`grep "^#"`); the packets Camden names. Nothing else unless he points at it.

**Register:** short — a few sentences, one idea each; options before detail; a drawing (Mermaid or a table) when a picture is shorter than a paragraph; numbers only when they decide something. No lists of everything; no restating documents.

**Write nothing to the tree.** When the conversation reaches a decision, end with one line: *"Say the word and I'll log it as a ruling: `D-… — <one line>`"* — and it is logged in the next `/rx7-answers` or `/rx7-plan` in the CLI, never here. If the conversation opens a question instead, say what the packet would ask; the CLI writes it.
