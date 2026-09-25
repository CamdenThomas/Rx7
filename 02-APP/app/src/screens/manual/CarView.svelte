<!--
  The car (D-417, D-421): the zones drawn on the renders, each opening its parts. Where each
  zone and part sits on the model is 00-CAR's (zones.model_box_mm, parts.model_at_mm); the
  renders' cameras are public/car/views.json. The model is a picture, and nothing is measured
  from it (R11).
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import type { Manual } from '../../lib/model';
  import { boxes, hull, places, project, type View } from '../../lib/manual';
  import { href, router } from '../../lib/router.svelte';
  import PartLink from '../../components/PartLink.svelte';

  let { m, id }: { m: Manual; id?: string } = $props();

  const NAMES = { side: 'Side', threequarter: 'Three-quarter' } as const;
  type Name = keyof typeof NAMES;
  let which = $state<Name>('threequarter');
  let views = $state<Record<Name, View> | null>(null);
  let hover = $state('');

  onMount(async () => {
    try {
      views = (await (await fetch('/car/views.json')).json()).views;
    } catch {
      views = null;
    }
  });

  const view = $derived(views?.[which]);
  const zone = $derived(id ? m.zones.find((z) => z.id === id) : undefined);
  const shapes = $derived(
    view
      ? m.zones
          .map((z) => {
            const polys = boxes(z.model_box_mm).map((b) => hull(b.map((p) => project(view, p))));
            const area = polys.reduce((n, p) => n + Math.abs(p.reduce((a, q, i) => a + q[0] * p[(i + 1) % p.length][1] - p[(i + 1) % p.length][0] * q[1], 0)) / 2, 0);
            return { z, polys, area };
          })
          .filter((s) => s.polys.length)
          // the small zones drawn last, so each can still be pointed at
          .sort((a, b) => b.area - a.area)
      : [],
  );
  const dots = $derived(
    view && zone
      ? m.parts.filter((p) => p.zone === zone.id).flatMap((p) => places(p.model_at_mm).map((at) => ({ p, xy: project(view, at) })))
      : [],
  );
  const pts = (poly: [number, number][]) => poly.map((q) => q.join(',')).join(' ');
  const go = (zid: string) => router.go({ name: 'manual', page: 'car', id: zid === id ? undefined : zid });
</script>

<div class="wrap">
  <div class="stage panel">
    <div class="views" role="group" aria-label="View">
      {#each Object.keys(NAMES) as n (n)}
        <button class="chip" class:solid={which === n} onclick={() => (which = n as Name)}>{NAMES[n as Name]}</button>
      {/each}
    </div>
    <div class="pic">
      <img src="/car/{which}.webp" alt="The car, {NAMES[which].toLowerCase()} view" />
      {#if view}
        <svg viewBox="0 0 {view.width} {view.height}" preserveAspectRatio="xMidYMid meet" aria-label="Zones">
          {#each shapes as s (s.z.id)}
            <g
              class="zone"
              class:on={s.z.id === id}
              class:hot={s.z.id === hover}
              class:dim={!!id && s.z.id !== id}
              role="button"
              tabindex="-1"
              aria-label={s.z.name}
              onclick={() => go(s.z.id)}
              onkeydown={(e) => e.key === 'Enter' && go(s.z.id)}
              onpointerenter={() => (hover = s.z.id)}
              onpointerleave={() => (hover = '')}
            >
              {#each s.polys as poly, i (i)}<polygon points={pts(poly)} />{/each}
            </g>
          {/each}
          {#each dots as d, i (i)}
            <circle cx={d.xy[0]} cy={d.xy[1]} r="9" class="dot"><title>{d.p.name}</title></circle>
          {/each}
        </svg>
      {/if}
    </div>
    <p class="faint small">A picture of an FB, not this car: where things sit is approximate, and nothing is measured from it.</p>
  </div>

  <aside>
    <ul class="zones">
      {#each m.zones as z (z.id)}
        <li>
          <a
            href={href({ name: 'manual', page: 'car', id: z.id === id ? undefined : z.id })}
            class:on={z.id === id}
            onpointerenter={() => (hover = z.id)}
            onpointerleave={() => (hover = '')}
          >
            <span>{z.name}</span><span class="faint">{z.parts.length}</span>
          </a>
        </li>
      {/each}
    </ul>
  </aside>
</div>

{#if zone}
  <section class="parts">
    <h2>{zone.name}</h2>
    {#if zone.note}<p class="muted small">{zone.note}</p>{/if}
    {#if !zone.parts.length}
      <p class="muted">No part here is in the Manual yet.</p>
    {:else}
      <ul>
        {#each zone.parts as pid (pid)}
          <li><PartLink id={pid} /></li>
        {/each}
      </ul>
    {/if}
  </section>
{/if}

<style>
  .wrap {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 240px;
    gap: 16px;
    align-items: start;
  }
  .stage {
    padding: 12px;
  }
  .views {
    display: flex;
    gap: 6px;
    margin-bottom: 8px;
  }
  .views .chip {
    cursor: pointer;
  }
  .pic {
    position: relative;
  }
  .pic img {
    display: block;
    width: 100%;
    height: auto;
  }
  svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }
  .zone polygon {
    fill: color-mix(in oklab, var(--sky) 6%, transparent);
    stroke: color-mix(in oklab, var(--sky) 45%, transparent);
    stroke-width: 2;
    cursor: pointer;
    transition:
      fill var(--t-fast),
      opacity var(--t-fast);
  }
  .zone.hot polygon {
    fill: color-mix(in oklab, var(--sky) 22%, transparent);
    stroke: var(--sky);
  }
  .zone.on polygon {
    fill: color-mix(in oklab, var(--ember) 22%, transparent);
    stroke: var(--ember);
    stroke-width: 3;
  }
  .zone.dim polygon {
    opacity: 0.35;
  }
  .zone:focus {
    outline: none;
  }
  .dot {
    fill: var(--ember);
    stroke: var(--foam);
    stroke-width: 3;
  }
  .small {
    font-size: 12.5px;
    margin: 8px 2px 0;
  }
  .zones {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .zones a {
    display: flex;
    justify-content: space-between;
    padding: 8px 12px;
    border-radius: var(--r-1);
    color: var(--text-2);
    font-size: 14px;
  }
  .zones a:hover {
    background: var(--surface-2);
    color: var(--text);
  }
  .zones a.on {
    background: var(--accent-soft);
    color: var(--accent-2);
  }
  .parts {
    margin-top: 20px;
  }
  .parts h2 {
    font-size: 16px;
    margin: 0 0 8px;
  }
  .parts ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 8px 18px;
    font-size: 14px;
  }
  @media (max-width: 859px) {
    .wrap {
      grid-template-columns: 1fr;
    }
    .zones {
      flex-direction: row;
      flex-wrap: wrap;
      gap: 6px;
    }
    .zones a {
      gap: 8px;
      background: var(--surface-2);
      padding: 6px 10px;
    }
  }
</style>
