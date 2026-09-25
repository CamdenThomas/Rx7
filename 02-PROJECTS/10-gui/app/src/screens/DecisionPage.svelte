<!-- Any decision by its id, from anywhere: a link in prose, a search result, a chip. -->
<script lang="ts">
  import DecisionView from '../components/DecisionView.svelte';
  import { app } from '../lib/app.svelte';

  let { id }: { id: string } = $props();
  const d = $derived(app.decision(id));
  const archived = $derived(/^D-\d+$/.test(id));
</script>

<div class="page narrow">
  {#if d}
    {#key d.id}<DecisionView {d} />{/key}
  {:else}
    <p class="muted">No decision {id} is in the record{archived ? ' — it may be in the archive' : ''}.</p>
  {/if}
</div>
