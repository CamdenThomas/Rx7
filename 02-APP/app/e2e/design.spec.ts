// The Design page (D-505, M3D1) on the web build: a project with no scene says so plainly;
// the stub scene (tests/fixtures/design, served in place of a project's own) shows its parts,
// links, missing entries and notes, names the model that does not load and keeps the rest,
// isolates a part from the list, and opens a part's own view and a board's. The version-2
// stub (tests/fixtures/design/v2, D-514) adds the legs, the connectors by leg with their
// cavities, and the layer toggles.

import { existsSync, readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

const fixture = JSON.parse(readFileSync(new URL('../fixture/export.json', import.meta.url), 'utf8'));
const areas: string[] = fixture.areas.map((a: { name: string }) => a.name).filter((a: string) => /^\d\d-/.test(a));
const exported = (a: string) => existsSync(new URL(`../public/design/${a}/scene.json`, import.meta.url));
const bare = areas.filter((a) => !exported(a));
if (bare.length < 3) throw new Error('the test needs three projects with no exported design');
const [empty, stub, stub2] = bare;

/** Serve a fixture folder as a project's design folder (paths under it, nothing above). */
async function stubScene(page: Page, area = stub, dir = '') {
  await page.route(`**/design/${area}/**`, (route) => {
    const rest = decodeURIComponent(new URL(route.request().url()).pathname.split(`/design/${area}/`)[1] ?? '');
    const file = new URL(`../tests/fixtures/design/${dir}${rest}`, import.meta.url);
    if (!/^[\w.-]+(\/[\w.-]+)*$/.test(rest) || rest.includes('..') || !existsSync(file)) return route.fulfill({ status: 404, body: 'not found' });
    return route.fulfill({ body: readFileSync(file), contentType: rest.endsWith('.json') ? 'application/json' : 'model/gltf-binary' });
  });
}

test('a project with no design exported says so plainly', async ({ page }) => {
  await page.goto(`/?claude=fake#/p/${empty}/design`);
  await expect(page.getByText('No design exported for this project yet.')).toBeVisible();
  await expect(page.getByRole('navigation', { name: 'Project pages' }).getByRole('link', { name: 'Design' })).toHaveAttribute('aria-current', 'page');
});

test('the stub scene: lists, a model that fails named, isolate, a part alone, a board alone', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await stubScene(page);
  await page.goto(`/?claude=fake#/p/${stub}/design`);

  const parts = page.locator('details', { has: page.locator('summary', { hasText: 'Parts' }) });
  for (const n of ['Control unit (DCU)', 'PMU', 'Ground point', 'DCU carrier board']) await expect(parts).toContainText(n);
  await expect(page.getByRole('button', { name: /DP-DCU · DT13 13-way/ })).toBeVisible();
  await expect(page.getByText('cur-board: housing model')).toBeVisible();
  await expect(page.getByText('Places are provisional until the dash is measured (C4).')).toBeVisible();

  // The vendor model is absent: named, and the rest still drawn (or, with no WebGL, said).
  await expect(page.getByText(/Could not load PMU|cannot draw 3D/)).toBeVisible({ timeout: 20_000 });

  // Isolate from the list, then restore.
  await parts.getByRole('button', { name: /^PMU/ }).click();
  await expect(page.getByRole('region', { name: 'Isolated part' })).toContainText('provisional');
  await page.getByRole('button', { name: 'Show everything' }).click();
  await expect(page.getByRole('region', { name: 'Isolated part' })).toHaveCount(0);

  // A link isolates too.
  await page.getByRole('button', { name: /DP-DCU · DT13 13-way/ }).click();
  await expect(page.getByRole('region', { name: 'Isolated link' })).toContainText('13 ways');

  // The control unit alone: its case and insides toggle.
  await page.getByRole('link', { name: 'Control unit (DCU) alone' }).click();
  await expect(page).toHaveURL(new RegExp(`#/p/${stub}/design/control-unit$`));
  const insides = page.getByRole('button', { name: /^Insides/ });
  await expect(insides).toHaveAttribute('aria-pressed', 'true');
  await insides.click();
  await expect(insides).toHaveAttribute('aria-pressed', 'false');

  // Its board alone, top and bottom.
  await page.getByRole('link', { name: /DCU carrier board/ }).click();
  await expect(page).toHaveURL(new RegExp(`#/p/${stub}/design/cu-carrier$`));
  await page.getByRole('button', { name: 'Bottom' }).click();
  await expect(page.getByRole('button', { name: 'Bottom' })).toHaveAttribute('aria-pressed', 'true');

  await page.getByRole('link', { name: 'Assembly' }).click();
  await expect(page).toHaveURL(new RegExp(`#/p/${stub}/design$`));
  expect(errors).toEqual([]);
});

test('version 2: legs on, links off; connectors by leg open their cavities; a leg isolates', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await stubScene(page, stub2, 'v2/');
  await page.goto(`/?claude=fake#/p/${stub2}/design`);

  const parts = page.locator('details', { has: page.locator('summary', { hasText: 'Parts' }) });
  await expect(parts).toContainText('Control Unit Remote (CUR)');
  await expect(parts).toContainText('PMU-24');
  await expect(parts).not.toContainText('L1-S1 plug'); // connectors have their own list

  const layers = page.getByRole('group', { name: 'Layers' });
  await expect(layers.getByRole('button', { name: 'Legs' })).toHaveAttribute('aria-pressed', 'true');
  await expect(layers.getByRole('button', { name: 'Links' })).toHaveAttribute('aria-pressed', 'false');
  await expect(layers.getByRole('button', { name: 'Connectors' })).toHaveAttribute('aria-pressed', 'true');
  await layers.getByRole('button', { name: 'Links' }).click();
  await expect(layers.getByRole('button', { name: 'Links' })).toHaveAttribute('aria-pressed', 'true');

  const conns = page.locator('details', { has: page.locator('summary', { hasText: /^Connectors/ }) });
  await expect(conns.getByRole('button', { name: /^L1 Engine/ })).toBeVisible();
  await expect(conns.getByRole('button', { name: /^L3 Dash/ })).toBeVisible();

  // A housing: its two halves isolated, its cavities shown.
  await conns.getByRole('button', { name: /^L1-S1/ }).click();
  const housing = page.getByRole('region', { name: 'Isolated housing' });
  await expect(housing).toContainText('DT06-12S');
  await expect(housing.getByRole('table')).toContainText('Ignition feed');
  await expect(housing).toContainText('Engine end');

  // A leg, from its group in the list.
  await conns.getByRole('button', { name: /^L3 Dash/ }).click();
  await expect(page.getByRole('region', { name: 'Isolated leg' })).toContainText('RT12');

  // Every model loads (four connector halves from one file); nothing failed.
  await expect(page.getByRole('status').filter({ hasText: 'Could not load' })).toHaveCount(0);

  // The CUR alone: its receptacle's housing and cavities, and a Connectors toggle.
  await page.getByRole('link', { name: 'Control Unit Remote (CUR) alone' }).click();
  await expect(page.getByRole('button', { name: 'Connectors' })).toHaveAttribute('aria-pressed', 'true');
  await page.locator('details.housing summary', { hasText: 'L3-S1' }).click();
  await expect(page.locator('details.housing table')).toContainText('Wink left');
  expect(errors).toEqual([]);
});
