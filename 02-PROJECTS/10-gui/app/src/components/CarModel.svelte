<!--
  The car in 3D (D-415, D-420): the FB body from the free CAD library, scaled to the factory
  size, on the bought 1978 model's wheels, built by 01-REFERENCE/model/blend.py. Turned with
  the mouse, repainted from the swatch (materials named carpaint). Desktop only — the model
  stays on the PC and out of git, so the phone shows the renders instead. It is low-poly and
  has no interior, and nothing is measured from it here.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import { RotateCcw } from '@lucide/svelte';

  let { src }: { src: string } = $props();

  const SILVER = '#b9bec4';
  let host: HTMLDivElement;
  let paint = $state(SILVER);
  let status = $state<'loading' | 'ready' | 'failed'>('loading');
  let setPaint: (hex: string) => void = () => undefined;

  $effect(() => setPaint(paint));

  onMount(() => {
    let stop = () => {};
    void (async () => {
      const THREE = await import('three');
      const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');
      const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls.js');
      const { RoomEnvironment } = await import('three/examples/jsm/environments/RoomEnvironment.js');

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
      renderer.toneMapping = THREE.AgXToneMapping;
      host.appendChild(renderer.domElement);
      const scene = new THREE.Scene();
      scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
      const camera = new THREE.PerspectiveCamera(30, 1, 10, 20000);
      camera.position.set(-620, 260, -640);
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.enablePan = false;
      controls.minDistance = 450;
      controls.maxDistance = 1600;
      controls.maxPolarAngle = Math.PI * 0.49;
      controls.target.set(0, 55, 0);
      controls.autoRotate = true;
      controls.autoRotateSpeed = 0.6;
      controls.addEventListener('start', () => (controls.autoRotate = false));

      const resize = () => {
        const { clientWidth: w, clientHeight: h } = host;
        renderer.setSize(w, h, false);
        camera.aspect = w / Math.max(h, 1);
        camera.updateProjectionMatrix();
      };
      const observer = new ResizeObserver(resize);
      observer.observe(host);
      resize();

      let frame = 0;
      const loop = () => {
        frame = requestAnimationFrame(loop);
        controls.update();
        renderer.render(scene, camera);
      };
      stop = () => {
        cancelAnimationFrame(frame);
        observer.disconnect();
        controls.dispose();
        renderer.dispose();
        renderer.domElement.remove();
      };

      try {
        const gltf = await new GLTFLoader().loadAsync(src);
        const body: InstanceType<typeof THREE.MeshStandardMaterial>[] = [];
        gltf.scene.traverse((o) => {
          const m = (o as InstanceType<typeof THREE.Mesh>).material as InstanceType<typeof THREE.MeshStandardMaterial> | undefined;
          if (m?.name?.startsWith('carpaint') && !body.includes(m)) body.push(m);
        });
        setPaint = (hex) => body.forEach((m) => m.color.set(hex).convertSRGBToLinear());
        setPaint(paint);
        scene.add(gltf.scene);
        status = 'ready';
        loop();
      } catch {
        status = 'failed';
      }
    })();
    return () => stop();
  });
</script>

<div class="model">
  <div class="canvas" bind:this={host}></div>
  {#if status === 'loading'}<p class="note faint">Loading the model…</p>{/if}
  {#if status === 'failed'}<p class="note faint">The model is not built on this PC — 01-REFERENCE/model/README.md.</p>{/if}
  {#if status === 'ready'}
    <div class="paint">
      <label title="Paint"><input type="color" bind:value={paint} aria-label="Paint colour" /></label>
      {#if paint !== SILVER}
        <button class="btn small ghost" onclick={() => (paint = SILVER)}><RotateCcw size={14} /> Sunbeam Silver</button>
      {/if}
    </div>
    <p class="caveat faint">The FB body at factory size; the wheels are the 1978 model's. Drag to turn it.</p>
  {/if}
</div>

<style>
  .model {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: var(--r-4);
    overflow: hidden;
    background: radial-gradient(ellipse at 50% 70%, color-mix(in oklab, var(--steel) 45%, transparent), transparent 70%), var(--bg-raise);
    box-shadow: var(--shadow-3);
  }
  .canvas,
  .canvas :global(canvas) {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    cursor: grab;
  }
  .note {
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    font-size: 13px;
  }
  .paint {
    position: absolute;
    top: 12px;
    right: 12px;
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .paint input {
    width: 30px;
    height: 30px;
    padding: 0;
    border: 1px solid var(--line);
    border-radius: 50%;
    background: none;
    cursor: pointer;
  }
  .caveat {
    position: absolute;
    left: 14px;
    bottom: 10px;
    font-size: 12px;
  }
</style>
