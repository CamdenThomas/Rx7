// The desktop app itself — the built binary, its Rust shell, rx7.py, git and the pre-commit
// hook — driven through WebDriver (tauri-driver) against a sandbox: a copy of the record in a
// throwaway HOME, pushing to a throwaway "GitHub". Nothing touches the real tree.
//
//   npx tauri build --no-bundle && node e2e/desktop.mjs [screenshot-dir]

import { execFileSync, spawn } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { makeRepo } from './fake-github.mjs';

const APP = join(import.meta.dirname, '..');
const TREE = join(APP, '..', '..', '..');
const BIN = join(APP, 'src-tauri', 'target', 'release', 'rx7');
const shots = process.argv[2];

// --- the sandbox: HOME/docs/storage/Rx7, a clone whose origin is a bare repo
const repo = makeRepo(TREE);
const home = join(repo.dir, '..', `${repo.dir.split('/').pop()}-home`);
const origin = join(home, 'origin.git');
const tree = join(home, 'docs', 'storage', 'Rx7');
mkdirSync(join(home, 'docs', 'storage'), { recursive: true });
execFileSync('git', ['clone', '-q', '--bare', repo.dir, origin]);
execFileSync('git', ['clone', '-q', origin, tree]);
cpSync(join(TREE, '.githooks'), join(tree, '.githooks'), { recursive: true });
const git = (...a) => execFileSync('git', a, { cwd: tree, encoding: 'utf8' }).trim();
git('config', 'user.name', 'Camden Thomas');
git('config', 'user.email', 'camden@example.invalid');
git('config', 'core.hooksPath', '.githooks');
writeFileSync(join(home, '.gitconfig'), '[user]\n\tname = Camden Thomas\n\temail = camden@example.invalid\n');

// --- WebDriver
const driver = spawn(join(process.env.HOME, '.cargo', 'bin', 'tauri-driver'), [], {
  env: { ...process.env, HOME: home },
  stdio: ['ignore', 'ignore', 'inherit'],
});
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const wd = async (method, path, body) => {
  const res = await fetch(`http://127.0.0.1:4444${path}`, { method, headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined });
  const j = await res.json();
  if (j.value?.error) throw new Error(`${path}: ${j.value.error} ${j.value.message}`);
  return j.value;
};

let failures = 0;
const check = (label, ok) => {
  console.log(`${ok ? 'PASS' : 'FAIL'} ${label}`);
  if (!ok) failures++;
};

try {
  for (let i = 0; i < 50; i++) {
    try {
      await fetch('http://127.0.0.1:4444/status');
      break;
    } catch {
      await sleep(200);
    }
  }
  const s = await wd('POST', '/session', { capabilities: { alwaysMatch: { 'tauri:options': { application: BIN } } } });
  const sid = s.sessionId;
  const js = (script, args = []) => wd('POST', `/session/${sid}/execute/sync`, { script, args });
  const until = async (label, script, ms = 20000) => {
    const end = Date.now() + ms;
    while (Date.now() < end) {
      if (await js(script).catch(() => false)) return true;
      await sleep(250);
    }
    check(label, false);
    return false;
  };
  const shot = async (name) => {
    if (!shots) return;
    mkdirSync(shots, { recursive: true });
    const png = await wd('GET', `/session/${sid}/screenshot`);
    writeFileSync(join(shots, `desktop-app-${name}.png`), Buffer.from(png, 'base64'));
  };

  await until('the record loads through rx7.py export', "return !!document.querySelector('.tiles')", 30000) && check('the record loads through rx7.py export', true);
  await sleep(1200);
  await shot('home');

  await js("location.hash = '#/p/00-electrical/blocks/00.29'");
  await until('the block opens', "return !!document.querySelector('.opt')");
  await js("document.querySelectorAll('.opt')[1].click()");
  const words = 'Toggles in a box — “belt and braces”.\nSecond line.';
  await js(
    "const t = document.querySelector('.answer textarea'); t.value = arguments[0]; t.dispatchEvent(new Event('input', { bubbles: true }));",
    [words],
  );
  await shot('block');
  await js("[...document.querySelectorAll('.answer .btn.primary')].find((b) => b.textContent.includes('Save answer')).click()");
  await until('the answer shows as saved', "return !!document.querySelector('.saved')");

  const file = join(tree, '02-PROJECTS/00-electrical/data/inbox/00.29~desktop.csv');
  check('rx7.py answer wrote the inbox file', existsSync(file));
  check('his words are in it byte for byte', existsSync(file) && readFileSync(file, 'utf8').includes('"Toggles in a box — “belt and braces”.\nSecond line."'));
  check('it was committed alone, with his message', git('log', '-1', '--format=%s') === 'Camden answered 00.29 (desktop)' && git('show', '--stat', '--format=', 'HEAD').split('\n').length === 2);
  let pushed = false;
  for (let i = 0; i < 40 && !pushed; i++) {
    pushed = execFileSync('git', ['log', '-1', '--format=%s'], { cwd: origin, encoding: 'utf8' }).trim() === 'Camden answered 00.29 (desktop)';
    if (!pushed) await sleep(250);
  }
  check('and pushed to GitHub in the background', pushed);
  execFileSync('python3', ['tools/rx7.py', 'check'], { cwd: tree });
  check('the record is valid with it', true);
  await shot('saved');

  // A phone answer arrives on GitHub; Sync brings it in.
  const other = join(home, 'phone');
  execFileSync('git', ['clone', '-q', origin, other]);
  mkdirSync(join(other, '02-PROJECTS/01-luxury/data/inbox'), { recursive: true });
  writeFileSync(join(other, '02-PROJECTS/01-luxury/data/inbox/PK021~phone.csv'),
    'id,target,kind,choice,text,context,device,at\nPK021~phone,PK021,pick,yes,,,phone,2026-09-24T20:00:00-06:00\n');
  execFileSync('git', ['-C', other, 'add', '-A']);
  execFileSync('git', ['-C', other, '-c', 'user.name=p', '-c', 'user.email=p@p', 'commit', '-q', '-m', 'Camden answered PK021 (phone)']);
  execFileSync('git', ['-C', other, 'push', '-q']);
  await js("document.querySelector('.sync').click()");
  await js("location.hash = '#/p/01-luxury/picks'");
  await until('the phone\'s answer arrives with Sync', "return [...document.querySelectorAll('.chip')].some((c) => c.textContent.trim() === 'Yes')");
  check('the phone\'s answer arrives with Sync', existsSync(join(tree, '02-PROJECTS/01-luxury/data/inbox/PK021~phone.csv')));
  await shot('picks');

  // Withdraw his desktop answer: the file goes, in its own commit.
  await js("location.hash = '#/p/00-electrical/blocks/00.29'");
  await until('the saved answer shows', "return !!document.querySelector('.saved')");
  await js("[...document.querySelectorAll('.saved .btn')].find((b) => b.textContent.includes('Withdraw')).click()");
  await until('withdrawn in the app', "return !document.querySelector('.saved')");
  check('withdrawing removes the file', !existsSync(file));
  check('in its own commit', git('log', '-1', '--format=%s') === 'Camden withdrew his answer to 00.29 (desktop)');

  await wd('DELETE', `/session/${sid}`);
} catch (e) {
  console.error(e);
  failures++;
} finally {
  driver.kill();
  repo.cleanup();
  rmSync(home, { recursive: true, force: true });
}
console.log(failures ? `\n${failures} failure(s)` : '\ndesktop: all pass');
process.exit(failures ? 1 : 0);
