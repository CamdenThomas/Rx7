<script lang="ts">
  let { done, total, label = true }: { done: number; total: number; label?: boolean } = $props();
  const pct = $derived(total ? Math.round((done / total) * 100) : 0);
</script>

<div class="progress" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={done} aria-label="Work done">
  <div class="track"><div class="bar" style:width="{pct}%"></div></div>
  {#if label}<span class="num">{done}<span class="faint"> / {total}</span></span>{/if}
</div>

<style>
  .progress {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12.5px;
  }
  .track {
    flex: 1;
    height: 6px;
    border-radius: 6px;
    background: var(--bg-raise);
    border: 1px solid var(--line-soft);
    overflow: hidden;
  }
  .bar {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, var(--steel), var(--sky));
    transition: width 400ms var(--ease);
  }
</style>
