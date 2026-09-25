<!--
  Home (D-406 3.1, 3.2): two working buttons, Manual and Projects, as large tiles. Everything
  else is here to look good — the car, and who it is.
-->
<script lang="ts">
  import { ArrowRight } from '@lucide/svelte';
  import CarArt from '../components/CarArt.svelte';
  import Mark from '../components/Mark.svelte';
  import ProjectIcon from '../components/ProjectIcon.svelte';
  import { app } from '../lib/app.svelte';
  import { href } from '../lib/router.svelte';
  import { plural } from '../lib/text';

  const vehicle = $derived.by(() => {
    const t = app.car;
    if (!t) return {} as Record<string, string>;
    const k = t.columns.indexOf('key');
    const v = t.columns.indexOf('value');
    return Object.fromEntries(t.rows.map((r) => [r[k], r[v]]));
  });

  const identity = $derived(
    [vehicle.generation && `${vehicle.generation} chassis`, vehicle.trim, vehicle.colour, vehicle.engine,
      vehicle.mileage && /^\d+$/.test(vehicle.mileage) ? `${Number(vehicle.mileage).toLocaleString()} mi` : ''].filter(Boolean),
  );

  const waiting = $derived(app.summaries.reduce((n, s) => n + s.waiting.blocks + s.waiting.picks, 0));
  const blocks = $derived(app.summaries.reduce((n, s) => n + s.waiting.blocks, 0));
  const picks = $derived(app.summaries.reduce((n, s) => n + s.waiting.picks, 0));
  const photos = $derived(app.snapshot?.photos ?? []);
  const hero = $derived(photos.length ? app.platform?.photo(photos[0]) : '');
</script>

