# Android emulator setup (macOS)

Purpose: install the app from Google Play under your own account, then pull the installed package with
adb. Status: written 2026-11-18, **not yet run**. Correct this file with whatever actually happens.

## Steps

1. **Install and create the emulator.** In Terminal on the Mac:
   `cd` to this folder, then `tools/setup_emulator.sh`.
   It installs a JDK and the Android command-line tools via Homebrew, downloads an Android 14 system
   image *with Google Play*, and creates an AVD called `fepro`.
   The image must be a `google_apis_playstore` one. Plain `google_apis` and AOSP images have no Play
   Store. (GUI alternative: Android Studio > Device Manager > create a Pixel device and pick a system
   image with the Play Store icon.)
2. **Start it:** `emulator -avd fepro &` and wait for the home screen. Check `adb devices` lists it.
3. **Sign in to Google Play** inside the emulator with the account that will own the purchase.
4. **Install** "Flat Earth" (free, `com.OProjects.FLS`). Open it once so any first-run asset download
   completes. Install "Flat Earth Pro" (`com.OProjects.FLSPro`) if and when the extra projections are
   needed.
5. **Pull the package:** `tools/pull_apk.sh com.OProjects.FLS`
   Output lands in `vendor/com.OProjects.FLS/` with a `MANIFEST.txt` (version + SHA-256).
6. **Fingerprint:** `tools/triage.sh vendor/com.OProjects.FLS/*.apk`

## Things that may go wrong

- **Intel Mac.** The emulator runs x86_64 images. If the app ships arm64-only native code, Play will
  show it as incompatible or it will crash on launch. A physical Android device is then the easy route.
  On Apple Silicon the arm64 image avoids this.
- **`adb pull` permission denied.** Play Store images are production builds without root. Pulling a
  user app's APK by the path `pm path` reports normally works; if it does not, try
  `adb shell cp <path> /sdcard/Download/ && adb pull /sdcard/Download/<file>`.
- **Extra data outside the APK.** A 235 MB app may ship split APKs or an expansion file (`.obb`) or
  Play Asset Delivery packs. `pm path` lists splits; also check `adb shell ls /sdcard/Android/obb/<package>`.
  Note what you find in `MANIFEST.txt`.
- **Licence check on the paid build.** Pro may verify its Play licence at launch. That only matters for
  running it, and it will be running on the account that bought it.
- **Brew cask name / SDK path differ.** If `sdkmanager` is not found after install, run
  `brew info --cask android-commandlinetools` for the actual path and set `ANDROID_HOME` to it.

## The emulator is also the capture rig for phase 1

- Screenshot: `adb exec-out screencap -p > evidence/captures/<name>.png`
- Screen recording (max 3 min per file): `adb shell screenrecord /sdcard/cap.mp4`, Ctrl-C, then
  `adb pull /sdcard/cap.mp4 evidence/captures/<name>.mp4`
- Set device GPS if the app uses it for "my location": `adb emu geo fix <lon> <lat>` (longitude first).
- Set device clock only if the app has no time control of its own; prefer the in-app time control so
  the capture shows the app time on screen.
