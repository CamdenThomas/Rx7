// The Manual's model page (05-cad D-518, 02-APP MG1) on the web build: no car scene says so
// plainly and the part pages offer no link; the car stub (tests/fixtures/design/car, served
// as the car's design folder) shows its systems and zones, filters, comes apart on the
// slider, isolates a part, opens one alone with how it is held, and the part page links in.

import { existsSync, readFileSync } from 'node:fs';
import { expect, test, type Page } from '@playwright/test';

const fixture = JSON.parse(readFileSync(new URL('../fixture/export.json', import.meta.url), 'utf8'));
// a real Manual part, standing in for the stub's crossmember so the part page can link to it
const manualPart: { id: string; name: string } = fixture.manual.parts[0];

async function carStub(page: Page, present = true) {
  await page.route('**/design/00-CAR/**', (route) => {
    const rest = new URL(route.request().url()).pathname.split('/design/00-CAR/')[1] ?? '';
    const file = new URL(`../tests/fixtures/design/car/${rest}`, import.meta.url);
    if (!present || !/^[\w.-]+$/.test(rest) || !existsSync(file)) return route.fulfill({ status: 404, body: 'not found' });
    if (rest === 'scene.json') {
      return route.fulfill({ body: readFileSync(file, 'utf8').replaceAll('PT-STUB', manualPart.id), contentType: 'application/json' });
    }
    return route.fulfill({ body: readFileSync(file), contentType: 'model/gltf-binary' });
  });
}

test('no car model: said plainly, and a part page offers no link to it', async ({ page }) => {
  await carStub(page, false);
  await page.goto('/?claude=fake#/manual/model');
  await expect(page.getByText('No model of the car exported yet.')).toBeVisible();
  await expect(page.getByRole('navigation', { name: 'Manual pages' }).getByRole('link', { name: 'Model' })).toHaveAttribute('aria-current', 'page');
  await page.goto(`/?claude=fake#/manual/part/${manualPart.id}`);
  await expect(page.getByRole('heading', { name: manualPart.name, exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Show in the model' })).toHaveCount(0);
});

test('the car stub: systems, the slider, isolate, a part alone, and the link from its page', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await carStub(page);

  // From the Manual's part page into the model, the part isolated.
  await page.goto(`/?claude=fake#/manual/part/${manualPart.id}`);
  await page.getByRole('link', { name: 'Show in the model' }).click();
  await expect(page).toHaveURL(new RegExp(`#/manual/model/${manualPart.id}$`));
  const picked = page.getByRole('region', { name: 'Isolated part' });
  await expect(picked).toContainText('Rear crossmember');
  await expect(picked).toContainText('bolted to Floor pan');
  await expect(picked).toContainText('M10 x 4');
  await page.getByRole('button', { name: 'Show everything' }).click();
  await expect(picked).toHaveCount(0);

  // Grouped by system, then zone.
  const body = page.locator('details', { has: page.locator('summary', { hasText: /^Body/ }) });
  const susp = page.locator('details', { has: page.locator('summary', { hasText: /^Suspension/ }) });
  await expect(body).toContainText('Floor pan');
  await expect(susp).toContainText('Rear crossmember');
  await expect(susp).toContainText('Trailing arm bracket');
  await expect(susp).not.toContainText('Rear jack point'); // a place, not a part

  // The Systems filter and the Taken-apart slider.
  const systems = page.getByRole('group', { name: 'Systems' });
  await systems.getByRole('button', { name: 'Body' }).click();
  await expect(systems.getByRole('button', { name: 'Body' })).toHaveAttribute('aria-pressed', 'true');
  await expect(systems.getByRole('button', { name: 'All' })).toHaveAttribute('aria-pressed', 'false');
  await systems.getByRole('button', { name: 'All' }).click();
  await expect(systems.getByRole('button', { name: 'All' })).toHaveAttribute('aria-pressed', 'true');
  await page.getByRole('slider', { name: 'Taken apart' }).fill('1');
  await expect(page.getByText('100%')).toBeVisible();

  // Isolate from the list, then the part alone.
  await susp.getByRole('button', { name: /^Trailing arm bracket/ }).click();
  await expect(picked).toContainText('Trailing arm bracket');
  await page.getByRole('link', { name: 'This part alone' }).click();
  await expect(page).toHaveURL(/#\/manual\/model-part\/bracket$/);
  await expect(page.getByRole('heading', { name: 'Trailing arm bracket' })).toBeVisible();
  await expect(page.getByText('bolted to Rear crossmember')).toBeVisible();
  await expect(page.getByText('Could not load')).toHaveCount(0);
  expect(errors).toEqual([]);
});
