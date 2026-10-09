// A small key-value store that survives the app being closed. In the Tauri apps it is the
// store plugin (a JSON file in the app's own data folder, written on every change); in a
// plain browser it is localStorage. Only the device's own things live here: settings,
// drafts, answers not yet sent, the last copy of the record. Never a fact of the record.

export interface KV {
  get<T>(key: string): Promise<T | undefined>;
  set(key: string, value: unknown): Promise<void>;
  delete(key: string): Promise<void>;
}

export function browserKV(prefix = 'rx7:'): KV {
  return {
    async get<T>(key: string) {
      const raw = localStorage.getItem(prefix + key);
      return raw === null ? undefined : (JSON.parse(raw) as T);
    },
    async set(key, value) {
      localStorage.setItem(prefix + key, JSON.stringify(value));
    },
    async delete(key) {
      localStorage.removeItem(prefix + key);
    },
  };
}

/** The same store on IndexedDB, for what is too big for localStorage's quota (the record's
 *  copy: files and snapshot together pass 9 MB). Plain-browser phone build only. */
export function idbKV(name = 'rx7-cache'): KV {
  const open = () =>
    new Promise<IDBDatabase>((resolve, reject) => {
      const r = indexedDB.open(name, 1);
      r.onupgradeneeded = () => r.result.createObjectStore('kv');
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => reject(r.error);
    });
  const run = async <T>(mode: IDBTransactionMode, f: (s: IDBObjectStore) => IDBRequest<T>) => {
    const db = await open();
    try {
      return await new Promise<T>((resolve, reject) => {
        const tx = db.transaction('kv', mode);
        const req = f(tx.objectStore('kv'));
        tx.oncomplete = () => resolve(req.result);
        tx.onerror = tx.onabort = () => reject(tx.error);
      });
    } finally {
      db.close();
    }
  };
  return {
    get: async <T>(key: string) => (await run('readonly', (s) => s.get(key))) as T | undefined,
    async set(key, value) {
      await run('readwrite', (s) => s.put(value, key));
    },
    async delete(key) {
      await run('readwrite', (s) => s.delete(key));
    },
  };
}

export async function tauriKV(file = 'rx7.json'): Promise<KV> {
  const { load } = await import('@tauri-apps/plugin-store');
  const store = await load(file, { autoSave: false, defaults: {} });
  return {
    get: (key) => store.get(key),
    async set(key, value) {
      await store.set(key, value);
      await store.save();
    },
    async delete(key) {
      await store.delete(key);
      await store.save();
    },
  };
}
