#!/usr/bin/env bash
# Pull an installed package (base + splits) from a connected Android device or emulator.
# Usage: tools/pull_apk.sh com.OProjects.FLS
# Requires: adb (Android platform-tools), device with USB debugging on, app installed from Google Play.
set -euo pipefail
pkg="${1:?package name, e.g. com.OProjects.FLS}"
here="$(cd "$(dirname "$0")/.." && pwd)"
out="$here/vendor/$pkg"
mkdir -p "$out"
adb shell pm path "$pkg" | tr -d '\r' | sed 's/^package://' | while read -r p; do
  echo "pulling $p"
  adb pull "$p" "$out/"
done
{
  echo "package: $pkg"
  echo "pulled:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  adb shell dumpsys package "$pkg" | tr -d '\r' | grep -E 'versionName|versionCode' | sed 's/^ *//'
  echo "sha256:"
  (cd "$out" && shasum -a 256 *.apk)
} > "$out/MANIFEST.txt"
cat "$out/MANIFEST.txt"
