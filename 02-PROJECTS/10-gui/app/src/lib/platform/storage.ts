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
