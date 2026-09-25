<!-- This device's settings: where the record is, and — on the phone — the key that sends answers. -->
<script lang="ts">
  import { KeyRound, FolderOpen, CircleCheck, CircleAlert } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { ago, plural } from '../lib/text';
  import { toast } from '../lib/toast.svelte';

  const p = $derived(app.platform);
  let root = $state('');
  let token = $state('');
  let showProblems = $state(false);

  $effect(() => {
    void p?.treeRoot?.().then((r) => (root = r));
    token = p?.token?.() ?? '';
  });

  async function saveRoot() {
    try {
      root = (await p!.setTreeRoot!(root.trim())) ?? root;
      await app.refresh(true);
      toast('Now reading that tree.', 'ok');
    } catch (e) {
      toast(String(e), 'warn');
    }
  }

  async function saveToken() {
    await p!.setToken!(token);
    toast(token ? 'Key saved. The phone can send answers now.' : 'Key removed.', 'ok');
  }

  const record = $derived(app.snapshot?.record);
</script>

<div class="page narrow">
  <p class="label">Settings</p>
  <h1>This {p?.kind === 'phone' ? 'phone' : p?.kind === 'desktop' ? 'computer' : 'browser'}</h1>

  <section class="card box">
    <h2>The record</h2>
    <p class="state">
      {#if record?.valid}<CircleCheck size={18} class="ok" /> Valid — it does not contradict itself.
      {:else}<CircleAlert size={18} class="bad" /> {plural(record?.problems.length ?? 0, 'problem')} — Claude fixes these on its next run.
        <button class="btn small ghost" onclick={() => (showProblems = !showProblems)}>{showProblems ? 'Hide' : 'Show'}</button>{/if}
    </p>
    {#if showProblems}<ul class="problems mono">{#each record?.problems ?? [] as x, i (i)}<li>{x}</li>{/each}</ul>{/if}
    <p class="faint small">Read {app.snapshot ? ago(app.snapshot.generated) : '—'} · {app.sync.asOf ? `as of ${ago(app.sync.asOf)}` : ''}</p>
  </section>

  {#if p?.setTreeRoot}
    <section class="card box">
      <h2><FolderOpen size={18} /> The tree</h2>
      <p class="muted">The folder the desktop app reads and answers into. It commits each answer and pushes it to GitHub, where the phone picks it up.</p>
      <div class="inline">
        <input class="input mono" bind:value={root} aria-label="Tree folder" />
        <button class="btn" onclick={saveRoot}>Use this folder</button>
      </div>
    </section>
  {/if}

  {#if p?.setToken}
    <section class="card box">
      <h2><KeyRound size={18} /> GitHub key</h2>
      <p class="muted">
        The phone reads the record from GitHub with no key. To send your answers it needs one: on github.com, Settings →
        Developer settings → Fine-grained tokens → Generate. Repository access: only <span class="mono">CamdenThomas/Rx7</span>.
        Permissions: Contents — read and write. Paste it here; it stays on this phone.
      </p>
      <div class="inline">
        <input class="input mono" type="password" bind:value={token} placeholder="github_pat_…" aria-label="GitHub key" autocomplete="off" />
        <button class="btn primary" onclick={saveToken}>Save</button>
      </div>
      {#if app.sync.waiting}<p class="faint small">{plural(app.sync.waiting, 'answer')} on this phone waiting to be sent.</p>{/if}
    </section>
  {/if}

  <section class="card box">
    <h2>About</h2>
    <p class="muted">Rx7 {p?.kind === 'phone' ? 'for Android' : p?.kind === 'desktop' ? 'for Fedora' : 'in a browser'} · a view of the record and the one place you answer it. It keeps no fact of its own.</p>
    {#if p?.canClaude}<p class="muted">Claude runs here through Claude Code, on your subscription.</p>{:else}<p class="muted">Claude runs on the desktop; from here you can read everything and save answers.</p>{/if}
  </section>
</div>

<style>
  h1 {
    font-size: 28px;
    margin: 6px 0 22px;
  }
  .box {
    padding: 18px 20px;
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  h2 {
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .inline {
    display: flex;
    gap: 10px;
  }
  .state {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .state :global(.ok) {
    color: var(--sky);
  }
  .state :global(.bad) {
    color: var(--ember);
  }
  .problems {
    font-size: 12px;
    color: var(--text-2);
    padding-left: 18px;
    max-height: 240px;
    overflow: auto;
  }
  .small {
    font-size: 12.5px;
  }
  @media (max-width: 759px) {
    .inline {
      flex-direction: column;
    }
  }
</style>
