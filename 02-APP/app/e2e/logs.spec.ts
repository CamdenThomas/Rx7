// Connect and log (BL2, BL3) and the Bluetooth scan (BL5) on the web build, against the
// stand-in ICU (?ble=fake, src/lib/logs/fake.ts): one press pulls two drives and saves each as
// a drives answer; the scan shows the battery's pack voltage from its advertisement.

import { expect, test } from '@playwright/test';

test('Connect and log pulls the drives and saves one drives answer each', async ({ page }) => {
  await page.goto('/?ble=fake#/manual');
  await page.evaluate(() => localStorage.clear());
  await page.goto('/?ble=fake#/manual');
  await page.getByRole('button', { name: 'Connect and log' }).first().click();
  await expect(page).toHaveURL(/#\/manual\/connect$/);
  await expect(page.getByText('2 drives saved to the inbox')).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText('Drive 12')).toBeVisible();
  await expect(page.getByText('(approximate)')).toBeVisible(); // drive 12 had no clock
  await expect(page.getByRole('button', { name: 'Pull full log' }).first()).toBeVisible();
});

test('the Bluetooth scan shows the battery pack voltage from its advertisement', async ({ page }) => {
  await page.goto('/?ble=fake#/manual/scan');
  await page.getByRole('button', { name: /Scan for/ }).click();
  await expect(page.getByText('13.01 V')).toBeVisible();
  await expect(page.getByText("the car's ICU", { exact: true })).toBeVisible();
  await expect(page.getByText('d4 32 01 00 64')).toBeVisible();
});
