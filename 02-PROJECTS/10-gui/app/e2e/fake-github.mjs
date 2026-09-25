// A stand-in for GitHub, for testing the phone app end to end: the few API calls the phone
// makes (branch, tree, raw file, contents put/get/delete, commits), served from a throwaway
// git repository holding a copy of the record. Nothing here touches the real tree.

import { execFileSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { dirname, join, relative } from 'node:path';

/** A git repo with the record's data and rx7.py copied from `tree`. */
export function makeRepo(tree) {
  const dir = mkdtempSync(join(tmpdir(), 'rx7-fake-gh-'));
  const keep = (p) => {
    const r = relative(tree, p);
    if (r === 'tools' || r === 'tools/rx7.py') return true;
    if (/(^|\/)(node_modules|\.git|target|app)(\/|$)/.test(r)) return false;
    if (statSync(p).isDirectory()) return true;
    return /\/data\/.*\.csv$/.test(r) || /^99-ARCHIVE\/.*(decisions|retired)\.csv$/.test(r) || /^99-ARCHIVE\/.*\/D-\d+\.md$/.test(r);
  };
  const walk = (src) => {
    for (const name of readdirSync(src)) {
      const p = join(src, name);
      if (!keep(p)) continue;
      if (statSync(p).isDirectory()) walk(p);
      else {
        const to = join(dir, relative(tree, p));
        mkdirSync(dirname(to), { recursive: true });
        cpSync(p, to);
      }
    }
  };
  walk(tree);
  const git = (...a) => execFileSync('git', a, { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  git('init', '-q', '-b', 'master');
  git('-c', 'user.name=t', '-c', 'user.email=t@t', 'add', '-A');
  git('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '-m', 'the record');
  return { dir, git, cleanup: () => rmSync(dir, { recursive: true, force: true }) };
}

export function startFakeGitHub(repo, port = 5199) {
  const { dir, git } = repo;
  const log = [];
  const send = (res, code, body) => {
    res.writeHead(code, {
      'Content-Type': typeof body === 'string' ? 'text/plain; charset=utf-8' : 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': '*',
      'Access-Control-Allow-Methods': 'GET, PUT, DELETE, OPTIONS',
    });
    res.end(typeof body === 'string' ? body : JSON.stringify(body));
  };
  const blob = (path) => {
    try {
      return git('rev-parse', `HEAD:${path}`);
    } catch {
      return undefined;
    }
  };
  const server = createServer(async (req, res) => {
    if (req.method === 'OPTIONS') return send(res, 204, '');
    const url = new URL(req.url, 'http://x');
    const p = decodeURIComponent(url.pathname);
    let body = '';
    for await (const c of req) body += c;
    log.push(`${req.method} ${p}`);
    let m;
    if ((m = p.match(/^\/api\/repos\/[^/]+\/[^/]+\/branches\/(.+)$/))) {
      const sha = git('rev-parse', 'HEAD');
      return send(res, 200, { commit: { sha, commit: { tree: { sha: git('rev-parse', 'HEAD^{tree}') }, committer: { date: git('log', '-1', '--format=%cI') } } } });
    }
    if ((m = p.match(/^\/api\/repos\/[^/]+\/[^/]+\/git\/trees\/(.+)$/))) {
      const tree = git('ls-tree', '-r', '-t', m[1]).split('\n').filter(Boolean).map((l) => {
        const [meta, path] = l.split('\t');
        const [, type, sha] = meta.split(' ');
        return { path, type, sha };
      });
      return send(res, 200, { tree, truncated: false });
    }
    if ((m = p.match(/^\/raw\/[^/]+\/[^/]+\/([0-9a-f]+)\/(.+)$/))) {
      try {
        return send(res, 200, execFileSync('git', ['show', `${m[1]}:${m[2]}`], { cwd: dir, encoding: 'utf8' }));
      } catch {
        return send(res, 404, 'Not Found');
      }
    }
    if ((m = p.match(/^\/api\/repos\/[^/]+\/[^/]+\/contents\/(.+)$/))) {
      const path = m[1];
      const have = blob(path);
      if (req.method === 'GET') return have ? send(res, 200, { sha: have }) : send(res, 404, { message: 'Not Found' });
      const b = JSON.parse(body || '{}');
      if (have && b.sha !== have) return send(res, 409, { message: `${path} does not match ${b.sha}` });
      if (!have && b.sha && req.method === 'PUT') return send(res, 422, { message: 'sha given for a new file' });
      const full = join(dir, path);
      if (req.method === 'PUT') {
        mkdirSync(dirname(full), { recursive: true });
        writeFileSync(full, Buffer.from(b.content, 'base64'));
        git('add', '--', path);
      } else if (req.method === 'DELETE') {
        if (!have) return send(res, 404, { message: 'Not Found' });
        git('rm', '-q', '--', path);
      }
      git('-c', 'user.name=phone', '-c', 'user.email=p@p', 'commit', '-q', '-m', b.message);
      return send(res, 200, { content: { sha: blob(path) ?? '' }, commit: { sha: git('rev-parse', 'HEAD') } });
    }
    if (p.match(/^\/api\/repos\/[^/]+\/[^/]+\/commits$/)) {
      const out = git('log', '-10', '--format=%H%x1f%s%x1f%an%x1f%cI');
      return send(res, 200, out.split('\n').map((l) => {
        const [sha, s, a, d] = l.split('\u001f');
        return { sha, commit: { message: s, author: { name: a, date: d } } };
      }));
    }
    return send(res, 404, { message: `no route ${p}` });
  });
  return new Promise((resolve) => server.listen(port, () => resolve({ server, log, exists: (f) => existsSync(join(dir, f)) })));
}
