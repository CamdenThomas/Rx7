# Rx7 — the app

The car's record, read and answered: a desktop app for the Fedora PC and an Android app for
the Galaxy, from one codebase (D-403). The design, and why it is this way, is pitched in
[`../README.md`](../README.md). This page is how to build it, test it and install it.

## How it is put together

```
src/                    the interface (Svelte 5 + TypeScript), shared by both apps
  screens/              one file per screen; screens/project/ holds a project's pages
  components/           the pieces screens share: the shell, focus navigation, chat, prose
  lib/app.svelte.ts     the app's state: the record snapshot and what each screen asks of it
  lib/platform/         the only code that differs by device, behind one interface (types.ts)
    desktop.ts            the Tauri commands below
    phone.ts              GitHub + rx7.py in Pyodide + answers kept on the phone until sent
    web.ts                the browser build the tests and screenshots run on
  lib/logs/             Connect and log (BL2) and the log pipeline (BL3), pure TypeScript:
    layout.generated.ts   the log link's bytes, generated from the record - never edited by hand
    format.ts · protocol.ts   the card's files and the link's messages, decoded
    transport.ts          the only file that imports the Bluetooth plugin; its one write is guarded
    pull.ts · pipeline.ts the pull's state machine; drives -> kind=drive answers and digests
    fake.ts · synth.ts    a stand-in ICU and a synthetic drive (tests; the browser build's ?ble=fake)
  app.css               the design system: his five colours as tokens, type, spacing, pieces
src-tauri/              the native shell (Rust, Tauri 2)
  src/logs.rs           both apps: the folder the pulled logs are written to (fixed file names)
  src/desktop/          the desktop's hands: record.rs runs rx7.py, git.rs commits and syncs,
                        claude.rs runs headless Claude Code, photos.rs serves the tree's photos
  tauri.conf.json       release config — only the `default` capability
  tauri.test.conf.json  merged into test builds only: lets a test APK reach the stand-in GitHub
  gen/android/          the generated Android project (Gradle)
scripts/                stage-core.mjs copies Pyodide into public/; fixture.mjs writes a test
                        copy of the record for the browser build; gen-log-tables.mjs writes
                        lib/logs/layout.generated.ts; icu-drive.cpp writes a drive with the
                        ICU firmware's own LogStore, for the decoder's tests
tests/                  unit tests (Vitest); fixtures/icu-drive/ is that firmware-written drive
e2e/                    end-to-end tests (Playwright) and fake-github.mjs, a stand-in GitHub
```

Every fact comes from the record through `tools/rx7.py`: the desktop runs `rx7.py export`
and `rx7.py answer`; the phone runs the same `rx7.py` compiled to WebAssembly (Pyodide)
against the files it fetched from GitHub. The app keeps no fact of its own (CLAUDE.md §1).

## What this machine needs

Installed once on the Fedora PC (`rx7.py doc machine`):

- `sudo dnf install nodejs npm webkit2gtk4.1-devel openssl-devel curl wget file libappindicator-gtk3-devel librsvg2-devel libxdo-devel gcc gcc-c++ make unzip`
- Rust through rustup (`~/.cargo`), with the Android targets:
  `rustup target add aarch64-linux-android x86_64-linux-android`
- JDK 21 in `~/.local/jdk/jdk-21.0.12.1+1` (Fedora has no JDK 21 package).
- The Android SDK in `~/Android/Sdk`: platform-tools, build-tools 35.0.0, platforms
  android-35 and 36, NDK 27.2.12479018, and for the emulator the
  `system-images;android-35;google_apis;x86_64` image.
- For the desktop end-to-end test: `cargo install tauri-driver`; `WebKitWebDriver` comes with
  `webkitgtk6.0`.
- `npm install` in this folder.

Installed once on the Mac (arm64, macOS 26; D-454), for the desktop app only — no Android
targets here:

- Rust through the official rustup installer, stable toolchain, default profile, into
  `~/.cargo` (Rust 1.99.0 on 2026-10-09):
  `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y`.
  It wrote one line, `. "$HOME/.cargo/env"`, into `~/.zshenv` and a new `~/.profile`.
- Node 24 (fnm) and the Xcode Command Line Tools were already there; Homebrew's `node` does
  the same job if fnm is not.
