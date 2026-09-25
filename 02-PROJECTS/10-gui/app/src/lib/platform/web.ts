// The app in a plain browser, for development and tests: the record is an export file
// (made by `npm run fixture`), answers are kept in this browser only, and Claude is either
// absent or a stand-in that replies with canned lines — so every screen can be exercised and
// photographed without touching the real tree.

import type { Answer, Snapshot } from '../model';
import { browserKV } from './storage';
import type { ClaudeLine, Draft, Platform, SaveOutcome, SyncInfo } from './types';

export async function webPlatform(opts: { fixture: string; fakeClaude: boolean }): Promise<Platform> {
  const kv = browserKV('rx7-web:');
  const base = (await (await fetch(opts.fixture)).json()) as Snapshot;
  let answers = (await kv.get<Answer[]>('answers')) ?? [];
  const info: SyncInfo = { online: true, busy: false, waiting: 0, asOf: base.generated };

  const view = (): Snapshot => {
    const inbox = [...base.inbox.filter((a) => !answers.some((b) => b.area === a.area && b.id === a.id)), ...answers];
    const answered = new Set(inbox.map((a) => `${a.area}/${a.target}`));
    return { ...base, inbox, blocks: base.blocks.map((b) => ({ ...b, answered: answered.has(`${b.area}/${b.id}`) })) };
  };

  return {
    kind: 'web',
    canClaude: opts.fakeClaude,
    kv,
    cached: async () => view(),
    load: async () => view(),
    async save(d: Draft, at: string): Promise<SaveOutcome> {
      const kind = d.kind ?? (base.blocks.some((b) => b.id === d.target) ? 'block' : base.picks.some((p) => p.id === d.target) ? 'pick' : 'work');
      const a: Answer = { area: d.area, id: `${d.target}~desktop`, target: d.target, kind, choice: d.choice, text: d.text, context: d.context, device: 'desktop', at };
      answers = [...answers.filter((x) => !(x.area === a.area && x.id === a.id)), a];
      await kv.set('answers', answers);
      return { state: 'committed' };
    },
    async withdraw(a: Answer) {
      answers = answers.filter((x) => !(x.area === a.area && x.id === a.id));
      await kv.set('answers', answers);
      return { state: 'committed' };
    },
    outbox: () => [],
    syncInfo: () => info,
    onSync: () => () => undefined,
    commits: async () => [
      { hash: '93222d1', subject: '10-gui SPEC: his Notion answers copied in word for word (D-402)', date: '2026-09-24T18:31:00-06:00', author: 'Camden Thomas' },
      { hash: '0949470', subject: '10-gui: answer the spec sheet on Notion while remote (D-402)', date: '2026-09-24T16:02:00-06:00', author: 'Camden Thomas' },
    ],
    async claude(mode, prompt, _session, onLine) {
      const id = `fake-${Date.now()}`;
      let stopped = false;
      const say = (lines: ClaudeLine[], i = 0) => {
        if (stopped || i >= lines.length) return;
        setTimeout(() => {
          onLine(lines[i]);
          say(lines, i + 1);
        }, 120);
      };
      say(fakeLines(mode, prompt));
      return { id, stop: async () => void (stopped = true, onLine({ type: 'exit', code: 143 })) };
    },
    open: (url) => window.open(url, '_blank'),
    photo: (path) => `/__repo/${path}`,
  };
}

function fakeLines(mode: string, prompt: string): ClaudeLine[] {
  const text = mode === 'chat'
    ? `In plain words: ${prompt.split('\n').find((l) => l.startsWith('Ask:'))?.slice(4).trim() ?? 'this question'} Either way, nothing already bought changes.`
    : 'DID        R3\nDECIDED    —\nBLOCKED    —\nCHANGED    work R3\nRECORD     valid\nPUSHED     a1b2c3d Electrical: ladder margin budget (R3)\nNEXT       R4';
  const words = text.split(/(?<= )/);
  return [
    { type: 'system', subtype: 'init', session_id: 'fake-session' },
    ...(mode === 'run'
      ? [{ type: 'assistant', message: { content: [{ type: 'tool_use', name: 'Bash', input: { command: 'python3 tools/rx7.py status' } }] } }]
      : []),
    ...words.map((w) => ({ type: 'stream_event', event: { type: 'content_block_delta', delta: { type: 'text_delta', text: w } } })),
    { type: 'assistant', message: { content: [{ type: 'text', text }] } },
    { type: 'result', subtype: 'success', result: text, session_id: 'fake-session', total_cost_usd: 0 },
    { type: 'exit', code: 0 },
  ];
}
