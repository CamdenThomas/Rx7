<!-- A project's icon, named in its _project.csv `icon` row (D-406 6.1). -->
<script lang="ts">
  import {
    AppWindow, Armchair, Battery, Car, Cog, Cpu, Disc3, Droplets, Folder, Fuel, Gauge, Lightbulb,
    Paintbrush, Radio, Shield, Snowflake, Wind, Wrench, Zap,
  } from '@lucide/svelte';

  let { name = 'folder', size = 20 }: { name?: string; size?: number } = $props();

  const ICONS = {
    'app-window': AppWindow, armchair: Armchair, battery: Battery, car: Car, cog: Cog, cpu: Cpu,
    disc: Disc3, droplets: Droplets, folder: Folder, fuel: Fuel, gauge: Gauge, lightbulb: Lightbulb,
    paintbrush: Paintbrush, radio: Radio, shield: Shield, snowflake: Snowflake, wind: Wind,
    wrench: Wrench, zap: Zap,
  } as const;

  const Icon = $derived(ICONS[name as keyof typeof ICONS] ?? Folder);
</script>

<Icon {size} strokeWidth={1.8} />
