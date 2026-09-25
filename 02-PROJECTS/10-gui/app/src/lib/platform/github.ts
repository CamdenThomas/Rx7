// The phone's way to the record: the repository on GitHub (D-403). Reading needs no key while
// the repository is public; writing his answers needs a fine-grained token he makes for this
// one repository, with "Contents: read and write".

export type Fetch = (input: string, init?: RequestInit) => Promise<Response>;

export interface Repo {
  owner: string;
  name: string;
  branch: string;
  token?: string;
}

export interface TreeEntry {
  path: string;
  sha: string;
  type: 'blob' | 'tree' | 'commit';
}

export class GitHubError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

const API = 'https://api.github.com';

export function github(repo: Repo, fetch: Fetch, api = API, raw = 'https://raw.githubusercontent.com') {
  const base = `${api}/repos/${repo.owner}/${repo.name}`;
  const headers = (json = false): Record<string, string> => ({
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    ...(repo.token ? { Authorization: `Bearer ${repo.token}` } : {}),
    ...(json ? { 'Content-Type': 'application/json' } : {}),
  });
  const call = async <T>(path: string, init: RequestInit = {}): Promise<T> => {
    const res = await fetch(`${base}${path}`, { ...init, headers: { ...headers(!!init.body), ...(init.headers ?? {}) } });
    if (!res.ok) {
      let why = res.statusText;
      try {
        why = ((await res.json()) as { message?: string }).message ?? why;
      } catch {
        /* the status says enough */
      }
      throw new GitHubError(res.status, why);
    }
    return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
  };

  return {
    /** The newest commit on the branch, with its tree and time. */
    async head() {
      const b = await call<{ commit: { sha: string; commit: { tree: { sha: string }; committer: { date: string } } } }>(
        `/branches/${encodeURIComponent(repo.branch)}`,
      );
      return { sha: b.commit.sha, tree: b.commit.commit.tree.sha, date: b.commit.commit.committer.date };
    },
    async tree(sha: string): Promise<TreeEntry[]> {
      const t = await call<{ tree: TreeEntry[]; truncated: boolean }>(`/git/trees/${sha}?recursive=1`);
      if (t.truncated) throw new GitHubError(0, 'the repository listing came back truncated');
      return t.tree;
    },
    /** A file's text at one commit, so every file of a sync is from the same moment. */
    async text(commit: string, path: string): Promise<string> {
      const url = `${raw}/${repo.owner}/${repo.name}/${commit}/${path.split('/').map(encodeURIComponent).join('/')}`;
      const res = await fetch(url, repo.token ? { headers: { Authorization: `Bearer ${repo.token}` } } : undefined);
      if (!res.ok) throw new GitHubError(res.status, `${path}: ${res.statusText}`);
      return res.text();
    },
    /** Create or replace one file with one commit. `sha` is the file's current blob, if it has one. */
    put(path: string, text: string, message: string, sha?: string) {
      return call<{ content: { sha: string }; commit: { sha: string } }>(`/contents/${encodePath(path)}`, {
        method: 'PUT',
        body: JSON.stringify({ message, content: base64(text), branch: repo.branch, ...(sha ? { sha } : {}) }),
      });
    },
    remove(path: string, message: string, sha: string) {
      return call<unknown>(`/contents/${encodePath(path)}`, {
        method: 'DELETE',
        body: JSON.stringify({ message, sha, branch: repo.branch }),
      });
    },
    /** The file's current blob sha on the branch, or undefined if it does not exist. */
    async sha(path: string): Promise<string | undefined> {
      try {
        const f = await call<{ sha: string }>(`/contents/${encodePath(path)}?ref=${encodeURIComponent(repo.branch)}`);
        return f.sha;
      } catch (e) {
        if (e instanceof GitHubError && e.status === 404) return undefined;
        throw e;
      }
    },
    async commits(path?: string, n = 20) {
      const q = new URLSearchParams({ sha: repo.branch, per_page: String(n), ...(path ? { path } : {}) });
      const list = await call<{ sha: string; commit: { message: string; author: { name: string; date: string } } }[]>(
        `/commits?${q}`,
      );
      return list.map((c) => ({
        hash: c.sha.slice(0, 7),
        subject: c.commit.message.split('\n')[0],
        date: c.commit.author.date,
        author: c.commit.author.name,
      }));
    },
    rawUrl: (commit: string, path: string) =>
      `${raw}/${repo.owner}/${repo.name}/${commit}/${path.split('/').map(encodeURIComponent).join('/')}`,
  };
}

export type GitHub = ReturnType<typeof github>;

function encodePath(path: string) {
  return path.split('/').map(encodeURIComponent).join('/');
}

/** UTF-8 safe base64 — his words may hold any character, and each must arrive as typed. */
export function base64(text: string): string {
  const bytes = new TextEncoder().encode(text);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

/** The files a sync needs: rx7.py, every area's tables and inbox, and the archive's ids. */
export function wanted(path: string): 'text' | 'name' | null {
  if (path === 'tools/rx7.py') return 'text';
  if (path.startsWith('99-ARCHIVE/')) {
    if (/\/(decisions|retired)\.csv$/.test(path)) return 'text';
    if (/\/D-\d+\.md$/.test(path)) return 'name';
    return null;
  }
  if (/^(00-CAR|01-REFERENCE|02-PROJECTS\/[^/]+)\/data\/(inbox\/)?[^/]+\.csv$/.test(path)) return 'text';
  if (/^01-REFERENCE\/photos\/.+\.(jpe?g|png|webp)$/i.test(path)) return 'name';
  return null;
}
