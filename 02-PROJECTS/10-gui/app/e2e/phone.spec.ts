// The phone's whole path, against a stand-in GitHub holding a copy of the record: the record
// is fetched and read by rx7.py running as WebAssembly, an answer typed offline waits on the
// phone, and it is committed — his words byte for byte — once the connection is back.

import { expect, test } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { makeRepo, startFakeGitHub } from './fake-github.mjs';

const TREE = join(import.meta.dirname, '..', '..', '..', '..');
const PORT = 5199;
// The block comes from the fixture, a copy of the live record: a block he answers is deleted,
// so one named by id breaks on the next run. A project's block, so the URL is #/p/<name>/…
const fixture = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'public', 'fixture', 'export.json'), 'utf8'));
const areas: { path: string; name: string }[] = fixture.areas;
const block: { area: string; id: string; title: string } = fixture.blocks.find((b: { area: string }) =>
  areas.find((a) => a.name === b.area)?.path.startsWith('02-PROJECTS/'),
);
const AREA = areas.find((a) => a.name === block.area)?.path ?? '';
const INBOX = `${AREA}/data/inbox/${block.id}~phone.csv`;
const WORDS = 'Option (a), but keep the old key switch in a box — “just in case”.\nSecond line, 55.2 mm, µ ✓';

test.describe('the phone', () => {
  test.skip(({ viewport }) => (viewport?.width ?? 0) > 600, 'phone only');
  let repo: ReturnType<typeof makeRepo>;
  let gh: Awaited<ReturnType<typeof startFakeGitHub>>;

  test.beforeAll(async () => {
    repo = makeRepo(TREE);
    gh = await startFakeGitHub(repo, PORT);
  });
  test.afterAll(async () => {
    gh.server.close();
    repo.cleanup();
  });

  test('reads the record through rx7.py, answers offline, sends on reconnect', async ({ page, context }) => {
    const url = `/?platform=phone&api=http://localhost:${PORT}/api&raw=http://localhost:${PORT}/raw`;
    await page.goto(url);
    await page.evaluate(() => {
      localStorage.clear();
      localStorage.setItem('rx7-phone:token', JSON.stringify('test-token'));
    });
    await page.goto(url + `#/p/${block.area}/blocks/${block.id}`);

    // The record arrived and was read by the real rx7.py inside the page.
    await expect(page.getByText(block.title, { exact: false }).first()).toBeVisible({ timeout: 60_000 });

    // Offline — GitHub cannot be reached: the answer is kept on the phone. (The app's own files
    // are on the phone, so only the network to GitHub is cut.)
    const cut = (r: import('@playwright/test').Route) => r.abort('internetdisconnected');
    await context.route(`http://localhost:${PORT}/**`, cut);
    await page.evaluate(() => {
      Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => false });
      window.dispatchEvent(new Event('offline'));
    });
    await page.getByRole('radio').first().click();
    await page.getByPlaceholder(/Anything to add/).fill(WORDS);
    await page.getByRole('button', { name: 'Save answer' }).click();
    await expect(page.getByText(/Saved on this phone|Not saved/)).toBeVisible();
    await expect(page.getByText(/Saved on this phone/)).toBeVisible();
    await expect(page.getByText(/on this phone, sent at the next connection/)).toBeVisible();
    expect(gh.exists(INBOX)).toBe(false);

    // It survives the app being closed and opened again while still offline.
    await page.reload();
    await expect(page.getByText(/on this phone, sent at the next connection/)).toBeVisible({ timeout: 30_000 });

    // Back online: it is sent, as one commit holding exactly his words.
    await context.unroute(`http://localhost:${PORT}/**`, cut);
    await page.evaluate(() => window.dispatchEvent(new Event('online')));
    await expect.poll(() => gh.exists(INBOX), { timeout: 30_000 }).toBe(true);
    const file = readFileSync(join(repo.dir, INBOX), 'utf8');
    expect(file).toContain('"Option (a), but keep the old key switch in a box — “just in case”.\nSecond line, 55.2 mm, µ ✓"');
    expect(file.startsWith(`id,target,kind,choice,text,context,device,at\n${block.id}~phone,${block.id},block,a,`)).toBe(true);
    expect(repo.git('log', '-1', '--format=%s')).toBe(`Camden answered ${block.id} (phone)`);

    // The record is still valid with his answer in it.
    execFileSync('python3', [join(repo.dir, 'tools', 'rx7.py'), 'check'], { cwd: repo.dir });

    // And the phone now shows it as sent.
    await expect(page.getByText(/saved .* from the phone/)).toBeVisible({ timeout: 30_000 });
  });
});
