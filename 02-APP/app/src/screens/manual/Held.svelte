<!--
  What the Manual holds back (D-417, his 4.5), with the reason rx7.py gave: folded away under
  the page, so a missing fact is never a silent gap.
-->
<script lang="ts">
  import type { Held } from '../../lib/model';

  let { rows, what }: { rows: Held[]; what: string } = $props();

  const REASON: Record<Held['reason'], string> = { confirm: 'Not yet checked on the car', unverified: 'Unverified', 'other-car': "Another car's figure" };
</script>

{#if rows.length}
  <details class="held panel">
    <summary>{rows.length} {what} held back until they are checked</summary>
    <ul>
      {#each rows as h (h.table + h.key)}
        <li>
          <span>{h.label}</span>
          <span class="chip quiet" title={h.why}>{REASON[h.reason] ?? h.reason}</span>
        </li>
      {/each}
    </ul>
  </details>
{/if}

<style>
  .held {
    margin-top: 28px;
    padding: 12px 16px;
  }
  summary {
    cursor: pointer;
    color: var(--text-2);
    font-weight: 560;
    font-size: 14px;
  }
  ul {
    list-style: none;
    margin: 10px 0 0;
    padding: 0;
  }
  li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    padding: 7px 0;
    border-top: 1px solid var(--line-soft);
    font-size: 13.5px;
    color: var(--text-2);
  }
</style>
