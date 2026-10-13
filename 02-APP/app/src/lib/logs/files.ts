// Where the pulled logs live on this device (02-APP BL2, BL3): `app_data_dir()/logs/<seq>/`,
// one folder per drive as on the ICU's card (electrical log_files LF01), written by the shell
// (src-tauri/src/logs.rs). Out of git and out of the tree: the raw logs stay on the device
// that pulled them until a second home is named (D-478, 02-APP P55, open).

export type LogName = 'summary.bin' | 'thin.bin' | 'full.bin' | 'digest.json';

export interface LogFiles {
  /** the folder, for the screen to say */
  where(): Promise<string>;
  /** Write at `offset` and cut the file there (append at the end, or start again at 0). */
  write(seq: number, name: LogName, offset: number, bytes: Uint8Array): Promise<number>;
  read(seq: number, name: LogName): Promise<Uint8Array>;
  size(seq: number, name: LogName): Promise<number>;
  list(): Promise<number[]>;
}

export async function tauriFiles(): Promise<LogFiles> {
  const { invoke } = await import('@tauri-apps/api/core');
  return {
    where: () => invoke<string>('logs_root'),
    write: (seq, name, offset, bytes) => invoke<number>('logs_write', { seq, name, offset, data: Array.from(bytes) }),
    read: async (seq, name) => new Uint8Array(await invoke<ArrayBuffer>('logs_read', { seq, name })),
    size: (seq, name) => invoke<number>('logs_size', { seq, name }),
    list: () => invoke<number[]>('logs_list'),
  };
}

/** The same in memory: the tests, and the browser build. */
export function memoryFiles(): LogFiles & { files: Map<string, Uint8Array> } {
  const files = new Map<string, Uint8Array>();
  const key = (seq: number, name: string) => `${String(seq).padStart(8, '0')}/${name}`;
  return {
    files,
    where: async () => '(memory)',
    async write(seq, name, offset, bytes) {
      const now = files.get(key(seq, name)) ?? new Uint8Array(0);
      if (offset > now.length) throw new Error(`${name} of drive ${seq} holds ${now.length} bytes; a write at ${offset} would leave a gap`);
      const next = new Uint8Array(offset + bytes.length);
      next.set(now.subarray(0, offset));
      next.set(bytes, offset);
      files.set(key(seq, name), next);
      return next.length;
    },
    read: async (seq, name) => files.get(key(seq, name))?.slice() ?? new Uint8Array(0),
    size: async (seq, name) => files.get(key(seq, name))?.length ?? 0,
    list: async () => [...new Set([...files.keys()].map((k) => Number(k.slice(0, 8))))].sort((a, b) => a - b),
  };
}
