// The screens, driven the way he would drive them, on the web build (a copy of the record,
// answers kept in the browser, a stand-in Claude). Runs at desktop and at phone size.

import { readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

// The open blocks come from the fixture, a copy of the live record: a block he answers is
// deleted, so a test that names one by id breaks on the next run.
const fixture = JSON.parse(readFileSync(new URL('../public/fixture/export.json', import.meta.url), 'utf8'));
const openBlocks: { area: string; id: string; recommended: string }[] = fixture.blocks;
const pair = (() => {
  for (const b of openBlocks) {
    const rest = openBlocks.filter((x) => x.area === b.area && x.id !== b.id);
    if (b.recommended && rest.length) return { area: b.area, first: b, others: rest.map((x) => x.id) };
  }
  throw new Error('the fixture needs an area with two open blocks, one of them with a recommendation');
})();
const blockUrl = (id: string) => `#/p/${pair.area}/blocks/${id}`;

const open = async (page: Page, hash: string) => {
  await page.goto(`/?claude=fake${hash}`);
  await page.evaluate(() => localStorage.clear());
  await page.goto(`/?claude=fake${hash}`);
};

test('home has exactly two ways in, and both lead somewhere', async ({ page }) => {
  await open(page, '#/');
  const tiles = page.locator('.tiles a');
  await expect(tiles).toHaveCount(2);
  await tiles.filter({ hasText: 'Projects' }).click();
  await expect(page.getByRole('heading', { name: 'What is being done to the car' })).toBeVisible();
  await page.goto('/?claude=fake#/');
  await page.locator('.tiles a').filter({ hasText: 'Manual' }).click();
  await expect(page.getByRole('heading', { name: 'Known faults' })).toBeVisible();
});

test('the Manual: car state, specs by category, the service log, and Set odo as an answer', async ({ page }) => {
  await open(page, '#/manual');
  await expect(page.getByRole('heading', { name: 'Due' })).toBeVisible();
  await expect(page.locator('.odo strong')).toContainText('mi');
  await page.getByRole('navigation', { name: 'Manual pages' }).getByRole('link', { name: 'Specs' }).click();
  await expect(page).toHaveURL(/#\/manual\/specs$/);
  await page.getByRole('button', { name: 'Brakes', exact: true }).click();
  await expect(page.locator('.group h2')).toHaveCount(1);
  await page.getByRole('navigation', { name: 'Manual pages' }).getByRole('link', { name: 'Service' }).click();
  await expect(page.getByRole('heading', { name: 'Service log' })).toBeVisible();
  await page.getByRole('button', { name: 'Set odo' }).click();
  await page.getByRole('dialog').locator('input').first().fill('999999');
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.locator('.odo')).toContainText('waiting to be filed');
});

test('the Manual: systems lead to a system, and a part name to its page', async ({ page }) => {
  await open(page, '#/manual/systems');
  const sys = page.locator('.tree .name').first();
  const name = (await sys.textContent())?.trim() ?? '';
  await sys.click();
  await expect(page.getByRole('heading', { name, exact: true })).toBeVisible();
  const part = page.locator('.parts .plink').first();
  const partName = (await part.textContent())?.trim() ?? '';
  await part.click();
  await expect(page).toHaveURL(/#\/manual\/part\/PT\d+$/);
  await expect(page.getByRole('heading', { name: partName, exact: true })).toBeVisible();
  // The crumbs lead back through the system.
  await expect(page.locator('nav').getByRole('link', { name, exact: true }).first()).toBeVisible();
});

test('a block is answered with an option and words, kept, changed and withdrawn', async ({ page }) => {
  await open(page, blockUrl(pair.first.id));
  await page.getByRole('radio').first().click();
  await page.getByPlaceholder(/Anything to add/).fill('Do it the weekend after the parts arrive.');
  // Leaving and coming back keeps the draft.
  await page.goto(`/?claude=fake#/p/${pair.area}/blocks`);
  await page.goto(`/?claude=fake${blockUrl(pair.first.id)}`);
  await expect(page.getByPlaceholder(/Anything to add/)).toHaveValue('Do it the weekend after the parts arrive.');
  await page.getByRole('button', { name: 'Save answer' }).click();
  await expect(page.getByText('Your answer — (a)')).toBeVisible();
  await expect(page.getByText('Do it the weekend after the parts arrive.')).toBeVisible();
  // The list and the Apply bar say so.
  await page.getByRole('button', { name: /List/ }).first().click();
  await expect(page.getByText('1 answer saved, waiting to be applied.')).toBeVisible();
  await expect(page.locator('.row').filter({ hasText: pair.first.id }).getByText(/Answered · \(a\)/)).toBeVisible();
  // Withdraw.
  await page.goto(`/?claude=fake${blockUrl(pair.first.id)}`);
  await page.getByRole('button', { name: /Withdraw/ }).click();
  await expect(page.getByRole('button', { name: 'Save answer' })).toBeVisible();
});

test('follow the recommendation is one tap, and next unanswered moves on', async ({ page }) => {
  await open(page, blockUrl(pair.first.id));
  const r = pair.first.recommended;
  await page.getByRole('button', { name: `Follow the recommendation (${r})` }).click();
  await expect(page.getByText(`Your answer — (${r})`)).toBeVisible();
  await page.getByRole('link', { name: /Next unanswered/ }).click();
  await expect(page).not.toHaveURL(new RegExp(`/${pair.first.id.replace('.', '\\.')}$`));
  expect(pair.others.some((id) => page.url().endsWith(`/${id}`))).toBe(true);
});

test('a pick needs a reason for no', async ({ page }) => {
  await open(page, '#/p/01-luxury/picks/PK021');
  await page.getByRole('radio', { name: /No/ }).click();
  const save = page.getByRole('button', { name: 'Save', exact: true });
  await expect(save).toBeDisabled();
  await page.getByPlaceholder(/Why not/).fill('Too bulky for the housing.');
  await save.click();
  await expect(page.getByText('Too bulky for the housing.')).toBeVisible();
});

test('his work rows are answered in the list: a check', async ({ page }) => {
  await open(page, '#/p/00-electrical/todo');
  const row = page.locator('.wrow').filter({ hasText: 'B2' }).first();
  await row.getByRole('button', { name: 'Done' }).click();
  await expect(row.getByText('Done', { exact: false })).toBeVisible();
  await expect(page.getByText('1 answer saved, waiting to be applied.')).toBeVisible();
});

test('search finds a decision by its words and opens it', async ({ page, isMobile }) => {
  test.skip(!!isMobile, 'the phone searches from its tab');
  await open(page, '#/');
  await page.keyboard.press('Control+k');
  await page.getByLabel('Search everything').fill('replaces the Markdown');
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/#\/d\/D-405/);
  await expect(page.getByRole('heading', { name: /The app replaces the Markdown pages/ })).toBeVisible();
});

test('a Claude run shows its feed and its report', async ({ page }) => {
  await open(page, '#/p/00-electrical/run');
  await page.locator('.offer').filter({ hasText: 'Plan' }).getByRole('button', { name: 'Run' }).click();
  await expect(page.locator('.report').first()).toContainText('PUSHED', { timeout: 15_000 });
  await expect(page.getByText('python3 tools/rx7.py status')).toBeVisible();
});

test('explain restates a block in plain words', async ({ page }) => {
  await open(page, blockUrl(pair.first.id));
  await page.getByRole('button', { name: 'Explain' }).click();
  await expect(page.getByText(/In plain words:/)).toBeVisible({ timeout: 10_000 });
});
