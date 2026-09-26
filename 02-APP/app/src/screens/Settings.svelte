<!-- This device's settings: where the record is, and — on the phone — the key that sends answers. -->
<script lang="ts">
  import { KeyRound, FolderOpen, CircleCheck, CircleAlert, Zap, Cpu } from '@lucide/svelte';
  import { app } from '../lib/app.svelte';
  import { autoApply } from '../lib/autoapply.svelte';
  import { runs, RUN_CLASS_TITLE, type RunClass, type RunSettings } from '../lib/claude.svelte';
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

  const MODELS = [
    ['', 'Claude Code’s default (your account setting)'],
    ['sonnet', 'Sonnet (cheapest, fine for applying answers)'],
    ['opus', 'Opus'],
  ];
  const EFFORTS = ['low', 'medium', 'high', 'xhigh'];
  const classes: RunClass[] = ['quick', 'design'];

  async function setRun(cls: RunClass, patch: Partial<RunSettings>) {
    await runs.setSettings({ ...runs.settings, [cls]: { ...runs.settings[cls], ...patch } });
    toast('Saved for the next run.', 'ok');
  }
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

  {#if p?.canClaude}
    <section class="card box">
      <h2><Zap size={18} /> Auto-apply</h2>
      <p class="muted">
        Claude applies your answers on its own, a minute and a half after the last one you save here or on the phone. The
        app checks GitHub for the phone's answers every three minutes while it is open. Off, answers wait for Apply.
      </p>
      <label class="toggle">
        <input type="checkbox" checked={app.autoApply} onchange={(e) => autoApply.set(e.currentTarget.checked)} />
        Apply my answers automatically
      </label>
    </section>
  {/if}

  {#if p?.canClaude}
    <section class="card box">
      <h2><Cpu size={18} /> Claude runs</h2>
      <p class="muted">
        Ticks, values, choices and drives are applied by rule, with no model at all. What is left goes to Claude Code,
        with the model, effort and spending cap set here per kind of run. Every run counts against your subscription's
        session budget, so the cheaper row is for the runs that only follow a playbook.
      </p>
      {#each classes as cls (cls)}
        <div class="runrow">
          <strong>{RUN_CLASS_TITLE[cls]}</strong>
          <div class="inline">
            <select class="input" aria-label="Model for {RUN_CLASS_TITLE[cls]}" value={runs.settings[cls].model} onchange={(e) => setRun(cls, { model: e.currentTarget.value })}>
              {#each MODELS as [v, label] (v)}<option value={v}>{label}</option>{/each}
            </select>
            <select class="input" aria-label="Effort for {RUN_CLASS_TITLE[cls]}" value={runs.settings[cls].effort} onchange={(e) => setRun(cls, { effort: e.currentTarget.value })}>
              {#each EFFORTS as ef (ef)}<option value={ef}>effort {ef}</option>{/each}
            </select>
            <label class="cap">cap $<input class="input" type="number" min="0" step="1" value={runs.settings[cls].budget} aria-label="Spending cap for {RUN_CLASS_TITLE[cls]}" onchange={(e) => setRun(cls, { budget: Number(e.currentTarget.value) || 0 })} /></label>
          </div>
        </div>
      {/each}
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
  .toggle {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
  }
  .runrow {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .cap {
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
  }
  .cap .input {
    width: 5em;
  }
  @media (max-width: 759px) {
    .inline {
      flex-direction: column;
    }
  }
</style>
