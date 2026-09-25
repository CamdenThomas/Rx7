import type { Answer, AnswerKind, Commit, Snapshot } from '../model';
import type { KV } from './storage';

/** What he is saving: which row, and his choice and words exactly as he left them. */
export interface Draft {
  area: string;
  target: string;
  kind?: AnswerKind;
  choice: string;
  text: string;
  context: string;
}

/**
 * committed — in the record's history (desktop: committed and pushing; phone: on GitHub)
 * saved     — written into the tree, not yet committed (the hook refused; it goes with the next)
 * queued    — on this device only, sent at the next connection
 */
export interface SaveOutcome {
  state: 'committed' | 'saved' | 'queued';
  note?: string;
}

export interface SyncInfo {
  online: boolean;
  busy: boolean;
  /** Answers on this device not yet on GitHub (phone), or commits not yet pushed (desktop). */
  waiting: number;
  /** The newest the record shown is: a commit time on the phone, the export time on the desktop. */
  asOf?: string;
  error?: string;
  /** Desktop: files changed in the tree and not committed (someone is working in it). */
  dirty?: number;
}

export interface ClaudeHandle {
  id: string;
  stop(): Promise<void>;
}

export type ClaudeMode = 'run' | 'chat';

export interface Platform {
  kind: 'desktop' | 'phone' | 'web';
  /** Whether Claude can be reached from this device at all (D-403: the desktop, for now). */
  canClaude: boolean;
  kv: KV;
  /** The last copy of the record this device holds, at once and offline. */
  cached(): Promise<Snapshot | null>;
  /** The record as it is now. `sync` first brings the device in step with GitHub. */
  load(sync: boolean): Promise<Snapshot>;
  save(draft: Draft, at: string): Promise<SaveOutcome>;
  withdraw(answer: Answer): Promise<SaveOutcome>;
  /** Answers saved here and not yet on GitHub (phone only). */
  outbox(): Answer[];
  syncInfo(): SyncInfo;
  onSync(listener: (s: SyncInfo) => void): () => void;
  commits(path?: string, n?: number): Promise<Commit[]>;
  claude(mode: ClaudeMode, prompt: string, session: string | null, onLine: (e: ClaudeLine) => void): Promise<ClaudeHandle>;
  open(url: string): void;
  photo(path: string): string;
  /** Phone: the GitHub key that lets it send answers. */
  token?(): string;
  setToken?(token: string): Promise<void>;
  /** Desktop: the tree it works on. */
  treeRoot?(): Promise<string>;
  setTreeRoot?(path: string): Promise<string>;
}

/** One line of Claude Code's stream-json output, or the exit the shell adds at the end. */
export type ClaudeLine = { type: string; [k: string]: unknown };