- `npm install` in this folder, and `npx playwright install chromium` for the browser tests.
- **Pin `SDKROOT` for every cargo build.** The Command Line Tools 26.6 linker cannot read the
  27.0 SDK that sits beside it (`tapi error: malformed file … unknown architecture`), and
  `xcrun` picks 27.0 by default; the firmware scripts pin the same SDK:
  `export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk`.

The Android build wants these set in the shell:

```sh
export PATH=$HOME/.cargo/bin:$PATH
export JAVA_HOME=$HOME/.local/jdk/jdk-21.0.12.1+1
export ANDROID_HOME=$HOME/Android/Sdk NDK_HOME=$HOME/Android/Sdk/ndk/27.2.12479018
```

## Run it while working on it

```sh
npm run dev          # the browser build at http://localhost:5173 (a copy of the record)
npx tauri dev        # the real desktop window, on the real tree
```

## Test it

```sh
npm run check        # types: svelte-check
npm test             # unit tests (Vitest), tests/logs.test.ts among them
npm run gen:logs -- --check   # rc 1 when the log link's generated tables are behind the record
npm run e2e          # every screen at desktop and phone size, and the phone's whole path
                     # (sync, answer offline, send) against the stand-in GitHub

npx tauri build --no-bundle && node e2e/desktop.mjs    # the desktop binary itself, through
                     # WebDriver: export, answer, commit, push, sync, withdraw — on a sandbox
```

On the Mac, `check`, `npm test` and `npm run e2e` run; the WebDriver test does not, because
`tauri-driver` exists only for Linux and Windows, so it stays on the Fedora PC (D-454).

**The phone app on an emulator.** Build a test APK that talks to the stand-in GitHub, then
drive its WebView with Playwright's Android API:

```sh
VITE_RX7_API=http://localhost:5199/api VITE_RX7_RAW=http://localhost:5199/raw \
  npx tauri android build --debug --apk --target x86_64 --config src-tauri/tauri.test.conf.json
$ANDROID_HOME/emulator/emulator -avd rx7test -no-window -no-audio -gpu swangle_indirect -memory 2048 -no-snapshot
adb reverse tcp:5199 tcp:5199
adb install -r src-tauri/gen/android/app/build/outputs/apk/universal/debug/app-universal-debug.apk
```

Two things learned the hard way on this PC:

- **Use `-gpu swangle_indirect`.** The emulator's default software renderer
  (`swiftshader_indirect`) crashes about 20 seconds into every boot here.
- **Mind the memory.** A Gradle build plus the emulator plus VS Code ran this 15 GB machine
  out of memory once and took VS Code down. Stop the Gradle and Kotlin daemons after a build
  (`(cd src-tauri/gen/android && ./gradlew --stop)`) before booting the emulator.

## Connect and log (Bluetooth)

Work rows BL2 and BL3 (02-APP), built from electrical D-478, D-483, D-493, D-494 and D-495.

**The screens.** The Manual's header has **Connect and log**: one press finds `RX7-ICU`,
connects, reads `info` (and stops on a log protocol it does not know), sets the ICU's clock
when it is unset or off by more than 2 s, lists the drives not yet pulled, and pulls each one's
summary and then its once-a-second log from the last byte this device holds; every tier is
CRC-32-checked before it is acknowledged. Its page (`#/manual/connect`) shows the progress
(drives, bytes, rate), what was saved, and the drives this device holds, each with **Pull full
log** - the only way the full log is ever fetched. The first connection makes the phone pair:
a long press of the cluster's page button shows a six-digit key to type. **Bluetooth scan**
(`#/manual/scan`) lists every advertisement - name, address, RSSI, manufacturer data - and the
Ionic battery's pack millivolts when it is heard (D-330): work row BL5's proof page.

**What reaches the record.** One `kind=drive` answer per drive in 00-CAR's inbox, through the
same `app.save` path as Log drive (target `drive-<end time>`, choice the end odometer in whole
miles, `at` the drive's end, his note the distance, duration, flags and - when the ICU's clock
was unset - that the date is approximate). A drive that did not move, or whose odometer the ICU
does not know yet (F-007), is not filed. The per-drive digest (every channel's min, max, mean,
blanks and fault bits) is kept beside the files for BL4.

