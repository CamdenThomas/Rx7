// The Claude Code stream (lib/claude.svelte.ts Stream): the state machine that turns
// stream-json lines into the run's feed, report, cost and status (plan P43). It is what
// every run's outcome - and auto-apply's retry - hangs on.
import { describe, expect, it } from 'vitest';
import { Stream } from '../src/lib/claude.svelte';

describe('Stream.take', () => {
  it('records the session, the text, the tools, the report and the cost', () => {
    const s = new Stream();
    s.take({ type: 'system', subtype: 'init', session_id: 'sess-1' });
    s.take({ type: 'stream_event', event: { type: 'message_start' } });
    s.take({ type: 'stream_event', event: { type: 'content_block_delta', delta: { type: 'text_delta', text: 'Hel' } } });
    s.take({ type: 'stream_event', event: { type: 'content_block_delta', delta: { type: 'text_delta', text: 'lo' } } });
    expect(s.partial).toBe('Hello');
    s.take({ type: 'assistant', message: { content: [{ type: 'text', text: 'Hello' }, { type: 'tool_use', name: 'Bash', input: { command: 'python3 tools/rx7.py status' } }] } });
    expect(s.partial).toBe('');
    expect(s.items.map((i) => i.kind)).toEqual(['text', 'tool']);
    expect(s.items[1].text).toContain('rx7.py status');
    s.take({ type: 'result', subtype: 'success', result: 'DID  x', session_id: 'sess-1', total_cost_usd: 0.42 });
    expect(s.result).toBe('DID  x');
    expect(s.cost).toBe(0.42);
    expect(s.status).toBe('done');
    expect(s.session).toBe('sess-1');
  });

  it('a result flagged as an error is a failed run', () => {
    const s = new Stream();
    s.take({ type: 'result', is_error: true, result: "You've hit your session limit" });
    expect(s.status).toBe('failed');
    expect(s.result).toContain('session limit');
  });

  it('an exit with no result decides the status from the code', async () => {
    const ok = new Stream();
    ok.take({ type: 'exit', code: 0 });
    expect(ok.status).toBe('done');
    const bad = new Stream();
    bad.take({ type: 'exit', code: 1 });
    expect(bad.status).toBe('failed');
    const killed = new Stream();
    killed.take({ type: 'exit', code: 143 });
    expect(killed.status).toBe('stopped');
    await expect(killed.finished).resolves.toBeUndefined();
  });

  it('an exit after a result keeps the result status', () => {
    const s = new Stream();
    s.take({ type: 'result', result: 'ok', total_cost_usd: 0 });
    s.take({ type: 'exit', code: 1 });
    expect(s.status).toBe('done');
  });

  it('stderr lines become notes, blank ones are dropped', () => {
    const s = new Stream();
    s.take({ type: 'stderr', text: '   ' });
    s.take({ type: 'stderr', text: 'warning: something' });
    expect(s.items).toEqual([{ kind: 'note', text: 'warning: something' }]);
  });
});