<div class="home">
  <section class="hero">
    <div class="glow"></div>
    <div class="intro rise">
      <p class="label">{vehicle.year_model ?? 'Mazda RX-7'}</p>
      <h1>The whole car, in one place.</h1>
      {#if identity.length}
        <p class="ident">{#each identity as x, i (i)}{#if i}<span class="dot">·</span>{/if}<span>{x}</span>{/each}</p>
      {/if}
    </div>
    <div class="art">
      {#if hero}
        <img src={hero} alt="The car" />
      {:else}
        <CarArt />
      {/if}
    </div>
  </section>

  <section class="tiles">
    <a class="tile manual" href={href({ name: 'manual' })}>
      <div class="pic">
        <div class="crop"><CarArt animate={false} /></div>
      </div>
      <div class="body">
        <h2>Manual</h2>
        <p>The car exactly as it is today — its parts, its specs, its service.</p>
        <span class="go">Open the manual <ArrowRight size={16} /></span>
      </div>
    </a>

    <a class="tile projects" href={href({ name: 'projects' })}>
      <div class="pic">
        <div class="rotor"><Mark size={180} /></div>
        <div class="orbit">
          {#each app.summaries as s, i (s.name)}
            <span class="planet" style:--i={i} style:--n={app.summaries.length}><ProjectIcon name={s.icon} size={18} /></span>
          {/each}
        </div>
      </div>
      <div class="body">
        <h2>Projects</h2>
        <p>{plural(app.summaries.length, 'project')} in flight, and every question only you can answer.</p>
        {#if waiting}
          <span class="status"><span class="pip"></span>{blocks ? plural(blocks, 'block') : ''}{blocks && picks ? ' · ' : ''}{picks ? plural(picks, 'pick') : ''} waiting for you</span>
        {:else}
          <span class="go">Open the projects <ArrowRight size={16} /></span>
        {/if}
      </div>
    </a>
  </section>
</div>

<style>
  .home {
    max-width: 1320px;
    margin: 0 auto;
    padding: 0 var(--gutter) calc(56px + var(--tabbar));
  }
  .hero {
    position: relative;
    display: grid;
    grid-template-columns: minmax(280px, 0.8fr) 1.6fr;
    align-items: center;
    gap: 24px;
    min-height: min(56vh, 560px);
    padding: 24px 0 8px;
  }
  .glow {
    position: absolute;
    inset: -80px -10vw 0;
    z-index: -1;
    background:
      radial-gradient(ellipse 55% 60% at 68% 55%, color-mix(in oklab, var(--steel) 55%, transparent), transparent 70%),
      radial-gradient(ellipse 30% 40% at 20% 30%, color-mix(in oklab, var(--ember) 10%, transparent), transparent 70%);
    pointer-events: none;
  }
  .intro h1 {
    font-size: clamp(34px, 4.6vw, 58px);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.02;
    margin: 12px 0 18px;
  }
  .ident {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 10px;
    color: var(--text-2);
    font-size: 15px;
  }
  .ident .dot {
    color: var(--ember);
  }
  .art {
    min-width: 0;
  }
  .art img {
    width: 100%;
    border-radius: var(--r-4);
    object-fit: cover;
    aspect-ratio: 16 / 9;
    box-shadow: var(--shadow-3);
  }

  .tiles {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px;
    margin-top: 12px;
  }
  .tile {
    position: relative;
    display: flex;
    flex-direction: column;
    border-radius: var(--r-4);
    overflow: hidden;
    background: var(--surface);
    border: 1px solid var(--line-soft);
    box-shadow: var(--shadow-2);
    color: var(--text);
    transition:
      transform var(--t) var(--ease),
      border-color var(--t),
      box-shadow var(--t);
  }
  .tile:hover {
    transform: translateY(-3px);
    border-color: var(--line);
    box-shadow: var(--shadow-3);
    color: var(--text);
  }
  .pic {
    position: relative;
    height: 220px;
    overflow: hidden;
    border-bottom: 1px solid var(--line-soft);
  }
  .manual .pic {
    background:
      linear-gradient(180deg, transparent 50%, var(--surface) 100%),
      radial-gradient(ellipse at 30% 60%, color-mix(in oklab, var(--steel) 50%, transparent), transparent 70%),
      var(--bg-raise);
  }
  .crop {
    position: absolute;
    width: 190%;
    left: -12%;
    top: -18%;
    opacity: 0.9;
  }
  .projects .pic {
    display: grid;
    place-items: center;
    background:
      radial-gradient(circle at 50% 55%, color-mix(in oklab, var(--ember) 16%, transparent), transparent 45%),
      radial-gradient(circle at 50% 55%, color-mix(in oklab, var(--steel) 60%, transparent), transparent 70%),
      var(--bg-raise);
  }
  .rotor {
    animation: turn 40s linear infinite;
    filter: drop-shadow(0 18px 30px rgb(0 0 0 / 0.5));
  }
  .orbit {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    pointer-events: none;
  }
  .planet {
    position: absolute;
    display: grid;
    place-items: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--surface-2);
    border: 1px solid var(--line);
    color: var(--sky);
    --a: calc(var(--i) / var(--n) * 360deg + 30deg);
    transform: translate(calc(cos(var(--a)) * 190px), calc(sin(var(--a)) * 72px));
  }
  .body {
    padding: 20px 24px 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .body h2 {
    font-size: 26px;
    font-weight: 680;
  }
  .body p {
    color: var(--text-2);
  }
  .go,
  .status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
    font-weight: 580;
    font-size: 14px;
    color: var(--sky);
  }
  .status {
    color: var(--accent-2);
  }
  .pip {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--ember);
    box-shadow: 0 0 0 4px var(--accent-soft);
  }
  @keyframes turn {
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 900px) {
    .hero {
      grid-template-columns: 1fr;
      min-height: 0;
      gap: 8px;
      padding-top: 8px;
    }
    .art {
      order: -1;
    }
    .tiles {
      grid-template-columns: 1fr;
      gap: 16px;
    }
    .pic {
      height: 170px;
    }
    .planet {
      transform: translate(calc(cos(var(--a)) * 130px), calc(sin(var(--a)) * 58px));
    }
  }
</style>
