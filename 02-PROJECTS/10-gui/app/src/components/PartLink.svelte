<!--
  A part's name, anywhere in the Manual (D-417, his 4.1): a link to its page, and on a pointer
  a small card of what it is before he leaves the page he is on.
-->
<script lang="ts">
  import { href } from '../lib/router.svelte';
  import { day, part, spec, system, value } from '../lib/manual';

  let { id, label = '' }: { id: string; label?: string } = $props();

  const p = $derived(part(id));
  const sys = $derived(p ? system(p.system) : undefined);
  const top = $derived((p?.specs ?? []).slice(0, 3).map(spec).filter((s) => !!s));
</script>

{#if p}
  <span class="wrap">
    <a class="plink" href={href({ name: 'manual', page: 'part', id })}>{label || p.name}</a>
    <span class="peek card" role="tooltip">
      <strong>{p.name}</strong>
      <span class="sub">
        {[p.maker, p.part_no].filter(Boolean).join(' ') || (p.factory === 'yes' ? 'Factory part' : '')}{sys ? ` · ${sys.name}` : ''}
      </span>
      {#if p.fitted}<span class="sub">Fitted {day(p.fitted.date)}</span>{/if}
      {#each top as s (s.id)}
        <span class="row"><span>{s.item}</span><span class="v">{value(s)}</span></span>
      {/each}
      {#if p.note}<span class="note">{p.note}</span>{/if}
    </span>
  </span>
{:else}
  <span>{label || id}</span>
{/if}

<style>
  .wrap {
    position: relative;
    display: inline;
  }
  .plink {
    color: var(--sky);
    text-decoration: underline;
    text-decoration-color: color-mix(in oklab, var(--sky) 35%, transparent);
    text-underline-offset: 3px;
  }
  .plink:hover {
    text-decoration-color: var(--sky);
  }
  .peek {
    position: absolute;
    z-index: 30;
    left: 0;
    top: calc(100% + 6px);
    width: 300px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 13px;
    line-height: 1.45;
    color: var(--text);
    background: var(--surface-2);
    pointer-events: none;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-3px);
    transition:
      opacity var(--t-fast) var(--ease),
      transform var(--t-fast) var(--ease),
      visibility 0s linear var(--t-fast);
  }
  .wrap:hover .peek,
  .plink:focus-visible + .peek {
    opacity: 1;
    visibility: visible;
    transform: none;
    transition-delay: 250ms, 250ms, 0s;
  }
  strong {
    font-size: 14px;
  }
  .sub {
    color: var(--text-3);
  }
  .row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    border-top: 1px solid var(--line-soft);
    padding-top: 4px;
    color: var(--text-2);
  }
  .v {
    color: var(--text);
    text-align: right;
  }
  .note {
    color: var(--text-2);
    font-size: 12.5px;
  }
  @media (hover: none) {
    .peek {
      display: none;
    }
  }
</style>
