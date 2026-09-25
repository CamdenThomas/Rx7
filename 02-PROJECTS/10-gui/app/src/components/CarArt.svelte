<!--
  The FB RX-7 in profile, drawn as a blueprint in the app's palette. It stands in for his
  photos until 01-REFERENCE/photos holds some (D-404); it carries no dimension or fact.
-->
<script lang="ts">
  let { animate = true }: { animate?: boolean } = $props();

  const body =
    'M40 240 C22 240 12 233 11 222 L10 197 C10 189 14 185 22 183 L30 174 C35 166 45 161 62 158 ' +
    'C160 146 262 131 348 117 L516 14 C548 5 586 3 614 7 C702 19 810 52 902 85 C932 94 960 97 985 99 ' +
    'L991 112 L996 150 C1000 162 1000 204 998 228 C996 238 988 242 975 242 L849 245 ' +
    'A84 84 0 0 0 680 245 L284 245 A84 84 0 0 0 116 245 Z';
  const glass = 'M376 111 L511 27 C546 17 590 15 632 19 C700 28 770 49 812 64 C800 80 792 90 786 97 L376 111 Z';
  const wheels = [200, 764];
  const fins = Array.from({ length: 6 }, (_, i) => (i * Math.PI) / 3);
</script>

<svg class="car" class:animate viewBox="-20 -30 1040 350" role="img" aria-label="A 1982 Mazda RX-7 in profile">
  <defs>
    <linearGradient id="car-body" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="var(--steel)" stop-opacity="0.55" />
      <stop offset="1" stop-color="var(--ink)" stop-opacity="0.2" />
    </linearGradient>
    <linearGradient id="car-glass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="var(--sky)" stop-opacity="0.22" />
      <stop offset="1" stop-color="var(--sky)" stop-opacity="0.04" />
    </linearGradient>
    <pattern id="car-grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0 L0 0 0 40" fill="none" stroke="var(--sky)" stroke-opacity="0.07" stroke-width="1" />
    </pattern>
  </defs>

  <rect x="-20" y="-30" width="1040" height="350" fill="url(#car-grid)" />
  <g class="construction">
    <line x1="-20" y1="300" x2="1020" y2="300" />
    {#each wheels as x (x)}
      <line x1={x} y1="-10" x2={x} y2="316" />
      <line x1={x - 110} y1="231" x2={x + 110} y2="231" />
    {/each}
  </g>

  <path class="line fill" d={body} fill="url(#car-body)" />
  <path class="line" d={glass} fill="url(#car-glass)" />
  <g class="line detail">
    <path d="M606 18 L604 105" />
    <path d="M364 120 L366 244" />
    <path d="M608 106 L612 244" />
    <path d="M286 196 L676 192" />
    <path d="M18 206 L112 206" />
    <path d="M852 208 L996 206" />
    <path d="M70 156 L150 147" />
    <path d="M385 110 C392 98 408 96 414 104 L406 113 Z" />
    <path d="M568 150 L594 149" />
    <rect x="838" y="118" width="26" height="18" rx="3" />
    <rect x="30" y="192" width="18" height="7" rx="2" class="amber" />
    <rect x="968" y="150" width="14" height="8" rx="2" class="red" />
  </g>

  {#each wheels as x (x)}
    <g class="wheel" transform="translate({x} 231)">
      <circle r="69" class="tyre" />
      <circle r="58" class="line" />
      <circle r="41" class="line rim" />
      {#each fins as a (a)}
        <line class="line" x1={Math.cos(a) * 14} y1={Math.sin(a) * 14} x2={Math.cos(a) * 36} y2={Math.sin(a) * 36} />
      {/each}
      <circle r="9" class="hub" />
    </g>
  {/each}
</svg>

<style>
  .car {
    width: 100%;
    height: auto;
    display: block;
    overflow: visible;
  }
  .construction line {
    stroke: var(--sky);
    stroke-opacity: 0.22;
    stroke-width: 1;
    stroke-dasharray: 6 8;
  }
  .line {
    fill: none;
    stroke: color-mix(in oklab, var(--sky) 80%, var(--foam));
    stroke-width: 2;
    stroke-linejoin: round;
    stroke-linecap: round;
  }
  .line.fill {
    stroke: var(--foam);
    stroke-width: 2.4;
  }
  .detail {
    stroke-opacity: 0.7;
    stroke-width: 1.5;
  }
  .amber {
    fill: var(--ember);
    stroke: none;
  }
  .red {
    fill: color-mix(in oklab, var(--ember) 70%, #b0303a);
    stroke: none;
  }
  .tyre {
    fill: color-mix(in oklab, var(--ink) 60%, #000);
    stroke: var(--foam);
    stroke-width: 2.4;
  }
  .rim {
    fill: color-mix(in oklab, var(--steel) 35%, transparent);
  }
  .hub {
    fill: var(--ember);
  }
  .animate path,
  .animate rect:not([fill]),
  .animate circle,
  .animate line {
    stroke-dasharray: 2400;
    stroke-dashoffset: 2400;
    animation: draw 1.6s var(--ease) forwards;
  }
  .animate .construction line {
    stroke-dasharray: 6 8;
    stroke-dashoffset: 0;
    animation: fade 1.2s both;
  }
  .animate .wheel circle,
  .animate .wheel line {
    animation-delay: 0.35s;
  }
  @keyframes draw {
    to {
      stroke-dashoffset: 0;
    }
  }
</style>
