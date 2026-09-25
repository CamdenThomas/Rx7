<!-- The app's mark: a Wankel rotor, the heart of the 12A this car runs on. -->
<script lang="ts">
  let { size = 28 }: { size?: number } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
  <path
    d="M32 9.5 A41.57 41.57 0 0 1 52.78 45.5 A41.57 41.57 0 0 1 11.22 45.5 A41.57 41.57 0 0 1 32 9.5 Z"
    fill="var(--steel)"
    stroke="var(--foam)"
    stroke-width="3.4"
    stroke-linejoin="round"
  />
  <circle cx="32" cy="33.5" r="7.5" fill="none" stroke="var(--sky)" stroke-width="2.8" />
  <circle cx="32" cy="33.5" r="2.8" fill="var(--ember)" />
</svg>
