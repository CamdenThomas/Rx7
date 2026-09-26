// Claude Code, from the app (D-406, CLAUDE.md §6.11). A run is one playbook for one project,
// with write access, one at a time, ending in the §8 report. A conversation (Explain, Discuss,
// the chat panel) is read-only and can go on for several turns.

import { app } from './app.svelte';
import type { Area, Block } from './model';
import type { ClaudeHandle, ClaudeLine, ClaudeOpts } from './platform/types';
import { toast } from './toast.svelte';

export interface FeedItem {
  kind: 'text' | 'tool' | 'note' | 'error';
  text: string;
}

export type Status = 'starting' | 'running' | 'done' | 'failed' | 'stopped';

/** One Claude Code process: its feed as it runs, and what it came to. */
export class Stream {
  items = $state<FeedItem[]>([]);
  partial = $state('');
  status = $state<Status>('starting');
  result = $state('');
  session: string | null = null;
  cost = $state<number | null>(null);
  #handle: ClaudeHandle | null = null;
  #done: Promise<void>;
  #finish!: () => void;

  constructor() {
    this.#done = new Promise((r) => (this.#finish = r));
  }

  get finished() {
    return this.#done;
  }

  attach(h: ClaudeHandle) {
    this.#handle = h;
    if (this.status === 'starting') this.status = 'running';
  }

  async stop() {
    await this.#handle?.stop();
  }

  take(line: ClaudeLine) {
    switch (line.type) {
      case 'system':
        if (line.subtype === 'init') this.session = String(line.session_id ?? '') || null;
        break;
      case 'stream_event': {
        const ev = line.event as { type: string; delta?: { type: string; text?: string } };
        if (ev.type === 'message_start') this.partial = '';
        if (ev.type === 'content_block_delta' && ev.delta?.type === 'text_delta') this.partial += ev.delta.text ?? '';
        break;
      }
      case 'assistant': {
        const content = ((line.message as { content?: unknown[] })?.content ?? []) as Record<string, unknown>[];
        for (const c of content) {
          if (c.type === 'text' && String(c.text).trim()) this.items = [...this.items, { kind: 'text', text: String(c.text) }];
          if (c.type === 'tool_use') this.items = [...this.items, { kind: 'tool', text: describeTool(String(c.name), c.input as Record<string, unknown>) }];
        }
        this.partial = '';
        break;
      }
      case 'result':
        this.result = String(line.result ?? '');
        this.session = String(line.session_id ?? '') || this.session;
        this.cost = typeof line.total_cost_usd === 'number' ? line.total_cost_usd : null;
        this.status = line.is_error ? 'failed' : 'done';
        break;
      case 'stderr':
        if (String(line.text ?? '').trim()) this.items = [...this.items, { kind: 'note', text: String(line.text) }];
        break;
      case 'exit':
        if (this.status === 'running' || this.status === 'starting') {
          this.status = line.code === 143 || line.code === 137 || line.code === null ? 'stopped' : line.code === 0 ? 'done' : 'failed';
        }
        this.partial = '';
        this.#finish();
        break;
    }
  }
}

