#!/usr/bin/env bash
# One-time setup of an Android emulator WITH Google Play on macOS, for obtaining the app lawfully.
# Run on the Mac itself (Terminal), not in a Claude session. Untested as of 2026-11-18: read before running.
# Requires Homebrew. Downloads roughly 2-3 GB.
set -euo pipefail

AVD_NAME="${AVD_NAME:-fepro}"
API="${API:-34}"
case "$(uname -m)" in
  arm64)  ABI="arm64-v8a" ;;
  x86_64) ABI="x86_64" ;;   # see emulator-setup.md: the app may not offer an x86_64 build
  *) echo "unknown arch"; exit 1 ;;
esac
IMG="system-images;android-${API};google_apis_playstore;${ABI}"

brew list --cask temurin >/dev/null 2>&1 || brew install --cask temurin
brew list --cask android-commandlinetools >/dev/null 2>&1 || brew install --cask android-commandlinetools

export ANDROID_HOME="${ANDROID_HOME:-$(brew --prefix)/share/android-commandlinetools}"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"

yes | sdkmanager --licenses >/dev/null || true
sdkmanager "platform-tools" "emulator" "platforms;android-${API}" "$IMG"

if ! avdmanager list avd | grep -q "Name: ${AVD_NAME}$"; then
  echo "no" | avdmanager create avd -n "$AVD_NAME" -k "$IMG" -d pixel_7
fi

cat <<MSG

Done. Add these to ~/.zshrc so adb and emulator are on PATH:
  export ANDROID_HOME="$ANDROID_HOME"
  export PATH="\$ANDROID_HOME/platform-tools:\$ANDROID_HOME/emulator:\$PATH"

Start the emulator:
  emulator -avd $AVD_NAME &

Then follow tools/emulator-setup.md from step 3.
MSG
