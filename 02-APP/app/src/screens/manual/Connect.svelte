<!--
  Connect and log (02-APP BL2, BL3; electrical D-478, D-483, D-493, D-494). One press pulls
  every drive the ICU holds that this device has not: the summary, then the thinned log, from
  the last byte held. Each drive then becomes one kind=drive answer in 00-CAR's inbox - the
  same path as Log drive - and is filed like any other. The full log stays on the car's card
  unless he asks for it here, drive by drive. The raw files stay on this device.
-->
<script lang="ts">
  import { BluetoothSearching, Download, Radar, Square } from '@lucide/svelte';
  import Progress from '../../components/Progress.svelte';
  import { app } from '../../lib/app.svelte';
  import { logLink } from '../../lib/logs/link.svelte';
  import { TIER_NAME, type Tier } from '../../lib/logs/format';
  import { day, miles } from '../../lib/manual';
  import { href } from '../../lib/router.svelte';

  $effect(() => {
    void logLink.load();
  });

  const p = $derived(logLink.progress);
  const kb = (n: number) => (n >= 1e6 ? `${(n / 1e6).toFixed(1)} MB` : `${Math.max(0, n / 1000).toFixed(n < 10_000 ? 1 : 0)} kB`);
  // the pull's rate budget (electrical params ble_kbps, confirm at BT4), for the full log's estimate
  const kbps = $derived.by(() => {
    const t = app.snapshot?.tables.find((x) => x.area === '01-electrical' && x.table === 'params');
    const row = t?.rows.find((r) => r[0] === 'ble_kbps');
    const v = Number(row?.[t!.columns.indexOf('value')]);
    return Number.isFinite(v) && v > 0 ? v : null;
  });
  const PHASE: Record<string, string> = {
    scanning: 'Looking for the car', connecting: 'Connecting', info: 'Reading the ICU', clock: 'Setting the clock', listing: 'Listing drives',
    pulling: 'Pulling', checking: 'Checking', done: 'Done', error: 'Stopped',
  };
  const tiers: Tier[] = [0, 1, 2];
  const len = (d: (typeof logLink.drives)[number], t: Tier) => (t === 0 ? d.item.summary_len : t === 1 ? d.item.thin_len : d.item.full_len);
</script>

