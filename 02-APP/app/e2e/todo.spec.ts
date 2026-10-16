// The TODO page as a step-by-step manual (02-electrical D-533), driven the way he would, at
// desktop and phone size. The rows are a test project laid over the copy of the record
// (todo-fixture.ts) and handed to the page here: nothing is written to the tree.

import { readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';
import { AREA, withManual } from './todo-fixture';

const real = JSON.parse(readFileSync(new URL('../fixture/export.json', import.meta.url), 'utf8'));
const body = JSON.stringify(withManual(real));
// A real project with open rows and no brief on any of them: its page must read as it always has.
const plain: { name: string } | undefined = real.areas.find((a: { name: string; kind: string; tables: { name: string; rows: number }[] }) =>
  a.kind === 'project' && !a.tables.some((t) => t.name === 'briefs' && t.rows > 0) &&
  real.work.some((w: { area: string; status: string }) => w.area === a.name && (w.status === 'ready' || w.status === 'waiting')));

const open = async (page: Page, hash: string) => {
  await page.goto(`/?claude=fake${hash}`);
  await page.evaluate(() => localStorage.clear());
  await page.goto(`/?claude=fake${hash}`);
};
const row = (page: Page, id: string) => page.locator('.wrow').filter({ has: page.locator('.id', { hasText: new RegExp(`^${id}$`) }) });
const section = (page: Page, part: string) => page.locator(`.guide [data-part="${part}"]`);

test.beforeEach(async ({ page }) => {
  await page.route('**/fixture/export.json', (r) => r.fulfill({ contentType: 'application/json', body }));
});

test('the list is his rows as one numbered sequence, each with its goal, where, time and step count', async ({ page }) => {
  await open(page, `#/p/${AREA}/todo`);
  await expect(page.getByRole('button', { name: 'Start here' })).toBeVisible();
  // Mine only is on: the agent's row is not there, and the build row follows the design rows.
  await expect(page.getByLabel('Mine only')).toBeChecked();
  await expect(page.locator('.wrow .id')).toHaveText(['M1', 'M2', 'M3', 'M4']);
  await expect(page.locator('.wrow .no')).toHaveText(['1', '2', '3', '4']);

  const m1 = row(page, 'M1');
  await expect(m1.locator('.goal')).toHaveText('The test plug is pinned and every cavity checked.');
  await expect(m1.locator('.meta')).toContainText('bench');
  await expect(m1.locator('.meta')).toContainText('40 min');
  await expect(m1.locator('.meta')).toContainText('0 / 3 steps');
  // A row with a brief and no steps shows no step count; a row without a brief looks as it did.
  await expect(row(page, 'M4').locator('.goal')).toHaveText('The plug is in the car.');
  await expect(row(page, 'M4').locator('.meta')).not.toContainText('steps');
  await expect(row(page, 'M3').locator('.goal')).toHaveCount(0);
  await expect(row(page, 'M3').locator('.meta')).toHaveCount(0);
  await expect(row(page, 'M3')).toContainText('waits on');

  // The grouping by part and stage is still there.
  await expect(page.getByRole('heading', { name: /^Part 1/ })).toBeVisible();
  await expect(page.getByRole('heading', { name: /Stage E/ })).toBeVisible();

  await page.getByLabel('Mine only').uncheck();
  await expect(page.locator('.wrow .id')).toHaveText(['M1', 'M2', 'M3', 'A1', 'M4']);
  await expect(row(page, 'A1').locator('.no')).toHaveText('');
  // One track at a time is still a tap away, and the numbers do not restart.
  await page.getByRole('tab', { name: 'Build' }).click();
  await expect(page.locator('.wrow .id')).toHaveText(['M4']);
  await expect(row(page, 'M4').locator('.no')).toHaveText('4');
});

test('Start here opens the first row he can do, and the row opens on its brief and steps', async ({ page }) => {
  await open(page, `#/p/${AREA}/todo`);
  await page.getByRole('button', { name: 'Start here' }).click();
  await expect(page).toHaveURL(new RegExp(`#/p/${AREA}/todo/M1$`));

  await expect(page.locator('.focus .goal')).toHaveText('The test plug is pinned and every cavity checked.');
  const strip = page.locator('.strip');
  await expect(strip).toContainText('bench');
  await expect(strip).toContainText('40 min');
  await expect(strip).toContainText('No. 1 of 4 in the list');

  // The sections, in order.
  await expect(page.locator('.guide [data-part]')).toHaveCount(8);
  expect(await page.locator('.guide [data-part]').evaluateAll((els) => els.map((e) => (e as HTMLElement).dataset.part))).toEqual(
    ['before', 'tools', 'parts', 'know', 'steps', 'done', 'ifnot', 'record']);
  await expect(section(page, 'before').getByRole('checkbox')).toHaveCount(2);
  await expect(section(page, 'tools').locator('li')).toHaveCount(3);
  // A tool that is a parts row leads to that row.
  await expect(section(page, 'tools').getByRole('link', { name: 'P037' })).toHaveAttribute('href', `#/row/${AREA}/parts/P037`);

  // Parts by name, quantity and supplier; an id that resolves to nothing, as the bare id.
  const parts = section(page, 'parts').locator('li');
  await expect(parts).toHaveCount(2);
  await expect(parts.nth(0)).toContainText('ATC fuse block, 4-position');
  await expect(parts.nth(0)).toContainText('2 ea');
  await expect(parts.nth(0)).toContainText('Waytek · 45643');
  await expect(parts.nth(1)).toHaveText('P404');
  await expect(parts.nth(1).getByRole('link')).toHaveCount(0);

  // What to know: the fact, then where it comes from as a chip - a link where the app has a page.
  const know = section(page, 'know').locator('li');
  await expect(know).toHaveCount(5);
  await expect(know.nth(0).locator('.ftext')).toHaveText('Cavity 9 carries the headlight feed, red 18 AWG');
  await expect(know.nth(0).locator('a.src')).toHaveAttribute('href', `#/row/${AREA}/cavities/T1-S1%209`);
  await expect(know.nth(1).locator('a.src')).toHaveAttribute('href', '#/d/D-405');
  await expect(know.nth(2).locator('a.src')).toHaveAttribute('href', '#/row/00-CAR/parts/PT001');
  await expect(know.nth(3).locator('a.src')).toHaveAttribute('href', '#/row/00-CAR/sources/S-001');
  await expect(know.nth(4).locator('.src.confirm')).toHaveText('confirm');
  await expect(know.nth(4).locator('a.src')).toHaveCount(0);
  await expect(know.nth(4).locator('.src').last()).toHaveText('tape measure');

  // The steps, by n whatever the file's order, a gap and all.
  await expect(page.locator('.step .sn')).toHaveText(['1', '2', '4']);
  await expect(page.locator('.step .sdo')).toHaveText(['Lay out the wires', 'Crimp and pin the plug', 'Test every cavity']);
  const two = page.locator('.step').nth(1);
  await expect(two.locator('.how')).toHaveText('Pin-out:');
  await expect(two.locator('.clist li')).toHaveCount(3);
  await expect(two.locator('.clist li').nth(2)).toHaveText('9black 16 AWG ground');
  await expect(two.locator('.expect')).toContainText('You should see');
  await expect(two.locator('.expect')).toContainText('Each terminal clicks and does not pull out');
  await expect(two.locator('.caution')).toContainText('Crimp once');
  await expect(page.locator('.step').nth(0).locator('.caution')).toHaveCount(0);
  await expect(page.locator('.sbar .count')).toHaveText('0 of 3 steps');

  // The row's own note stays, folded away below the steps.
  const note = page.locator('details.rnote');
  await expect(note.locator('summary')).toHaveText("The row's note");
  await expect(note).not.toHaveAttribute('open');
  await expect(page.getByText('Keep the offcuts.')).toBeHidden();
  await note.locator('summary').click();
  await expect(page.getByText('Keep the offcuts.')).toBeVisible();

  await expect(section(page, 'done')).toContainText('Every cavity reads under 1 ohm end to end.');
  await expect(section(page, 'ifnot')).toContainText('Pull the pin with the removal tool');
  await expect(section(page, 'record')).toContainText('Tick the row done.');

  // His answer is the same control as ever, below it all, and the ticks say what they are.
  await expect(page.getByText('Step ticks stay on this device. The row is done when you answer it below.')).toBeVisible();
  await expect(page.getByRole('group', { name: 'Your answer for M1' }).getByRole('button', { name: 'Done' })).toBeVisible();

  // A source chip leads where it says.
  await know.nth(1).locator('a.src').click();
  await expect(page).toHaveURL(/#\/d\/D-405$/);
});

test('step ticks are kept on the device across a reload, and are never his answer', async ({ page }) => {
  await open(page, `#/p/${AREA}/todo/M1`);
  const count = page.locator('.sbar .count');
  await expect(count).toHaveText('0 of 3 steps');
  await page.getByRole('checkbox', { name: 'Step 1 done' }).check();
  await section(page, 'before').getByRole('checkbox').first().check();
  await expect(count).toHaveText('1 of 3 steps');

  await page.reload();
  await expect(page.getByRole('checkbox', { name: 'Step 1 done' })).toBeChecked();
  await expect(section(page, 'before').getByRole('checkbox').first()).toBeChecked();
  await expect(page.getByRole('checkbox', { name: 'Step 2 done' })).not.toBeChecked();
  await expect(count).toHaveText('1 of 3 steps');

  // The next unticked step is one press away.
  await page.getByRole('button', { name: 'Next unticked step' }).click();
  await expect(page.locator('[data-step="M1.02"]')).toBeInViewport();

  // The list shows the same count, and nothing has been answered.
  await page.goto(`/?claude=fake#/p/${AREA}/todo`);
  await expect(row(page, 'M1').locator('.meta')).toContainText('1 / 3 steps');
  await expect(page.getByText(/answer saved/)).toHaveCount(0);
  await expect(row(page, 'M1').getByRole('button', { name: 'Done' })).toBeVisible();

  // Every step ticked is still not an answer; Untick all clears the row's ticks.
  await page.goto(`/?claude=fake#/p/${AREA}/todo/M1`);
  await page.getByRole('checkbox', { name: 'Step 2 done' }).check();
  await page.getByRole('checkbox', { name: 'Step 4 done' }).check();
  await expect(count).toHaveText('3 of 3 steps');
  await expect(page.getByRole('button', { name: 'Next unticked step' })).toBeDisabled();
  await expect(page.getByRole('group', { name: 'Your answer for M1' }).getByRole('button', { name: 'Done' })).toBeVisible();
  await page.getByRole('button', { name: 'Untick all' }).click();
  await expect(count).toHaveText('0 of 3 steps');
  await expect(page.getByRole('checkbox', { name: 'Step 1 done' })).not.toBeChecked();

  // His answer goes the way it always has, and the page moves to the next row he can do.
  await page.getByRole('group', { name: 'Your answer for M1' }).getByRole('button', { name: 'Done' }).click();
  await expect(page).toHaveURL(new RegExp(`#/p/${AREA}/todo/M2$`));
  await expect(page.getByLabel('Measured value')).toBeVisible();
  await expect(page.locator('.strip')).toContainText('No. 2 of 4 in the list');
  await page.goto(`/?claude=fake#/p/${AREA}/todo`);
  await expect(page.getByText('1 answer saved, waiting to be applied.')).toBeVisible();
  // Start here has moved on to the first row he has not answered.
  await page.getByRole('button', { name: 'Start here' }).click();
  await expect(page).toHaveURL(new RegExp(`#/p/${AREA}/todo/M2$`));
});

test('a row without a brief, and a project without briefs, read as they always have', async ({ page }) => {
  await open(page, `#/p/${AREA}/todo/M3`);
  await expect(page.getByRole('heading', { name: 'Photograph the finished plug' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Waits on' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Note', exact: true })).toBeVisible();
  await expect(page.getByText('One photo from each side.')).toBeVisible();
  await expect(page.locator('.strip')).toHaveCount(0);
  await expect(page.locator('.guide')).toHaveCount(0);
  await expect(page.getByRole('group', { name: 'Your answer for M3' }).getByRole('button', { name: 'Done' })).toBeVisible();

  test.skip(!plain, 'every real project in the fixture has briefs');
  await page.goto(`/?claude=fake#/p/${plain!.name}/todo`);
  await expect(page.locator('.wrow').first()).toBeVisible();
  await expect(page.getByRole('button', { name: 'Start here' })).toHaveCount(0);
  await expect(page.getByLabel('Mine only')).toHaveCount(0);
  await expect(page.getByRole('tablist', { name: 'Whose' })).toBeVisible();
  await expect(page.locator('.wrow .no')).toHaveCount(0);
});

test('the row page fits a 390 px phone: nothing runs off the side, and what he taps is 44 px', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'phone only');
  await page.setViewportSize({ width: 390, height: 844 });
  await open(page, `#/p/${AREA}/todo/M1`);
  await expect(page.locator('.step')).toHaveCount(3);
  const over = await page.locator('.focus').evaluate((el) => {
    const w = document.documentElement.clientWidth;
    return [...el.querySelectorAll<HTMLElement>('*')].filter((x) => x.getBoundingClientRect().right > w + 1).map((x) => x.className || x.tagName);
  });
  expect(over).toEqual([]);
  // Step cards run the full width of the page's column.
  const widths = await page.evaluate(() => ({ step: document.querySelector('.step')!.getBoundingClientRect().width, col: document.querySelector('.focus')!.getBoundingClientRect().width }));
  expect(widths.step).toBeGreaterThanOrEqual(widths.col - 1);
  // The tick's label, the before-you-start lines, the parts and the controls take a thumb.
  for (const sel of ['.shead', '.checks label', '.prow', '.sbar .nextstep', '.rnote summary']) {
    const h = await page.locator(sel).first().evaluate((el) => el.getBoundingClientRect().height);
    expect(h, sel).toBeGreaterThanOrEqual(44);
  }
  // A source chip is small to the eye and still 44 px to the thumb.
  const chip = await page.locator('a.src').first().evaluate((el) => {
    const r = el.getBoundingClientRect();
    const a = getComputedStyle(el, '::after');
    return r.height - parseFloat(a.top) - parseFloat(a.bottom);
  });
  expect(chip).toBeGreaterThanOrEqual(44);

  await page.goto(`/?claude=fake#/p/${AREA}/todo`);
  await expect(page.locator('.wrow')).toHaveCount(4);
  const wide = await page.locator('.content').evaluate((el) => {
    const w = document.documentElement.clientWidth;
    return [...el.querySelectorAll<HTMLElement>('*')].filter((x) => x.getBoundingClientRect().right > w + 1).map((x) => x.className || x.tagName);
  });
  expect(wide).toEqual([]);
  for (const sel of ['.start .btn', '.toggle']) {
    const h = await page.locator(sel).first().evaluate((el) => el.getBoundingClientRect().height);
    expect(h, sel).toBeGreaterThanOrEqual(44);
  }
});