function describeTool(name: string, input: Record<string, unknown> = {}): string {
  const s = (v: unknown) => String(v ?? '');
  const path = (v: unknown) => s(v).replace(/^.*?\/Rx7\//, '');
  switch (name) {
    case 'Bash':
      return `$ ${s(input.command).replace(/\s+/g, ' ').slice(0, 160)}`;
    case 'Read':
      return `Read ${path(input.file_path)}`;
    case 'Edit':
    case 'MultiEdit':
      return `Edited ${path(input.file_path)}`;
    case 'Write':
      return `Wrote ${path(input.file_path)}`;
    case 'Grep':
      return `Searched for “${s(input.pattern)}”`;
    case 'Glob':
      return `Listed ${s(input.pattern)}`;
    default:
      return name;
  }
}

async function launch(mode: 'run' | 'chat', prompt: string, session: string | null, into: Stream, opts: ClaudeOpts = {}) {
  const p = app.platform;
  if (!p?.canClaude) throw new Error('Claude runs on the desktop for now.');
  into.attach(await p.claude(mode, prompt, session, (l) => into.take(l), opts));
}

// ---------------------------------------------------------------- runs

export type Workflow = 'apply' | 'plan' | 'review' | 'parts' | 'new';

/** What a run may spend (plan P06). `quick` runs apply answers by the playbook; `design` runs
 *  plan, review and open projects. An empty model means Claude Code's own default. */
export type RunClass = 'quick' | 'design';
export interface RunSettings {
  model: string;
  effort: string;
  budget: number;
}
export const RUN_CLASS: Record<Workflow, RunClass> = { apply: 'quick', parts: 'quick', plan: 'design', review: 'design', new: 'design' };
export const RUN_CLASS_TITLE: Record<RunClass, string> = { quick: 'Apply answers and parts rounds', design: 'Plan, review and new projects' };
export const DEFAULT_RUN_SETTINGS: Record<RunClass, RunSettings> = {
  quick: { model: 'sonnet', effort: 'medium', budget: 2 },
  design: { model: '', effort: 'high', budget: 8 },
};

/** How the harness wants commands written; every short run lost a turn learning it. */
const HARNESS =
  'The tree is the working directory and the app pulled from GitHub just before starting you: do not pull again unless a push is refused. Write plain commands - no cd, no $?, no $VAR, no heredoc; one Bash call per step, with several rx7.py calls joined by && where they belong together. The harness shows you a non-zero exit code itself.';

/** His answers waiting, exactly as saved, so the run reads nothing to find them. */
function inboxFacts(areaName?: string): string {
  const rows = (app.snapshot?.inbox ?? []).filter(
    (a) => ['block', 'pick', 'work', 'drive'].includes(a.kind) && !a.pending && (!areaName || a.area === areaName),
  );
  if (!rows.length) return '';
  const line = (a: (typeof rows)[number]) =>
    `- ${a.area}/${a.id} · ${a.kind} ${a.target} · ${a.choice || '(no choice)'}` +
    (a.text ? ` · his words: "${a.text.replace(/\s+/g, ' ').slice(0, 400)}"` : '') +
    (a.context ? ' · a discussion rides along in context' : '');
  return `His answers waiting in the inbox (id · kind target · choice · words):\n${rows.map(line).join('\n')}`;
}

export interface RunRecord {
  id: string;
  workflow: Workflow;
  area: string;
  title: string;
  status: Status;
  result: string;
  started: string;
  ended?: string;
  cost?: number | null;
}

const WHAT: Record<Workflow, string> = {
  apply: 'CLAUDE.md §6.2 — apply his answers waiting in its inbox (his picks by §6.9 step 4, his work rows by §6.4, his drives by §6.7)',
  plan: 'CLAUDE.md §6.1 — plan: take agent rows from READY until none has a met gate',
  review: 'CLAUDE.md §6.5 — review, changing nothing but the findings',
  parts: 'CLAUDE.md §6.9 — a parts round',
  new: 'CLAUDE.md §6.8 — open a new project',
};

export const WORKFLOW_TITLE: Record<Workflow, string> = {
  apply: 'Apply answers',
  plan: 'Plan',
  review: 'Review',
  parts: 'Parts round',
  new: 'New project',
};

function runPrompt(w: Workflow, area: Area | undefined, extra: string) {
  const where = area ? ` for ${area.path}` : '';
  return [
    `You were started from the Rx7 app (CLAUDE.md §6.11). Run ${WHAT[w]}${where}.`,
    extra,
    w === 'apply' ? inboxFacts(area?.name) : '',
    HARNESS,
    'Follow CLAUDE.md exactly, commit and push as §6.10 says, and end with the §8 report — the app shows it to Camden as this run\'s result.',
  ].filter(Boolean).join('\n\n');
}

type Queued = { w: Workflow; area?: string; extra: string; title?: string; onEnd?: (status: Status, result: string) => void };

class Runs {
  current = $state<{ record: RunRecord; stream: Stream } | null>(null);
  history = $state<RunRecord[]>([]);
  settings = $state<Record<RunClass, RunSettings>>(structuredClone(DEFAULT_RUN_SETTINGS));
  #queue = $state<Queued[]>([]);
  #requested = new Set<string>();

  async load() {
    this.history = (await app.platform?.kv.get<RunRecord[]>('runs')) ?? [];
    const saved = await app.platform?.kv.get<Partial<Record<RunClass, RunSettings>>>('runSettings');
    if (saved) this.settings = { ...structuredClone(DEFAULT_RUN_SETTINGS), ...saved };
  }

  async setSettings(next: Record<RunClass, RunSettings>) {
    this.settings = next;
    await app.platform?.kv.set('runSettings', $state.snapshot(next));
  }

  /** The Claude Code options for one kind of run, from his settings. */
  optsFor(w: Workflow): ClaudeOpts {
    const s = this.settings[RUN_CLASS[w]];
    return { model: s.model || undefined, effort: s.effort || undefined, budget: s.budget || undefined, fallback: s.model ? undefined : 'sonnet' };
  }

  busy = $derived(this.current !== null && ['starting', 'running'].includes(this.current.stream.status));

  /** Runs waiting their turn behind the one that is going. */
  get queued() {
    return this.#queue.length;
  }

  start(w: Workflow, area?: string, extra = '', title?: string, onEnd?: Queued['onEnd']) {
    this.#queue.push({ w, area, extra, title, onEnd });
    void this.#next();
  }

  async #next() {
    if (this.busy || !this.#queue.length) return;
    const { w, area, extra, title, onEnd } = this.#queue.shift()!;
    const a = area ? app.area(area) : undefined;
    const record: RunRecord = {
      id: `${Date.now()}`, workflow: w, area: area ?? '', status: 'starting', result: '',
      title: title ?? `${WORKFLOW_TITLE[w]}${a ? ` · ${app.title(a.name)}` : ''}`, started: new Date().toISOString(),
    };
    const stream = new Stream();
    this.current = { record, stream };
    try {
      // The pull happens here, before Claude starts, never under it (D-413).
      await app.refresh(true);
      await launch('run', runPrompt(w, a, extra), null, stream, this.optsFor(w));
    } catch (e) {
      stream.items = [{ kind: 'error', text: e instanceof Error ? e.message : String(e) }];
      stream.take({ type: 'exit', code: 1 });
    }
    await stream.finished;
    const done = { ...record, status: stream.status, result: stream.result, ended: new Date().toISOString(), cost: stream.cost };
    this.history = [done, ...this.history].slice(0, 30);
    await app.platform?.kv.set('runs', $state.snapshot(this.history));
    toast(`${record.title}: ${stream.status === 'done' ? 'finished' : stream.status}.`, stream.status === 'done' ? 'ok' : 'warn');
    await app.refresh(true);
    onEnd?.(stream.status, stream.result);
    void this.#next();
  }

  /** Runs he asked for from the phone wait in the inbox as kind=run / kind=project (§6.11).
   *  Each request starts once, however often the record is read while it waits. */
  startRequested() {
    if (!app.platform?.canClaude) return;
    for (const a of app.snapshot?.inbox ?? []) {
      if (a.pending || this.#requested.has(`${a.area}/${a.id}`)) continue;
      if (a.kind === 'run' || a.kind === 'project') this.#requested.add(`${a.area}/${a.id}`);
      if (a.kind === 'run' && ['apply', 'plan', 'review', 'parts'].includes(a.target)) {
        this.start(a.target as Workflow, a.area,
          `He asked for this run from his phone (${a.at}); it is inbox row ${a.id} in ${app.area(a.area)?.path} — delete that row when the run is done.`);
      }
      if (a.kind === 'project') {
        this.start('new', undefined,
          `He asked for a new project from his phone (${a.at}), inbox row ${a.id} in 00-CAR. Its name: ${a.target}. His goal, in his words:\n\n${a.text}\n\nDelete that row once the area exists.`,
          `New project · ${a.target}`);
      }
    }
  }
}

export const runs = new Runs();

// ------------------------------------------------------------ conversations

export interface Message {
  who: 'you' | 'claude';
  text: string;
}

const READ_ONLY = 'You were started from the Rx7 app, read-only (CLAUDE.md §6.11): answer from the record, never write, never commit. Plain words, short paragraphs, no headings.';

export function blockText(b: Block): string {
  return [
    `Block ${b.id} in ${app.area(b.area)?.path ?? b.area}: ${b.title}`,
    `Ask: ${b.ask}`,
    `Why: ${b.why}`,
    `Options:\n${b.options.map((o) => `(${o.letter}) ${o.text}`).join('\n')}`,
    `Recommend: ${b.recommend}`,
    `Stops: ${b.stops}`,
  ].join('\n');
}

/** A read-only exchange with Claude that can run to several turns. */
export class Conversation {
  messages = $state<Message[]>([]);
  live = $state<Stream | null>(null);
  #session: string | null = null;

  constructor(private preface: string) {}

  get busy() {
    return !!this.live && ['starting', 'running'].includes(this.live.status);
  }

  async ask(text: string, hidden = false): Promise<string> {
    if (!hidden) this.messages = [...this.messages, { who: 'you', text }];
    const stream = new Stream();
    this.live = stream;
    const prompt = this.#session ? text : `${READ_ONLY}\n\n${this.preface}\n\n${text}`;
    try {
      await launch('chat', prompt, this.#session, stream);
      await stream.finished;
    } catch (e) {
      stream.items = [{ kind: 'error', text: e instanceof Error ? e.message : String(e) }];
    }
    this.#session = stream.session ?? this.#session;
    const reply = stream.result || stream.items.filter((i) => i.kind === 'text').map((i) => i.text).join('\n\n');
    const failed = stream.status === 'failed' || stream.items.some((i) => i.kind === 'error');
    const shown = failed ? `Claude could not answer: ${stream.items.find((i) => i.kind === 'error')?.text ?? 'it stopped.'}` : reply;
    if (!hidden) this.messages = [...this.messages, { who: 'claude', text: shown }];
    this.live = null;
    return failed ? '' : reply;
  }

  stop() {
    void this.live?.stop();
  }

  /** The discussion's key points, to travel with his answer (D-406 7.5). */
  async keyPoints(): Promise<string> {
    if (!this.messages.length) return '';
    return (await this.ask(
      'He is saving his answer now. List the key points of this discussion that should travel with it, as 1 to 5 short lines starting "- ", keeping his own words where he gave them. Output only those lines.',
      true,
    )).trim();
  }
}

export function explainPrompt(b: Block) {
  return `He pressed Explain on this block. Restate it in plain words for someone with no design in front of him, then give one short paragraph per option saying what it would mean for the car, starting each with its letter in parentheses. Under 250 words.\n\n${blockText(b)}`;
}
