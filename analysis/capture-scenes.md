# Capture scenes

Shot list for screen recordings of the Flat Earth app (free Android build, versionCode 250004) running
in the emulator. Each scene is self-contained: what it shows, how to set it up, what to record, the
numbers to expect, and the line it supports.

Expected numbers come from `tools/refcalc.py` ("globe" = standard spherical astronomy; "map" = the
app's own flat map taken literally, Sun 3,000-6,000 km above its marker). They are predictions.
**If the app shows something different, record what it shows. That is a finding, not a mistake.**

## Before recording

- Use the app's own time control so the app time is visible in frame. Times below are UTC. Check how
  the app labels its clock (UTC, device time, or the location's zone) and note it in the first clip.
- Set locations by manual coordinates where given, so latitude is exact.
- "Map view" = the default top-down map. "Sky view" = what the sky button on the bottom bar opens
  (the listing calls it Telescope Mode).
- Whenever an info panel shows altitude, azimuth, RA/Dec, distance or angular diameter, get it in
  frame. A number on screen beats any measurement off pixels.
- Screenshot: `adb exec-out screencap -p > evidence/captures/<name>.png`
- Recording (3 min max per file): `adb shell screenrecord /sdcard/cap.mp4`, Ctrl-C, then
  `adb pull /sdcard/cap.mp4 evidence/captures/<name>.mp4`. The emulator's own record button also works.
- File names: `<scene>_<shot>_<place>.mp4|png`, e.g. `S1_b_sky_A.png`.

---

## S1. Two observers, one hour apart: the marker is an address, not a position

**Point.** The Sun icon on the map marks the spot on the ground where the Sun is overhead (the
sub-solar point: the place where it is solar noon, at the latitude of the Sun's declination). It is not
the Sun's position in space. The sky view is correct for each observer, and it cannot be obtained from
the map.

**Setup.** Date/time **20 Dec 2026, 21:00 UTC** (about 08:00 on 21 Dec in eastern Australia).
- Observer A: **35.0 S, 150.0 E**
- Observer B: **35.0 S, 135.0 E** (same latitude, 15 degrees = one hour of sidereal turn west)

**Shots.**
| Shot | What |
|---|---|
| a | Map view, both A and B visible with the Sun marker. Hold 5 s. Then zoom so A, B and the marker fill the frame |
| b | Sky view from A, facing the Sun. Sun's alt/az readout in frame |
| c | Sky view from B, same instant, facing the Sun. Readout in frame |
| d | Back at A, step time back one hour to 20:00 UTC. Sky view. Readout in frame |

**Expect.**
| | Sky view (globe) | Map taken literally |
|---|---|---|
| A at 21:00 | alt 25.4, az 101.8 (12 deg south of east) | az 49 (north-east), elev 11-21 |
| B at 21:00 | alt 13.6, az 109.3 (19 deg south of east) | az 43 (north-east), elev 9-18 |
| A at 20:00 | alt 13.6, az 109.3, identical to B at 21:00 | |

Sun marker on the map: 23.4 S, 135.6 W. Map distance from A 16,070 km, from B 18,680 km.

**Lines it supports.**
- From both places the app's sky puts the Sun south of east. On the app's map the marker lies to the
  north-east of both. The two views disagree about which way to look by about 55-65 degrees.
- Shot d against shot c: moving 15 degrees west gives exactly the sky you had an hour earlier. Position
  in longitude is interchangeable with time. That is a turning sphere, not a lamp at a fixed spot.
- On the map, B is 2,600 km farther from the marker than A, which would lower the Sun by about 2
  degrees. The sky view lowers it by 12.

---

## S2. Star trails: London vs Sydney

**Point.** Same stars, same clock, opposite rotation, and a second centre that the map does not have.

**Setup.** Date 21 Dec 2026.
- London (51.51 N, 0.13 W), start **00:00 UTC**
- Sydney (33.87 S, 151.21 E), start **14:00 UTC** (01:00 local)

**Shots.**
| Shot | What |
|---|---|
| a | Map view with stars overlay on. Run time forward quickly for 10 s. The field turns as one disc about the centre |
| b | London, sky view, face north, find Polaris. Run time forward 3-4 hours of app time |
| c | Sydney, sky view, face south, find the Southern Cross / Sigma Octantis. Same time-lapse |
| d | Sydney, sky view, face north, tilt to the horizon. Show there is no Polaris and no northern centre |
| e | Optional: turn on the alt/az grid or constellation lines for b and c so the centre is obvious |

**Expect.**
| | Centre of rotation | Sense when facing it |
|---|---|---|
| London | Polaris, due north, alt 52 | counter-clockwise |
| Sydney | near Sigma Octantis, due south, alt 33-34 | clockwise |
| Sydney facing north | Polaris would be 33 degrees below the horizon | |
| Map taken literally, from Sydney | single centre due north, 12-24 degrees up | one sense for everyone |

**Lines it supports.**
- The app gets the southern sky right. It does it with the observer's latitude as a tilt of the sky's
  axis, which the code shows is the only extra input the sky view takes
  (`analysis/static/01-star-field-rotation.md`).
- Shot a against shot c: on the map every star circles the north pole. In Sydney's sky the Southern
  Cross circles a point in the south that is not on the map at all.

---

## S3. The equator: both poles on the horizon  (supplement)

**Setup.** Quito (0.18 S, 78.47 W), 21 Mar 2027, start 04:00 UTC (23:00 local).

**Shots.** Sky view time-lapse facing (a) north, (b) south, (c) east.

**Expect.** Polaris on the northern horizon, Sigma Octantis on the southern horizon (both within about
1 degree of it). Counter-clockwise facing north, clockwise facing south, stars rising straight up in
the east.

**Line.** One observer, two rotation centres, opposite senses, both in one night. Cleanest single clip
for "this is a sphere of stars seen from a sphere".

---

## S4. The Sun's distance, size and setting  (supplement; depends on the info panel)

**Setup.** Sydney, 21 Dec 2026. Open the Sun's info panel.

**Shots.**
| Shot | What |
|---|---|
| a | Info panel at local noon (about 02:00 UTC): distance and angular diameter in frame |
| b | Same panel near sunset (about 08:45 UTC) |
| c | Sky view, facing west-south-west, time-lapse through sunset (09:05 UTC, az 241) |

**Expect.** Angular diameter the same at noon and near sunset (about 0.54 degrees). The Sun crosses the
horizon and goes below it. Note exactly what the panel shows for distance.

**Line.** On the app's own map, the Sun would shrink to about a quarter of its noon size by sunset and
never drop below about 6 degrees. The app shows neither.

---

## S5. The fly-in itself  (supplement)

**Setup.** Sydney, any daytime instant with the Sun marker in frame on the map.

**Shot.** Screen-record pressing the sky button, from map to settled sky view. Then step through it
frame by frame.

**Expect (from the code).** The 2D map zooms toward the location, then the map is hidden and a
separate 3D scene appears. Nothing visibly travels from one into the other.

**Line.** The transition is a zoom and a cut. Record whether the Sun's on-screen direction is
continuous across it or jumps.

---

## S6. Daylight on the map at the December solstice  (supplement)

**Setup.** Map view, daylight shading on. **20 Dec 2026, 12:53 UTC.**

**Shots.**
| Shot | What |
|---|---|
| a | Whole map. Hold 5 s. Then slow time-lapse over 24 h |
| b | Sky view at McMurdo (77.85 S, 166.67 E), same instant: Sun up at local midnight |
| c | Sky view at Tokyo (35.68 N, 139.69 E), same instant: night |

**Expect.** McMurdo: Sun 11 degrees up, due south. Tokyo: Sun 64 degrees below the horizon. On the map
the lit area is a ring round the outer edge, not a pool of light under the marker. McMurdo is 31,300 km
from the marker on the map and in daylight; Tokyo is 18,200 km from it and in darkness.

**Line.** No "the Sun only reaches so far" explanation survives this: the nearer place is dark and the
farther place is lit.

---

## S7. The Moon: same phase, three orientations  (supplement)

**Point.** The phase is the same in every view and is correct. The orientation is corrected for the
observer in the sky view and the tracking view, and not at all on the map. On the map the lit side
does not face the map's Sun.

**Setup.** **18 Nov 2026, 00:00 UTC** (just after first quarter, Moon 55% lit).

**Shots.**
| Shot | What |
|---|---|
| a | Map view, zoomed so the Moon icon and the Sun marker are both in frame. Then zoom in on the Moon icon until the lit side is clear |
| b | Tracking view of the Moon from London, with the parallactic-angle option on, then off |
| c | Tracking view of the Moon from Sydney, same instant, option on, then off |
| d | Sky view from each place if the Moon is above the horizon there; otherwise step time until it is, and note the time |

**Expect.**
- Same lit fraction in every shot.
- With the option on, London and Sydney show the Moon turned differently (roughly upside down
  relative to each other when each sees it near its highest). With it off, both show the same picture.
- On the map: the lit side points about 249 degrees from map-north (west, a little south). The Sun
  marker lies about 318 degrees from map-north (north-west). They miss by about 69 degrees.
- **Record which side of the map icon is lit** (toward or away from the Sun marker's side). The code
  does not settle whether the icon is drawn mirrored; see `static/02-moon-phase-orientation.md`.

**Line.** One Moon, one phase, but you need to know where the observer stands to draw it the right way
up. The map cannot know that, so its Moon is the view from the centre of the Earth, and its lit side
does not even face the map's own Sun.

---

## Not in this list

- Switching projections (AE to orthographic and back) would show the map is a re-skinnable view of the
  same longitude/latitude data, but the listing says extra projections are Pro-only. Add as S7 if the
  Pro build is bought.

## Order of value if time is short

S1, S2, S3, S5. S4, S6 and S7 are strong but each takes longer to set up.