**The plugin**, pinned exactly (confirm at each bump - its API has moved between minor versions):
`tauri-plugin-blec = "=0.17.0"` (crates.io) and `@mnlphlp/plugin-blec` `0.17.0` (npm), the
newest on both registries on 2026-10-12. It is registered with `try_init`, so a machine with no
adapter still opens; `blec:default` is in `capabilities/default.json`.

**Permissions** (D-495):

- Android - `gen/android/app/src/main/AndroidManifest.xml`: `BLUETOOTH_SCAN` with
  `neverForLocation` and `BLUETOOTH_CONNECT` (API 31 up); `ACCESS_FINE_LOCATION` and
  `ACCESS_COARSE_LOCATION` only to API 30 (`maxSdkVersion="30"`, `tools:node="replace"` over
  the plugin's own lines, which ask for location on every API). The plugin also merges
  `BLUETOOTH` (to API 30), `BLUETOOTH_ADMIN` and `uses-feature bluetooth_le`. The Scan and
  Connect pages ask at run time.
- macOS - `src-tauri/Info.plist` (merged into the bundle): `NSBluetoothAlwaysUsageDescription`.
  The first scan raises the system prompt.
- Fedora - BlueZ over D-Bus; the user may need the `bluetooth` group (confirm on the PC).

**Where the logs live.** `app_data_dir()/logs/<seq>/` - `summary.bin`, `thin.bin`, `full.bin`
and `digest.json`, the sequence as eight digits as on the card: on the Mac
`~/Library/Application Support/com.camdenthomas.rx7/logs/`, on Fedora
`~/.local/share/com.camdenthomas.rx7/logs/`, on the phone the app's private data folder. The
Connect page prints the exact path. Out of git and out of the tree; a second home is P55's,
still open. What each drive's pull has reached (the resume offsets) is in the app's own store.

**When the record's log tables change** (log_channels, log_link, log_files, or
`icu/log_store.h`'s layout strings): `npm run gen:logs` (it runs `rx7.py export`; on this Mac
with `DEVELOPER_DIR=/Library/Developer/CommandLineTools`), then `npm test`. A header whose
layout CRC is not the generated one is refused. To rewrite the firmware-made fixture:
`c++ -std=c++17 -O2 scripts/icu-drive.cpp -o /tmp/icu-drive && /tmp/icu-drive tests/fixtures/icu-drive`.

**Try it without a car:** `npm run dev`, then open
`http://localhost:5173/?ble=fake#/manual/connect`: a stand-in ICU with two drives and a
battery advertisement.

## Install it

**On the desktop.** `npx tauri build` makes an RPM in
`src-tauri/target/release/bundle/rpm/`; `sudo dnf install ./Rx7-*.rpm` puts Rx7 in the
application menu. It opens on `~/docs/storage/Rx7`; Settings can point it elsewhere.

**On the Mac.** The `rpm` target means nothing here, so name the bundle:

```sh
export PATH=$HOME/.cargo/bin:$PATH SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk
npx tauri build --bundles app
rm -rf /Applications/Rx7.app && ditto src-tauri/target/release/bundle/macos/Rx7.app /Applications/Rx7.app
```

That makes `src-tauri/target/release/bundle/macos/Rx7.app` (about 12 MB, arm64) and puts
it in `/Applications/Rx7.app`, where Launchpad and Spotlight find it. It is signed ad hoc
(`bundle.macOS.signingIdentity: "-"`) and not notarized: a copy built on this Mac opens with
no warning, but `spctl` rejects it and a copy downloaded onto another Mac would be blocked.
It opens on `~/dev/Rx7` (whichever of the two paths exists); Settings can point it
elsewhere.

**On the phone.** With the Galaxy plugged in and USB debugging on (Settings → About phone →
Software information → tap Build number seven times, then Developer options → USB debugging):

```sh
npx tauri android build --debug --apk --target aarch64
adb install -r src-tauri/gen/android/app/build/outputs/apk/universal/debug/app-universal-debug.apk
```

That is a build signed with the development key, which Android installs from a cable with no
store. A release build (`--debug` left off) comes out unsigned and needs a signing key set up
in `gen/android` first; for one phone the debug build is enough.

Then open Rx7 → Settings and paste a GitHub fine-grained token with access to
`CamdenThomas/Rx7` only, permission Contents: read and write. The phone reads without it; it
needs it only to send answers.
