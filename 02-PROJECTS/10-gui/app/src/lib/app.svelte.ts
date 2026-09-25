// The app's one source of state: the record as last read, and what this device knows about
// reaching it. Everything a screen shows is looked up here from the snapshot, never stored
// a second time.

import type { Answer, Area, Block, Decision, Pick, Snapshot, WorkRow } from './model';
import { choosePlatform, type Platform } from './platform';
import type { Draft, SaveOutcome, SyncInfo } from './platform/types';
import { toast } from './toast.svelte';

export interface ProjectSummary {
  area: Area;
  name: string;
  title: string;
  phase: string;
  icon: string;
  goal: string;
  done: number;
  total: number;
  waiting: { blocks: number; picks: number; work: number; total: number };
  answered: number;
  last?: { date: string; summary: string };
}

const titleOf = (area: Area) =>
  area.project.title ||
  area.name.replace(/^\d{2}-/, '').replace(/-/g, ' ').replace(/^./, (c) => c.toUpperCase());

class App {
  platform = $state<Platform | null>(null);
  snapshot = $state<Snapshot | null>(null);
  sync = $state<SyncInfo>({ online: true, busy: false, waiting: 0 });
  ready = $state(false);
  /** On the desktop, whether his answers are applied without a press (D-413; autoapply.svelte.ts). */
  autoApply = $state(false);
  error = $state<string | null>(null);

  areas = $derived(this.snapshot?.areas ?? []);
  projects = $derived(this.areas.filter((a) => a.kind === 'project'));
  car = $derived(this.snapshot?.tables.find((t) => t.area === '00-CAR' && t.table === 'vehicle'));

  /** The newest answer to each (area, target), whichever device it came from. */
  answers = $derived.by(() => {
    const m = new Map<string, Answer>();
    for (const a of this.snapshot?.inbox ?? []) {
      const k = `${a.area}/${a.target}`;
      const cur = m.get(k);
      if (!cur || a.at > cur.at) m.set(k, a);
    }
    return m;
  });

  summaries = $derived(this.projects.map((a) => this.summarise(a)));

  async start() {
    try {
      const platform = await choosePlatform();
      this.platform = platform;
      this.sync = platform.syncInfo();
      platform.onSync((s) => {
        const finished = this.sync.busy && !s.busy;
        this.sync = s;
        // A sync that ran in the background may have brought new rows; show them.
        if (finished && !s.error) void this.platform?.load(false).then((snap) => (this.snapshot = snap), () => undefined);
      });
      const cached = await platform.cached();
      if (cached) {
        this.snapshot = cached;
        this.ready = true;
      }
      await this.refresh(true);
    } catch (e) {
      this.error = e instanceof Error ? e.message : String(e);
    } finally {
      this.ready = true;
    }
  }

  /** Read the record again; with `sync`, bring the device in step with GitHub first. */
  async refresh(sync = false) {
    if (!this.platform) return;
    try {
      this.snapshot = await this.platform.load(sync);
      this.error = null;
    } catch (e) {
      if (!this.snapshot) this.error = e instanceof Error ? e.message : String(e);
      else toast(e instanceof Error ? e.message : String(e), 'warn');
    }
  }

  area(name: string): Area | undefined {
    return this.areas.find((a) => a.name === name);
  }

  title(name: string): string {
    const a = this.area(name);
    return a ? titleOf(a) : name;
  }

  answer(area: string, target: string): Answer | undefined {
    return this.answers.get(`${area}/${target}`);
  }

  blocks(area?: string): Block[] {
    const all = this.snapshot?.blocks ?? [];
    return area ? all.filter((b) => b.area === area) : all;
  }

  /** The picks that wait for his verdict, in the order they were proposed. */
  picks(area?: string): Pick[] {
    const all = (this.snapshot?.picks ?? []).filter((p) => p.verdict === 'proposed');
    return area ? all.filter((p) => p.area === area) : all;
  }

  pick(area: string, id: string): Pick | undefined {
    return this.snapshot?.picks.find((p) => p.area === area && p.id === id);
  }

  work(area: string): WorkRow[] {
    return (this.snapshot?.work ?? []).filter((w) => w.area === area);
  }

  decisions(area?: string): Decision[] {
    const all = this.snapshot?.decisions ?? [];
    return area ? all.filter((d) => d.area === area) : all;
  }

  decision(id: string): Decision | undefined {
    const all = (this.snapshot?.decisions ?? []).filter((d) => d.id === id);
    return all.find((d) => d.status !== 'inherited') ?? all[0];
  }

  /** His rows that he could do now and has not answered. */
  myReady(area: string): WorkRow[] {
    return this.work(area).filter((w) => w.owner === 'camden' && w.status === 'ready' && !this.answer(area, w.id));
  }

  summarise(a: Area): ProjectSummary {
    const work = this.work(a.name);
    const live = work.filter((w) => w.status !== 'dropped');
    const blocks = this.blocks(a.name).filter((b) => !this.answer(a.name, b.id)).length;
    const picks = this.picks(a.name).filter((p) => !this.answer(a.name, p.id)).length;
    const mine = this.myReady(a.name).length;
    const logs = (this.snapshot?.log ?? []).filter((l) => l.area === a.name);
    const last = logs.at(-1);
    return {
      area: a,
      name: a.name,
      title: titleOf(a),
      phase: a.project.phase ?? '',
      icon: a.project.icon ?? 'folder',
      goal: a.project.goal ?? '',
      done: live.filter((w) => w.status === 'done').length,
      total: live.length,
      waiting: { blocks, picks, work: mine, total: blocks + picks + mine },
      answered: (this.snapshot?.inbox ?? []).filter((x) => x.area === a.name && ['block', 'pick', 'work'].includes(x.kind)).length,
      last: last ? { date: last.date, summary: last.summary } : undefined,
    };
  }

  /** Save one answer. The draft is only cleared by the caller once this resolves. */
  async save(d: Draft): Promise<SaveOutcome | null> {
    if (!this.platform) return null;
    try {
      const out = await this.platform.save(d, localIso());
      await this.refresh(false);
      toast(
        out.state === 'committed'
          ? this.autoApply
            ? 'Saved. Claude applies it once you have been quiet for a minute and a half.'
            : 'Saved. It waits for Apply.'
          : out.state === 'saved'
            ? 'Saved in the tree. It is committed with your next answer.'
            : 'Saved on this phone. It is sent at the next connection.',
        out.state === 'committed' ? 'ok' : 'info',
      );
      return out;
    } catch (e) {
      toast(`Not saved: ${e instanceof Error ? e.message : String(e)}`, 'warn');
      return null;
    }
  }

  async withdraw(a: Answer) {
    if (!this.platform) return;
    try {
      await this.platform.withdraw(a);
      await this.refresh(false);
      toast('Answer withdrawn.', 'info');
    } catch (e) {
      toast(`Not withdrawn: ${e instanceof Error ? e.message : String(e)}`, 'warn');
    }
  }
}

/** Now, as a local time with its offset — what `inbox.at` holds. */
export function localIso(d = new Date()): string {
  const pad = (n: number) => String(Math.abs(n)).padStart(2, '0');
  const off = -d.getTimezoneOffset();
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` +
    `${off >= 0 ? '+' : '-'}${pad(Math.trunc(off / 60))}:${pad(off % 60)}`
  );
}

export const app = new App();
