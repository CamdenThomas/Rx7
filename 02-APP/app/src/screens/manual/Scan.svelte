<!--
  Bluetooth scan (02-APP BL5's proof page; D-495, electrical D-330). Lists every advertisement
  the device hears - name, address, signal and manufacturer data - and, where the data begins
  with a plausible pack voltage, the Ionic battery's millivolts as the ICU's radio reads them.
  It only listens: nothing here connects to the battery or writes to anything.
-->
<script lang="ts">
  import { BatteryCharging, Radar, Square } from '@lucide/svelte';
  import { logLink } from '../../lib/logs/link.svelte';
  import { looksIonic, mfrHex, packMv } from '../../lib/logs/ionic';
  import { isIcu } from '../../lib/logs/pull';

  const rows = $derived(
    logLink.adverts.map((a) => ({ a, pack: packMv(a.manufacturerData), hex: mfrHex(a.manufacturerData), ionic: looksIonic(a.name), icu: isIcu(a) })),
  );
  const pack = $derived(rows.find((r) => r.pack && r.ionic) ?? rows.find((r) => r.pack));
</script>

<section class="intro">
  <p class="muted">
    Rx7 uses Bluetooth for two things: reading the battery's broadcast, and pulling the drive logs from the car's ICU. The
    first scan asks for permission to find nearby devices; on Android it asks for no location. A scan only listens.
  </p>
  <div class="go">
    {#if logLink.scanning}
      <button class="btn" onclick={() => logLink.stop()}><Square size={14} /> Stop</button>
      <span class="faint small">Listening…</span>
    {:else}
      <button class="btn primary" onclick={() => logLink.scan()} disabled={logLink.running}><Radar size={15} /> Scan for 15 s</button>
    {/if}
  </div>
</section>

{#if pack?.pack}
  <section class="panel battery">
    <BatteryCharging size={20} />
    <div>
      <strong class="num">{(pack.pack.mv / 1000).toFixed(2)} V</strong>
      <span class="faint small">{pack.pack.mv} mV at the pack, from {pack.a.name || pack.a.address}'s advertisement (D-330)</span>
    </div>
  </section>
{/if}

<section>
  {#if !rows.length}
    <p class="muted">{logLink.scanning ? 'Nothing heard yet.' : 'Press Scan to list what is advertising nearby.'}</p>
  {:else}
    <div class="panel rows">
      {#each rows as r (r.a.address)}
        <div class="row" class:hit={r.ionic || r.icu}>
          <div class="what">
            <span class="item">{r.a.name || '(no name)'}{#if r.icu}<span class="chip cool">the car's ICU</span>{/if}{#if r.ionic}<span class="chip accent">battery</span>{/if}</span>
            <span class="faint small num">{r.a.address}</span>
            {#each r.hex as h, i (i)}<span class="small num mfr">{h}</span>{/each}
            {#if r.pack}<span class="small">pack {r.pack.mv} mV</span>{/if}
          </div>
          <span class="num rssi">{r.a.rssi} dBm</span>
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
  section {
    margin-bottom: 22px;
  }
  .intro p {
    max-width: 68ch;
    margin: 0 0 12px;
  }
  .go {
    display: flex;
    gap: 10px;
    align-items: center;
  }
  .battery {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
  }
  .battery strong {
    font-size: 24px;
    display: block;
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
    padding: 10px 0;
    border-top: 1px solid var(--line-soft);
  }
  .row:first-child {
    border-top: 0;
  }
  .row.hit .item {
    color: var(--foam);
  }
  .what {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }
  .item {
    font-weight: 560;
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
  }
  .mfr {
    color: var(--text-2);
    overflow-wrap: anywhere;
  }
  .rssi {
    color: var(--text-3);
    font-size: 13px;
  }
</style>
