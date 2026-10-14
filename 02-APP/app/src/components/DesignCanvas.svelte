<!--
  One three.js view of a project's design (D-505), or of the car itself (02-cad D-518, the
  Manual's model page): the assembly, a part, or a board. The
  drawing is lib/designView.ts, loaded on demand like CarModel's three.js; this holds its
  canvas, passes it what the page selects, and says plainly when the device cannot draw.
  Built for one mode: the page keys it on the mode, so a new view is a new canvas and the
  old one's GPU memory is let go.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import type { Scene, Selection, Toggles } from '../lib/design';
  import type { DesignView, LoadState, Mode } from '../lib/designView';

  let {
    scene,
    base,
    mode,
    selection = null,
    hidden = new Set<string>(),
    side = 'top',
    toggles,
    apart = 0,
    dimmed,
    onpick,
    onstatus,
    onnodes,
  }: {
    scene: Scene;
    base: string;
    mode: Mode;
    selection?: Selection;
    hidden?: Set<string>;
    side?: 'top' | 'bottom';
    toggles?: Toggles;
    /** the car taken apart, 0 to 1 (the Manual's model page) */
    apart?: number;
    /** parts faded by a filter (the model page's Systems and Zone) */
    dimmed?: Set<string>;
    onpick?: (sel: Selection) => void;
    onstatus?: (id: string, s: LoadState) => void;
    onnodes?: (found: { case: boolean; inside: boolean }) => void;
  } = $props();

  let host: HTMLDivElement;
  let view = $state<DesignView | null>(null);
  let failed = $state('');

  onMount(() => {
    let v: DesignView | null = null;
    let gone = false;
    void (async () => {
      try {
        const { DesignView } = await import('../lib/designView');
        if (gone) return;
        v = new DesignView(host, scene, base, mode, {
          pick: (s) => onpick?.(s),
          status: (id, s) => onstatus?.(id, s),
          nodes: (f) => onnodes?.(f),
        });
        view = v;
      } catch (e) {
        failed = e instanceof Error ? e.message : String(e);
      }
    })();
    return () => {
      gone = true;
      v?.dispose();
      view = null;
    };
  });

  $effect(() => {
    const sel = selection;
    view?.setSelection(sel);
  });
  $effect(() => {
    const h = hidden;
    view?.setHidden(h);
  });
  $effect(() => {
    const s = side;
    if (mode.kind === 'board') view?.setSide(s);
  });
  $effect(() => {
    const t = toggles;
    if (t) view?.setToggles(t);
  });
  $effect(() => {
    const a = apart;
    view?.setApart(a);
  });
  $effect(() => {
    const d = dimmed;
    if (d) view?.setDimmed(d);
  });

  /** Frame the view again; `all` takes in every far end of the harness too. */
  export function fit(all = false) {
    view?.fit(all);
  }
</script>

<div class="stage" data-testid="design-stage">
  <div class="canvas" bind:this={host}></div>
  {#if failed}
    <p class="note muted">This device cannot draw 3D here ({failed}). The lists below still hold everything in the design.</p>
  {:else if !view}
    <p class="note faint">Starting the 3D view…</p>
  {/if}
</div>

<style>
  .stage {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 260px;
    border-radius: var(--r-3);
    overflow: hidden;
    background: radial-gradient(ellipse at 50% 60%, color-mix(in oklab, var(--steel) 40%, transparent), transparent 72%), var(--bg-raise);
    border: 1px solid var(--line-soft);
  }
  .canvas,
  .canvas :global(canvas) {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    touch-action: none;
  }
  .note {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    padding: 24px;
    text-align: center;
    font-size: 13.5px;
  }
  /* The labels are DOM elements three.js places (CSS2DRenderer), so they are styled here. */
  .canvas :global(.d3-labels) {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
  }
  .canvas :global(.d3-label) {
    font: 600 11.5px/1.2 var(--mono);
    color: var(--foam);
    white-space: nowrap;
    pointer-events: none;
  }
  .canvas :global(.d3-link) {
    pointer-events: auto;
    min-height: 28px;
    padding: 4px 8px;
    border-radius: 999px;
    border: 1px solid color-mix(in oklab, var(--sky) 45%, var(--ink));
    background: color-mix(in oklab, var(--ink) 82%, transparent);
    color: var(--sky);
    cursor: pointer;
  }
  .canvas :global(.d3-link.on) {
    background: var(--ember);
    border-color: var(--ember);
    color: #1f1714;
  }
  .canvas :global(.d3-conn),
  .canvas :global(.d3-node) {
    padding: 2px 6px;
    border-radius: var(--r-1);
    background: color-mix(in oklab, var(--ink) 80%, transparent);
  }
  .canvas :global(.d3-conn) {
    color: var(--ember);
  }
  .canvas :global(.d3-dot) {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--ember);
    box-shadow: 0 0 0 2px var(--ink);
  }
  .canvas :global(.d3-dot.approx) {
    background: transparent;
    border: 2px dashed var(--ember);
  }
  /* a far end (a node): smaller, sky, and a tap target larger than it looks */
  .canvas :global(.d3-nodedot) {
    pointer-events: auto;
    width: 7px;
    height: 7px;
    padding: 0;
    border: 10px solid transparent;
    box-sizing: content-box;
    background: var(--sky) content-box;
    box-shadow: none;
    cursor: pointer;
  }
  .canvas :global(.d3-node) {
    color: var(--sky);
    font-weight: 560;
  }
  /* names and the isolated links' labels above the dots (CSS2DRenderer sets z-index inline) */
  .canvas :global(.d3-part),
  .canvas :global(.d3-leg),
  .canvas :global(.d3-link) {
    z-index: 2000000 !important;
  }
  /* a leg's name at its root, in the leg's colour */
  .canvas :global(.d3-leg) {
    pointer-events: auto;
    min-height: 28px;
    padding: 4px 9px;
    border-radius: 999px;
    border: 2px solid var(--leg, var(--sky));
    background: color-mix(in oklab, var(--ink) 80%, transparent);
    font-family: var(--font);
    font-size: 12.5px;
    cursor: pointer;
  }
  /* a housing's code on its connector */
  .canvas :global(.d3-housing) {
    pointer-events: auto;
    padding: 2px 6px;
    border-radius: var(--r-1);
    border: 1px solid color-mix(in oklab, var(--foam) 25%, var(--ink));
    background: color-mix(in oklab, var(--ink) 82%, transparent);
    color: var(--foam);
    cursor: pointer;
  }
  .canvas :global(.d3-part) {
    padding: 3px 8px;
    border-radius: var(--r-1);
    background: color-mix(in oklab, var(--ink) 78%, transparent);
    font-family: var(--font);
    font-size: 12.5px;
    color: var(--foam);
  }
</style>
