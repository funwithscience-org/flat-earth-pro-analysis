# adb-emulator MCP server

Lets an MCP-capable assistant (Gemini CLI, or any other MCP client) operate the Android emulator
through adb to capture the scenes in `analysis/capture-scenes.md`.

- One file, `server.py`, Python standard library only. Runs on the python3 that ships with macOS.
- Tools: `device_info`, `launch_app`, `screenshot`, `tap`, `long_press`, `swipe`, `type_text`, `key`,
  `wait`, `record_start`, `record_stop`.
- Narrow on purpose: no arbitrary shell, a fixed list of keys, restricted characters for typed text,
  and it only talks to a device whose serial starts with `emulator-`.
- Screenshots and recordings are saved to `evidence/captures/`.

Status: protocol tested against a fake adb (handshake, tool list, tool calls, error path).
**Not yet tested against the real emulator or a real Gemini client.**

## Set up (Gemini CLI)

Add this to `~/.gemini/settings.json` (merge with what is there). The config shape is from memory of
the Gemini CLI docs; check it against the current docs if the server does not show up.

```json
{
  "mcpServers": {
    "adb-emulator": {
      "command": "python3",
      "args": ["/Users/headknocker/Library/Mobile Documents/com~apple~CloudDocs/claude working folder/flat earth pro analysis/tools/adb_mcp/server.py"],
      "env": {
        "ADB_PATH": "/Users/headknocker/Library/Android/sdk/platform-tools/adb"
      }
    }
  }
}
```

`ADB_PATH` above assumes the Android Studio install. If adb lives elsewhere, run `which adb` and use
that. Start the emulator before starting Gemini, then check the server is listed (`/mcp` in Gemini CLI).

## Quick check without any assistant

```
cd "tools/adb_mcp"
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"device_info","arguments":{}}}' \
  | ADB_PATH="$HOME/Library/Android/sdk/platform-tools/adb" python3 server.py
```

The second line of output should name the emulator and its screen size.

## Known limits

- **No pinch.** `adb input` cannot do two-finger gestures. Use the app's on-screen zoom control.
- **The app is a game-engine canvas.** There are no Android buttons to query, so the assistant has to
  work from screenshots: look, tap, look again.
- **Screenshots returned to the assistant are scaled down** (longest side 1024 px) to keep them light.
  Coordinates are converted automatically. Saved copies are full resolution.
- **Recordings stop at 180 s** (an Android limit). Split longer time-lapses.
- Typed text is limited to letters, digits, space and `. , : + - _ / @`. Enter negative coordinates
  with the app's own S/W controls if it has them, or with `-`.

## Starter prompt for the assistant

> You are operating an Android emulator through the adb-emulator tools. The app under test is "Flat
> Earth" (com.OProjects.FLS). Read `analysis/capture-scenes.md` and capture scene S1 exactly as
> written: same coordinates, same UTC times, same shot names. Before every tap take a screenshot, and
> after every tap take another to confirm what changed. First spend a few steps learning the UI: find
> the location control, the time control, the sky button and the object info panel, and tell me where
> they are. Save every shot with the file name the scene specifies. If the app shows a value that
> differs from the "Expect" table, do not adjust anything to make it match: save the capture and
> report the difference. Do not change any app setting that is not needed for the scene.
