<!-- Search as its own page: the phone's Search tab, and any #/search?q= link. -->
<script lang="ts">
  import { untrack } from 'svelte';
  import SearchBox from '../components/SearchBox.svelte';

  let { q }: { q: string } = $props();
  let query = $state(untrack(() => q));
</script>

<div class="page narrow sp">
  <div class="card box"><SearchBox bind:query /></div>
</div>

<style>
  .sp {
    padding-top: 12px;
  }
  .box {
    height: calc(100dvh - var(--topbar) - var(--tabbar) - 60px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
</style>
