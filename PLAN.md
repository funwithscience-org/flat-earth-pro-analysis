# Plan

## Ground rules

1. **Lawfully obtained copy only.** Install from Google Play on a device or emulator signed in to
   Steve's account, then pull the installed package with adb. No APK mirror sites: they are untrusted
   binaries and, for the paid build, unlicensed copies.
2. **No binaries or decompiled source in git, ever.** `vendor/` is ignored. What goes in the repo is our
   own prose, our own test captures, our own reference calculations, and at most short excerpts
   (a constant, a formula, a function name) needed to support a specific claim.
3. **Behaviour first, code second.** Every published claim should stand on a black-box test anyone with
   the app can repeat. Static analysis explains *why* the behaviour occurs; it is corroboration.
   (Legal aside, not legal advice: UK law is clearly comfortable with a lawful user observing and testing
   how a program behaves; decompilation is a narrower permission. Get a view on this before publishing
   anything that leans on decompiled code.)
4. **The app only.** No probing of the developer's servers or weather/API backends. If a security
   problem turns up incidentally, it goes privately to the developer, not on the site.
5. **No personal details** of the developer beyond the public developer name.
6. **Steelman.** The developer's own store listing says the map and sky views share one astronomical
   model, and the app may make no claim to be a physical flat model. The finding is not "gotcha, globe
   code"; it is whether the sky view can be produced from the map view's own geometry. See
   "The other side" below.

## Phase 0 - Acquire and fingerprint

- Start with the **free** build `com.OProjects.FLS`: its listing says it includes both Map Mode and the
  sky simulation, so the star-trails question may not need the paid build at all. Buy
  `com.OProjects.FLSPro` only if the extra projections matter (they probably do for phase 2, item 2).
- No Android device needed: `tools/emulator-setup.md` + `tools/setup_emulator.sh` set up an emulator
  with Google Play on the Mac. It doubles as the capture rig for phase 1.
- `tools/pull_apk.sh <package>` pulls base + split APKs via adb and records SHA-256, versionName and
  versionCode in `vendor/<package>/MANIFEST.txt`. Record the version in every finding.
- iOS build: skip for static work (App Store binaries are encrypted; removing that is a line not worth
  crossing). The iPhone app is still useful for phase 1 captures.

## Phase 1 - Black-box tests (the publishable core)

Run `analysis/star-trails/test-matrix.md`. For each case capture the map view and the sky view at the
same app time and location, and compare three things:

- **A. App sky view** - what it draws.
- **B. Globe ephemeris** - Skyfield/astropy for the same place and instant.
- **C. Literal flat rendering** - what an observer would see if the map view were physically real:
  bodies at a fixed height over the AE plane at their plotted positions, straight-line sight.

Expected if the hypothesis holds: A matches B to within drawing precision and disagrees with C in
direction, elevation, rotation sense and rise/set behaviour. `tools/` will get a small reference
calculator for B and C (to be written in this phase).

## Phase 2 - Triage the package

`tools/triage.sh vendor/<package>/base.apk` lists native libs, managed assemblies and large assets to
identify the engine. Unverified guess from the package naming and 235 MB size: Unity.

| If it is | Then |
|---|---|
| Unity, Mono (`Assembly-CSharp.dll` present) | ILSpy gives near-source C#. Easy. |
| Unity, IL2CPP (`libil2cpp.so` + `global-metadata.dat`) | Il2CppDumper for names/signatures, Ghidra for bodies. Class and method names survive; logic is slower to read. |
| Native Android (Kotlin/Java) | jadx. |
| Flutter / other | Reassess; black-box evidence carries more weight. |

Shaders and scene assets (AssetRipper for Unity) matter as much as code: the day/night terminator and
the map projections are likely shader-side.

## Phase 3 - Static analysis by function

Work through `analysis/function-map.md`. One markdown file per function in `analysis/static/`, each
stating: what the function does, the inputs it takes, the coordinate system it works in, the evidence
(constant, formula, call graph), and a confidence level.

Priority order: 7 (sky view + fly-in) -> 4 (local alt/az) -> 1 (ephemeris core) -> 3 (terminator) ->
2 (projections) -> the rest.

## Phase 4 - Write-up

Adversarial review pass (FIX/SOFTEN/ADD/NIT) before anything goes in `docs/`. Natural home for the
star-trails result is a tab or companion page to funwithscience.net/star-trails/.

## The other side

- The app may be an honest visualisation tool. An AE map with sub-solar and sub-lunar points is a
  legitimate map; using spherical astronomy to place them is not hypocrisy unless the app or its
  marketing claims a flat physical model. Check what the app itself asserts before characterising it.
- "Uses globe formulas" does not prove the Earth's shape. The flat-earth reply is that the formulas are
  empirical fits to observed cycles. The claim that survives that reply is narrower and stronger:
  no single flat geometry reproduces the sky view, which is why comparison C matters.
- A sky view centred on the observer is what *any* planetarium does. The switch from map scene to sky
  scene is only interesting if the sky scene takes nothing from the map scene except clock, latitude
  and longitude. That is a specific, checkable claim; phase 3 item 7 is where it is checked.
- Developer intent is unknowable from code. Write about what the software does.

## GitHub

Local repo is initialised here on `main`. The funwithscience PAT can push but cannot create org repos,
so: create `funwithscience-org/flat-earth-pro-analysis` in the GitHub UI (suggest **private** until
phase 4 is reviewed), then push. Pages from `/docs` only when there is something reviewed to publish.
