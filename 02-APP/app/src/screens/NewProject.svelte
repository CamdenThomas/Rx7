<!--
  New project (D-406 6.2): a name and one paragraph of goal. Claude opens the area, writes the
  opening blocks and a first work list (the new-project playbook), and he lands on the project.
-->
<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { runs } from '../lib/claude.svelte';
  import { drafts } from '../lib/drafts.svelte';
  import { router } from '../lib/router.svelte';
  import { toast } from '../lib/toast.svelte';

  const saved = drafts.get('00-CAR', '~new-project');
  let name = $state(saved.choice);
  let goal = $state(saved.text);
  let busy = $state(false);

  const slug = $derived(name.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
  const next = $derived.by(() => {
    const nums = app.projects.map((p) => Number(p.prefix)).filter((n) => !Number.isNaN(n));
    return String(Math.max(-1, ...nums) + 1).padStart(2, '0');
  });

  $effect(() => drafts.set('00-CAR', '~new-project', { choice: name, text: goal }));

  async function create() {
    if (!slug || !goal.trim()) return;
    busy = true;
    if (app.platform?.canClaude) {
      runs.start('new', undefined, `Its folder: 02-PROJECTS/${next}-${slug}. His goal, in his words:\n\n${goal.trim()}`, `New project · ${name.trim()}`);
      drafts.clear('00-CAR', '~new-project');
      toast('Claude is opening the project. Follow it on the run screen.', 'ok');
      router.go({ name: 'projects' });
    } else {
      const out = await app.save({ area: '00-CAR', target: slug, kind: 'project', choice: '', text: goal.trim(), context: '' });
      if (out) {
        drafts.clear('00-CAR', '~new-project');
        router.go({ name: 'projects' });
      }
    }
    busy = false;
  }
</script>

<div class="page narrow">
  <p class="label">New project</p>
  <h1>What do you want to do to the car?</h1>
  <p class="muted lead">
    Give it a name and say what it is for, in a paragraph. Claude opens the project, writes the first questions only you
    can answer, and a first work list.
  </p>

  <div class="form card">
    <label>
      <span class="label">Name</span>
      <input class="input big" bind:value={name} placeholder="Paint" maxlength="40" />
      {#if slug}<span class="faint small">Folder: <span class="mono">02-PROJECTS/{next}-{slug}</span></span>{/if}
    </label>
    <label>
      <span class="label">Goal</span>
      <textarea class="textarea" bind:value={goal} rows="6" placeholder="What it should achieve, what it must not touch, anything you already know you want."></textarea>
    </label>
    <div class="actions">
      {#if !app.platform?.canClaude}
        <p class="faint small">From the phone this is saved as a request, and the desktop opens the project the next time it runs.</p>
      {/if}
      <button class="btn primary big" onclick={create} disabled={!slug || !goal.trim() || busy}>
        {app.platform?.canClaude ? 'Open the project' : 'Save the request'}
      </button>
    </div>
  </div>
</div>

<style>
  h1 {
    font-size: clamp(26px, 3vw, 34px);
    margin: 8px 0 12px;
  }
  .lead {
    max-width: 620px;
    margin-bottom: 24px;
  }
  .form {
    padding: 22px;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .input.big {
    font-size: 18px;
    padding: 12px 14px;
  }
  .small {
    font-size: 12.5px;
  }
  .actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 16px;
  }
</style>
