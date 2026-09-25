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
  /** The Manual (D-417): 00-CAR as the car is now, verified rows only. Absent in an old export. */
  manual?: Manual;
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

export type AnswerKind = 'block' | 'pick' | 'work' | 'run' | 'project' | 'drive';

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

// ---------------------------------------------------------------- the Manual (D-417)
// rx7.py manual_view(): every field below is computed there, from 00-CAR, and only shown here.

/** A 00-CAR row as the Manual hands it over: its columns, trimmed. */
export type Row = Record<string, string>;

export interface Odometer {
  miles: number | null;
  date: string;
  /** drive · set · service · vehicle (an undated figure) · '' (none at all) */
  source: string;
  ref: string;
}

export interface ManualSystem {
  id: string;
  name: string;
  parent: string;
  order: string;
  state: string;
  since: string;
  note: string;
  children: string[];
  parts: string[];
  specs: number;
}

export interface ManualZone {
  id: string;
  name: string;
  order: string;
  note: string;
  parts: string[];
}

export interface Fitting {
  service: string;
  date: string;
  miles: number | null;
}

export interface ManualPart {
  id: string;
  name: string;
  system: string;
  zone: string;
  factory: string;
  maker: string;
  part_no: string;
  factory_code: string;
  link: string;
  support: string;
  cad: string;
  photo: string;
  note: string;
  fitted: Fitting | null;
  specs: string[];
  service: string[];
  bought: { id: string; part: string; source: string }[];
}

export interface ManualSpec {
  id: string;
  category: string;
  item: string;
  value: string;
  unit: string;
  source: string;
  page: string;
  confidence: string;
  system: string;
  part: string;
  note: string;
}

export interface ManualService {
  id: string;
  date: string;
  mileage: string;
  work: string;
  items: string;
  parts: string;
  notes: string;
  fitted: string[];
}

export interface Due {
  last: Fitting | null;
  next_miles: number | null;
  next_date: string;
  status: 'overdue' | 'soon' | 'ok' | 'never' | 'each';
  miles_left?: number | null;
  days_left?: number | null;
}

export interface ManualInterval {
  id: string;
  item: string;
  every_miles: string;
  every_months: string;
  spec: string;
  source: string;
  note: string;
  due: Due;
}

export interface ManualDrive {
  id: string;
  date: string;
  odometer: string;
  kind: string;
  from: string;
  to: string;
  note: string;
  miles: number | null;
}

export interface ManualProcedure {
  id: string;
  system: string;
  title: string;
  when: string;
  tools: string;
  source: string;
  body: string;
}

export interface Held {
  table: string;
  key: string;
  label: string;
  reason: 'confirm' | 'unverified' | 'other-car';
  why: string;
}

export interface Manual {
  today: string;
  odometer: Odometer;
  vehicle: Row[];
  systems: ManualSystem[];
  zones: ManualZone[];
  parts: ManualPart[];
  specs: ManualSpec[];
  service: ManualService[];
  intervals: ManualInterval[];
  issues: Row[];
  drives: ManualDrive[];
  procedures: ManualProcedure[];
  sources: Record<string, { title: string; url: string; local_path: string }>;
  circuits: string[];
  held: Held[];
}