<section class="intro">
  <p class="muted">
    With the key at ACC or RUN, Connect and log pulls every drive the ICU's card holds that this device has not: its summary,
    then its once-a-second log. A pull that is cut short carries on from where it stopped next time. Each drive becomes a
    drives entry, waiting to be filed. The first time, pair the phone: a long press of the page button shows a six-digit key on
    the cluster, and the phone asks for it.
  </p>
  <div class="go">
    {#if logLink.running}
      <button class="btn" onclick={() => logLink.stop()}><Square size={14} /> Stop</button>
    {:else}
      <button class="btn primary big" onclick={() => logLink.pull()} disabled={logLink.available === false}>
        <BluetoothSearching size={16} /> Connect and log
      </button>
    {/if}
    <a class="btn ghost small" href={href({ name: 'manual', page: 'scan' })}><Radar size={14} /> Bluetooth scan</a>
  </div>
  {#if logLink.available === false}
    <p class="warn">Bluetooth is not available here. It works in the installed apps - the phone, the Mac and the Fedora PC.</p>
  {/if}
</section>

{#if p && (logLink.running || p.phase === 'error' || p.phase === 'done')}
  <section class="panel prog" aria-live="polite">
    <header>
      <strong>{PHASE[p.phase] ?? p.phase}</strong>
      {#if p.drives}<span class="faint small">drive {Math.min(p.drivesDone + (logLink.running ? 1 : 0), p.drives)} of {p.drives}</span>{/if}
    </header>
    <p class:warn={p.phase === 'error'}>{p.message}</p>
    {#if p.expected}
      <Progress done={Math.min(p.bytes, p.expected)} total={p.expected} label={false} />
      <p class="faint small num">{kb(p.bytes)} of {kb(p.expected)}{p.rate ? ` · ${kb(p.rate)}/s` : ''}</p>
    {/if}
  </section>
{/if}

{#if logLink.last && !logLink.running}
  {@const o = logLink.last}
  <section class="panel outcome">
    {#if o.error}<p class="warn">{o.error}</p>{/if}
    {#if o.filed}
      <p>
        {o.filed.written.length} drive{o.filed.written.length === 1 ? '' : 's'} saved to the inbox{o.filed.written.length ? ' - Apply files them' : ''}.
        {#if o.acked.length}<span class="faint">{o.acked.length} file{o.acked.length === 1 ? '' : 's'} acknowledged to the ICU.</span>{/if}
      </p>
      {#each o.filed.skipped as s, i (i)}<p class="faint small">Not a drive: {s}</p>{/each}
    {/if}
    {#each [...o.problems, ...(o.filed?.problems ?? [])] as s, i (i)}<p class="warn small">{s}</p>{/each}
  </section>
{/if}

<section>
  <h2>Drives on this device</h2>
  {#if !logLink.drives.length}
    <p class="muted">None pulled yet.</p>
  {:else}
    <div class="panel rows">
      {#each logLink.drives as d (d.seq)}
        <div class="row">
          <div class="what">
            <span class="item">
              Drive {d.seq}
              {#if d.brief}<span class="faint"> · {day(d.brief.start.slice(0, 10))} {d.brief.start.slice(11, 16)}{d.brief.approx ? ' (approximate)' : ''}</span>{/if}
            </span>
            {#if d.brief}
              <span class="sub">{d.brief.miles.toFixed(1)} mi · {d.brief.minutes} min{d.brief.endOdo ? ` · ended at ${miles(d.brief.endOdo)}` : ''}</span>
              {#each d.brief.flags as f, i (i)}<span class="flag">{f}</span>{/each}
            {/if}
            <span class="faint small">
              {#each tiers as t (t)}
                {#if len(d, t)}<span class="tier">{TIER_NAME[t]} {d.held[t] >= len(d, t) ? '✓' : d.held[t] ? `${kb(d.held[t])} of ${kb(len(d, t))}` : 'on the car'}</span>{/if}
              {/each}
            </span>
            {#if d.filed?.target}<span class="faint small">filed as {d.filed.target}</span>
            {:else if d.filed?.skipped}<span class="faint small">no drives entry: {d.filed.skipped}</span>{/if}
          </div>
          <div class="due">
            {#if d.item.full_len && d.held[2] < d.item.full_len}
              <button class="btn small ghost" disabled={logLink.running} onclick={() => logLink.pull([d.seq], false)} title="The full log stays on the card unless asked for (D-493)">
                <Download size={13} /> Pull full log
              </button>
              <span class="faint small">{kb(d.item.full_len - d.held[2])}{kbps ? ` · about ${Math.max(1, Math.round((d.item.full_len - d.held[2]) / (kbps * 1000) / 60))} min` : ''}</span>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
  {#if logLink.where}<p class="faint small where">Kept on this device in <span class="num">{logLink.where}</span>, out of the record.</p>{/if}
</section>

<style>
  section {
    margin-bottom: 22px;
  }
  h2 {
    font-size: 15px;
    margin: 0 0 8px;
  }
  .intro p {
    max-width: 68ch;
    margin: 0 0 12px;
  }
  .go {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }
  .prog,
  .outcome {
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .prog header {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }
  .prog p,
  .outcome p {
    margin: 0;
  }
  .warn {
    color: var(--accent-2);
  }
  .small {
    font-size: 12.5px;
  }
  .rows {
    padding: 0 16px;
  }
  .row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 6px 16px;
    align-items: start;
    padding: 11px 0;
    border-top: 1px solid var(--line-soft);
  }
  .row:first-child {
    border-top: 0;
  }
  .what {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 0;
  }
  .item {
    font-weight: 560;
    font-size: 14px;
  }
  .sub {
    color: var(--text-2);
    font-size: 13px;
  }
  .flag {
    color: var(--accent-2);
    font-size: 12.5px;
  }
  .tier + .tier::before {
    content: ' · ';
  }
  .due {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
  }
  .where {
    margin-top: 10px;
    overflow-wrap: anywhere;
  }
  @media (max-width: 759px) {
    .row {
      grid-template-columns: 1fr;
    }
    .due {
      align-items: flex-start;
    }
  }
</style>
