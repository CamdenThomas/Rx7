<script lang="ts">
  import { toasts } from '../lib/toast.svelte';
</script>

<div class="toasts" aria-live="polite">
  {#each toasts.list as t (t.id)}
    <button class="toast {t.tone}" onclick={() => toasts.dismiss(t.id)}>{t.text}</button>
  {/each}
</div>

<style>
  .toasts {
    position: fixed;
    z-index: 60;
    left: 50%;
    bottom: calc(var(--tabbar) + 18px);
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: min(460px, calc(100vw - 32px));
    pointer-events: none;
  }
  .toast {
    pointer-events: auto;
    text-align: left;
    padding: 12px 16px;
    border-radius: var(--r-2);
    background: color-mix(in oklab, var(--surface-3) 92%, transparent);
    backdrop-filter: blur(12px);
    border: 1px solid var(--line);
    border-left: 3px solid var(--sky);
    color: var(--text);
    font-size: 14px;
    box-shadow: var(--shadow-3);
    animation: rise var(--t) var(--ease);
  }
  .toast.ok {
    border-left-color: var(--sky);
  }
  .toast.warn {
    border-left-color: var(--ember);
  }
  .toast.info {
    border-left-color: var(--steel);
  }
</style>
