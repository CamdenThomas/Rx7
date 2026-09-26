// Which device this is decides how the record is reached; nothing else in the app knows.

import type { Platform } from './types';

export type { Platform } from './types';

const inTauri = () => typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;

export async function choosePlatform(): Promise<Platform> {
  const q = new URLSearchParams(location.search);
  if (inTauri()) {
    if (/Android/i.test(navigator.userAgent)) {
      const [{ phonePlatform }, { tauriKV }, http, { openUrl }] = await Promise.all([
        import('./phone'), import('./storage'), import('@tauri-apps/plugin-http'), import('@tauri-apps/plugin-opener'),
      ]);
      // A test build can point the phone at a stand-in GitHub (e2e/fake-github.mjs).
      // Two stores (plan P37): his answers, key and drafts in a small file written often; the
      // record's 6 MB cache in its own file, so no write of the cache can tear the other.
      const phone = await phonePlatform({
        kv: await tauriKV('answers.json'),
        cache: await tauriKV('cache.json'),
        fetch: http.fetch as typeof fetch,
        api: import.meta.env.VITE_RX7_API || undefined,
        raw: import.meta.env.VITE_RX7_RAW || undefined,
      });
      return { ...phone, open: (url) => void openUrl(url) };
    }
    const { desktopPlatform } = await import('./desktop');
    return desktopPlatform();
  }
  if (q.get('platform') === 'phone') {
    const [{ phonePlatform }, { browserKV }] = await Promise.all([import('./phone'), import('./storage')]);
    return phonePlatform({
      kv: browserKV('rx7-phone:'),
      fetch: window.fetch.bind(window),
      api: q.get('api') ?? undefined,
      raw: q.get('raw') ?? undefined,
    });
  }
  const { webPlatform } = await import('./web');
  return webPlatform({ fixture: q.get('fixture') ?? '/fixture/export.json', fakeClaude: q.get('claude') === 'fake' });
}
