#!/usr/bin/env bash
# Identify the engine/toolchain of an APK without decompiling anything.
# Usage: tools/triage.sh vendor/com.OProjects.FLS/base.apk [split_config.arm64_v8a.apk ...]
set -euo pipefail
for apk in "$@"; do
  echo "== $apk"
  unzip -l "$apk" | awk 'NR>3 {print $4}' > /tmp/triage_list.$$
  echo "-- native libs";      grep -E '^lib/.*\.so$' /tmp/triage_list.$$ || echo "(none)"
  echo "-- managed assemblies"; grep -E '\.dll$' /tmp/triage_list.$$ | head -40 || echo "(none)"
  echo "-- engine markers"
  grep -qE 'libil2cpp\.so'            /tmp/triage_list.$$ && echo "Unity IL2CPP (libil2cpp.so)"
  grep -qE 'global-metadata\.dat'     /tmp/triage_list.$$ && echo "Unity IL2CPP metadata present"
  grep -qE 'Assembly-CSharp\.dll'     /tmp/triage_list.$$ && echo "Unity Mono (Assembly-CSharp.dll)"
  grep -qE 'libunity\.so'             /tmp/triage_list.$$ && echo "Unity runtime (libunity.so)"
  grep -qE 'libflutter\.so|libapp\.so' /tmp/triage_list.$$ && echo "Flutter"
  grep -qE 'libUE4\.so|libUnreal\.so' /tmp/triage_list.$$ && echo "Unreal"
  grep -qE 'libgodot'                 /tmp/triage_list.$$ && echo "Godot"
  grep -qE 'index\.android\.bundle'   /tmp/triage_list.$$ && echo "React Native"
  echo "-- dex";  grep -E '^classes[0-9]*\.dex$' /tmp/triage_list.$$ || echo "(none)"
  echo "-- 15 largest entries"
  unzip -l "$apk" | awk 'NR>3 && $4!="" {print $1, $4}' | sort -rn | head -15
  rm -f /tmp/triage_list.$$
done
