// The record as `rx7.py export` hands it over (tools/rx7.py, export_data). The app never
// computes a fact of its own: anything shown is one of these fields, or a count of them.

export interface Snapshot {
  version: number;
  generated: string;
  record: { valid: boolean; problems: string[] };
  areas: Area[];
  blocks: Block[];
  picks: Pick[];
  work: WorkRow[];
  decisions: Decision[];
  inbox: Answer[];
  log: LogRow[];
  tables: RawTable[];
  photos: string[];
  next: Record<string, string>;
}

export interface Area {
  path: string;
  name: string;
  prefix: string;
  kind: 'car' | 'reference' | 'project';
  project: Record<string, string>;
  tables: TableMeta[];
}

export interface TableMeta {
  name: string;
  purpose: string;
  key: string | null;
  rows: number;
  columns: { column: string; type: string; required: string; ref: string; note: string }[];
}

export interface Option {
  letter: string;
  text: string;
}

export interface Block {
  area: string;
  id: string;
  title: string;
  opened: string;
  age: number | null;
  ask: string;
  why: string;
  options: Option[];
  recommend: string;
  recommended: string;
  stops: string;
  touches: string[];
  unblocks: { area: string; id: string; item: string; owner: string }[];
  answered: boolean;
}

export interface Pick {
  area: string;
  id: string;
  part: string;
  part_item: string;
  part_spec: string;
  round: string;
  rank: string;
  product: string;
  maker_pn: string;
  vendor: string;
  url: string;
  usd: string;
  qty: string;
  meets: string;
  why: string;
  drawbacks: string;
  confidence: string;
  confirm: string;
  recommend: string;
  verdict: string;
  said: string;
  decided: string;
  decision: string;
}

export type WorkStatus = 'ready' | 'waiting' | 'done' | 'dropped';

export interface Blocker {
  ref: string;
  kind: 'bad' | 'phase' | 'work' | 'block' | 'area-work' | 'decision' | 'marked';
  label: string;
  owner?: string;
  state?: string;
  area?: string;
  answered?: boolean;
  freeze?: boolean;
}

export interface WorkRow {
  area: string;
  id: string;
  order: number;
  seq: number;
  stage: string;
  stage_title: string;
  item: string;
  owner: 'agent' | 'camden' | string;
  state: string;
  status: WorkStatus;
  gate: string[];
  blockers: Blocker[];
  note: string;
  track: '' | 'design' | 'build' | string;
  part: number;
  depth: number;
  reply: 'check' | 'value' | 'choice' | string;
  choices: string[];
  unit: string;
}

export interface Decision {
  area: string;
  id: string;
  system: string;
  title: string;
  date: string;
  status: 'standing' | 'superseded' | 'withdrawn' | 'inherited' | string;
  supersedes: string[];
  superseded_by: string;
  closes: string[];
  also: string;
  body: string;
  cited_by: string[];
  cited_in: { area: string; table: string; key: string }[];
}

export type AnswerKind = 'block' | 'pick' | 'work' | 'run' | 'project';

/** One of his answers, as it sits in an area's inbox (or, on the phone, still on its way). */
export interface Answer {
  area: string;
  id: string;
  target: string;
  kind: AnswerKind;
  choice: string;
  text: string;
  context: string;
  device: 'desktop' | 'phone';
  at: string;
  /** Only on the phone: saved on the device, not yet committed on GitHub. */
  pending?: boolean;
}

export interface LogRow {
  area: string;
  id: string;
  date: string;
  workflow: string;
  ids: string;
  summary: string;
}

export interface RawTable {
  area: string;
  table: string;
  columns: string[];
  rows: string[][];
}

export interface Commit {
  hash: string;
  subject: string;
  date: string;
  author: string;
}
