// Photographs every screen at desktop and phone size, for design review. Needs the dev
// server running (npm run dev). Usage: node scripts/shots.mjs <out-dir> [filter]
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';

const out = process.argv[2] ?? 'shots';
const only = process.argv[3] ?? '';
const base = process.env.RX7_URL ?? 'http://localhost:5173/?claude=fake';
mkdirSync(out, { recursive: true });

const pages = [
  ['home', '#/'],
  ['manual', '#/manual'],
  ['projects', '#/projects'],
  ['project-electrical', '#/p/01-electrical'],
  ['blocks', '#/p/01-electrical/blocks'],
  ['block-0129', '#/p/01-electrical/blocks/01.29'],
  ['picks', '#/p/03-luxury/picks'],
  ['pick', '#/p/03-luxury/picks/PK021'],
  ['todo-design', '#/p/01-electrical/todo'],
  ['todo-lux', '#/p/03-luxury/todo'],
  ['todo-row', '#/p/01-electrical/todo/S1'],
  ['decisions', '#/p/01-electrical/decisions'],
  ['decision', '#/p/02-APP/decisions/D-405'],
  ['parts', '#/p/03-luxury/parts'],
  ['run', '#/p/01-electrical/run'],
  ['row', '#/row/00-CAR/vehicle/mileage'],
  ['new', '#/projects/new'],
  ['settings', '#/settings'],
  ['search', '#/search?q=fuse'],
];
const sizes = [
  ['desk', { width: 1440, height: 900 }, 1],
  ['phone', { width: 412, height: 915 }, 2],
];

const browser = await chromium.launch();
for (const [label, viewport, scale] of sizes) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: scale, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => console.error(`[${label}] page error:`, e.message));
  page.on('console', (m) => m.type() === 'error' && console.error(`[${label}] console:`, m.text()));
  for (const [name, hash] of pages) {
    if (only && !name.includes(only)) continue;
    await page.goto(base + hash);
    await page.waitForTimeout(700);
    await page.screenshot({ path: `${out}/${label}-${name}.png`, fullPage: false });
  }
  await ctx.close();
}
await browser.close();
console.log('shots in', out);
