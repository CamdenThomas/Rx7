# What the Rx7 app bundles, and under which licences

Read on 2026-09-26 from each package's own `package.json` (plan P52). The app's own code has no
licence stated yet: block REF.01 asks Camden which.

| Package | Version | Licence | What it is |
| --- | --- | --- | --- |
| @fontsource-variable/inter | 5.3.0 | OFL-1.1 | the Inter typeface |
| @fontsource-variable/jetbrains-mono | 5.3.0 | OFL-1.1 | the JetBrains Mono typeface |
| @lucide/svelte | 1.x | ISC | the icon set |
| @tauri-apps/api, plugin-http, plugin-opener, plugin-store | 2.x | MIT OR Apache-2.0 | the shell's bridge |
| pyodide | 314.0.7 | MPL-2.0 | Python in WebAssembly (Android build only) |
| three | 0.186 | MIT | the desktop's 3D view |
| Rust crates (tauri, tauri-plugin-*, serde, serde_json) | see Cargo.lock | MIT OR Apache-2.0 | the shell |

Regenerate the table with:

```sh
node -e "const p=require('./package.json');for(const d of Object.keys(p.dependencies)){const j=require(d+'/package.json');console.log(d,j.version,j.license)}"
```

The three renders in `public/car/` are pictures made from a bought model (01-REFERENCE S-037) and
a free CAD library (D-418); the model files themselves are never in the repository.
