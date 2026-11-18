#!/usr/bin/env python3
"""Minimal MCP server (stdio) that lets an assistant operate ONE Android emulator through adb.

Standard library only; works on the system python3 that ships with macOS (3.9+).
Deliberately narrow: taps, swipes, text, a few keys, screenshots and screen recordings.
There is no arbitrary shell tool, and it refuses to talk to anything that is not an emulator.

Environment:
  ADB_PATH     path to adb (default: $PATH, then ~/Library/Android/sdk/platform-tools/adb)
  CAPTURE_DIR  where screenshots and recordings are saved (default: ../../evidence/captures)
  APP_PACKAGE  package launched by launch_app (default: com.OProjects.FLS)
  SHOT_MAX_PX  longest side of the screenshot returned to the model (default: 1024)
"""
import base64, json, os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
CAPTURE_DIR = os.environ.get("CAPTURE_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "evidence", "captures"))
APP_PACKAGE = os.environ.get("APP_PACKAGE", "com.OProjects.FLS")
SHOT_MAX_PX = int(os.environ.get("SHOT_MAX_PX", "1024"))
KEYS = {"BACK": 4, "HOME": 3, "ENTER": 66, "DEL": 67, "TAB": 61, "ESCAPE": 111,
        "DPAD_UP": 19, "DPAD_DOWN": 20, "DPAD_LEFT": 21, "DPAD_RIGHT": 22, "APP_SWITCH": 187}
STATE = {"scale": 1.0, "recording": None}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def adb_path():
    p = os.environ.get("ADB_PATH") or shutil.which("adb") or os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
    if not os.path.exists(p):
        raise RuntimeError("adb not found. Set ADB_PATH to the full path of adb.")
    return p


def serial():
    out = subprocess.run([adb_path(), "devices"], capture_output=True, text=True, timeout=15).stdout
    emus = [l.split()[0] for l in out.splitlines()[1:] if l.strip().endswith("device") and l.startswith("emulator-")]
    if not emus:
        raise RuntimeError("No running emulator found (adb devices shows none). Start the emulator first.")
    return emus[0]


def adb(*args, timeout=30, binary=False):
    r = subprocess.run([adb_path(), "-s", serial()] + list(args), capture_output=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError("adb %s failed: %s" % (" ".join(args[:3]), r.stderr.decode("utf8", "replace")[:300]))
    return r.stdout if binary else r.stdout.decode("utf8", "replace")


def safe_name(name, ext):
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", (name or "").strip()).strip("._") or time.strftime("cap_%Y%m%d_%H%M%S")
    if not name.lower().endswith("." + ext):
        name += "." + ext
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    return os.path.join(CAPTURE_DIR, name)


def png_size(b):
    return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")


def dev(v):
    """Convert a coordinate from the last returned screenshot's pixels to device pixels."""
    return str(int(round(float(v) / STATE["scale"])))


# ---- tools ----

def t_device_info(a):
    size = adb("shell", "wm", "size").strip()
    focus = adb("shell", "dumpsys", "window").split("mCurrentFocus")[-1].splitlines()[0][:160]
    return "emulator: %s\n%s\nfocus:%s\ncaptures saved to: %s" % (serial(), size, focus, CAPTURE_DIR)


def t_launch_app(a):
    adb("shell", "monkey", "-p", APP_PACKAGE, "-c", "android.intent.category.LAUNCHER", "1")
    return "launched %s" % APP_PACKAGE


def t_screenshot(a):
    png = adb("exec-out", "screencap", "-p", binary=True, timeout=30)
    w, h = png_size(png)
    saved = ""
    if a.get("save_as"):
        path = safe_name(a["save_as"], "png")
        with open(path, "wb") as f:
            f.write(png)
        saved = " Full-resolution copy saved: %s." % path
    small, scale = png, 1.0
    if max(w, h) > SHOT_MAX_PX and shutil.which("sips"):
        with tempfile.TemporaryDirectory() as d:
            src, dst = os.path.join(d, "a.png"), os.path.join(d, "b.png")
            with open(src, "wb") as f:
                f.write(png)
            subprocess.run(["sips", "-Z", str(SHOT_MAX_PX), src, "--out", dst], capture_output=True, timeout=30)
            if os.path.exists(dst):
                small = open(dst, "rb").read()
                scale = png_size(small)[0] / float(w)
    STATE["scale"] = scale
    sw, sh = png_size(small)
    text = ("Screenshot %dx%d (device is %dx%d). Give tap and swipe coordinates in THIS image's pixels; "
            "they are converted for you.%s" % (sw, sh, w, h, saved))
    return [{"type": "text", "text": text},
            {"type": "image", "data": base64.b64encode(small).decode("ascii"), "mimeType": "image/png"}]


def t_tap(a):
    adb("shell", "input", "tap", dev(a["x"]), dev(a["y"]))
    return "tapped"


def t_long_press(a):
    x, y = dev(a["x"]), dev(a["y"])
    adb("shell", "input", "swipe", x, y, x, y, str(int(a.get("ms", 800))))
    return "long-pressed"


def t_swipe(a):
    adb("shell", "input", "swipe", dev(a["x1"]), dev(a["y1"]), dev(a["x2"]), dev(a["y2"]), str(int(a.get("ms", 400))))
    return "swiped"


def t_type_text(a):
    s = str(a["text"])
    if not re.fullmatch(r"[A-Za-z0-9 .,:+\-_/@]*", s):
        raise RuntimeError("type_text only accepts letters, digits, space and . , : + - _ / @")
    adb("shell", "input", "text", s.replace(" ", "%s"))
    return "typed"


def t_key(a):
    k = str(a["key"]).upper()
    if k not in KEYS:
        raise RuntimeError("key must be one of: " + ", ".join(sorted(KEYS)))
    adb("shell", "input", "keyevent", str(KEYS[k]))
    return "pressed " + k


def t_wait(a):
    s = max(0.0, min(30.0, float(a.get("seconds", 1))))
    time.sleep(s)
    return "waited %.1fs" % s


def t_record_start(a):
    if STATE["recording"]:
        raise RuntimeError("A recording is already running. Call record_stop first.")
    secs = max(1, min(180, int(a.get("max_seconds", 60))))
    path = safe_name(a.get("save_as"), "mp4")
    remote = "/sdcard/_mcp_rec.mp4"
    p = subprocess.Popen([adb_path(), "-s", serial(), "shell", "screenrecord", "--time-limit", str(secs), remote],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    STATE["recording"] = {"proc": p, "path": path, "remote": remote}
    return "recording (up to %ds). Call record_stop to finish and save to %s" % (secs, path)


def t_record_stop(a):
    r = STATE["recording"]
    if not r:
        raise RuntimeError("No recording is running.")
    if r["proc"].poll() is None:
        subprocess.run([adb_path(), "-s", serial(), "shell", "pkill", "-2", "screenrecord"], capture_output=True, timeout=15)
        try:
            r["proc"].wait(timeout=15)
        except subprocess.TimeoutExpired:
            r["proc"].kill()
    time.sleep(1.5)  # let the device finalise the file
    adb("pull", r["remote"], r["path"], timeout=120)
    adb("shell", "rm", "-f", r["remote"])
    STATE["recording"] = None
    return "saved %s (%d bytes)" % (r["path"], os.path.getsize(r["path"]))


def num(desc):
    return {"type": "number", "description": desc}


XY = "in pixels of the most recent screenshot"
TOOLS = [
    ("device_info", "Emulator serial, screen size, focused window, and where captures are saved.", {}, [], t_device_info),
    ("launch_app", "Bring the Flat Earth app to the foreground (starts it if needed).", {}, [], t_launch_app),
    ("screenshot", "Take a screenshot and return it. Optionally also save a full-resolution PNG into the captures folder.",
     {"save_as": {"type": "string", "description": "Optional file name, e.g. S1_a_map. Omit to just look."}}, [], t_screenshot),
    ("tap", "Tap a point.", {"x": num("x " + XY), "y": num("y " + XY)}, ["x", "y"], t_tap),
    ("long_press", "Press and hold a point.", {"x": num("x " + XY), "y": num("y " + XY), "ms": num("hold time, default 800")}, ["x", "y"], t_long_press),
    ("swipe", "Drag from one point to another. Use for panning, scrolling wheel pickers and dragging the timeline.",
     {"x1": num("start x " + XY), "y1": num("start y " + XY), "x2": num("end x " + XY), "y2": num("end y " + XY), "ms": num("duration, default 400")},
     ["x1", "y1", "x2", "y2"], t_swipe),
    ("type_text", "Type into the focused text field (letters, digits, space and . , : + - _ / @).",
     {"text": {"type": "string"}}, ["text"], t_type_text),
    ("key", "Press a key: " + ", ".join(sorted(KEYS)) + ".", {"key": {"type": "string"}}, ["key"], t_key),
    ("wait", "Pause up to 30 seconds, e.g. while an animation or time-lapse runs.", {"seconds": num("seconds")}, [], t_wait),
    ("record_start", "Start a screen recording (max 180 s). Finish with record_stop.",
     {"save_as": {"type": "string", "description": "File name, e.g. S2_b_london_north"}, "max_seconds": num("1-180, default 60")}, [], t_record_start),
    ("record_stop", "Stop the running screen recording and save it as MP4 into the captures folder.", {}, [], t_record_stop),
]
BY_NAME = {t[0]: t for t in TOOLS}


def handle(msg):
    m, mid = msg.get("method"), msg.get("id")
    if m == "initialize":
        ver = (msg.get("params") or {}).get("protocolVersion") or "2024-11-05"
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": ver, "capabilities": {"tools": {}},
            "serverInfo": {"name": "adb-emulator", "version": "0.1.0"},
            "instructions": "Operates one Android emulator. Always take a screenshot before tapping, and again after, to confirm what happened."}}
    if m == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if m == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": [
            {"name": n, "description": d, "inputSchema": {"type": "object", "properties": p, "required": r}}
            for n, d, p, r, _ in TOOLS]}}
    if m == "tools/call":
        p = msg.get("params") or {}
        try:
            if p.get("name") not in BY_NAME:
                raise RuntimeError("unknown tool %r" % p.get("name"))
            out = BY_NAME[p["name"]][4](p.get("arguments") or {})
            content = out if isinstance(out, list) else [{"type": "text", "text": str(out)}]
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": content, "isError": False}}
        except Exception as e:  # tool errors go back to the model, not the transport
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": "ERROR: %s" % e}], "isError": True}}
    if mid is None:
        return None  # notification
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found: %s" % m}}


def main():
    log("adb-emulator MCP server started; captures ->", CAPTURE_DIR)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except Exception as e:
            log("bad message:", e)
            continue
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
