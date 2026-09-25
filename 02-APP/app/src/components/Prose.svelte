<!-- The record's prose, rendered: bold, lists, tables, and every D-### a link. -->
<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { md } from '../lib/text';

  let { text, compact = false }: { text: string; compact?: boolean } = $props();

  function click(e: MouseEvent) {
    const a = (e.target as HTMLElement).closest('a[data-external]') as HTMLAnchorElement | null;
    if (a) {
      e.preventDefault();
      app.platform?.open(a.href);
    }
  }
</script>

<!-- eslint-disable-next-line svelte/no-at-html-tags — md() escapes every character of the source first -->
<div class="prose" class:compact onclick={click} role="presentation">{@html md(text)}</div>

<style>
  .compact {
    font-size: 14px;
    line-height: 1.55;
  }
</style>
