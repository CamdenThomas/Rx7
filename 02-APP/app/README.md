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
  app.css               the design system: his five colours as tokens, type, spacing, pieces
src-tauri/              the native shell (Rust, Tauri 2)
  src/desktop/          the desktop's hands: record.rs runs rx7.py, git.rs commits and syncs,
                        claude.rs runs headless Claude Code, photos.rs serves the tree's photos
  tauri.conf.json       release config — only the `default` capability
  tauri.test.conf.json  merged into test builds only: lets a test APK reach the stand-in GitHub
  gen/android/          the generated Android project (Gradle)
scripts/                stage-core.mjs copies Pyodide into public/; fixture.mjs writes a test
                        copy of the record for the browser build
tests/                  unit tests (Vitest)
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
npm test             # unit tests (Vitest)
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
