# The Moon: phase is right everywhere, orientation is only right in the sky views

Build: `com.OProjects.FLS` versionCode 250004. Sources: `Script/Utility.gd` (`process_SSOscop`),
`Script/Astronomy/SSOScop.gd`, `Script/SSOScopView.gd`, `Script/Astronomy/SSBody.gd` (recovered scripts)
and `Shader/SSObject.gdshader` (plain text). Confidence: high on what goes in. The on-screen handedness was settled by a capture; see below.

## How the Moon is drawn

One shader draws the Moon in every view. It ray-traces a lit sphere from seven numbers
(`CBODY_DAT`), filled by `process_SSOscop`:

| Number | Meaning |
|---|---|
| `SubObserverLat`, `SubObserverLon` | Which point of the Moon faces the Earth (libration) |
| `SubSolarLon`, `SubSolarLat` | Which point of the Moon has the Sun overhead. This sets the phase |
| `PA` | The angle the whole disc is turned on screen |
| distance, stroke offset | Size and line drawing |

The phase is therefore real three-body geometry: a sphere, lit from the direction of the Sun as seen
from the Moon, viewed from the direction of the Earth. It is the same in every view, and it is correct.

## Where the views differ: one line

    data2gpu[vData.PA] = wrapf(sso.position_angle - (sso.ParallacticAngle if EnableParallacticAngle else 0.0), 0.0, 360.0)

`ParallacticAngle` is how far the sky is turned for a particular observer. It comes from
`get_AzimAltiParallactic(..., lat, lon)`, so it depends on the user's latitude and longitude and on
the time. Each view calls the function differently:

| View | Call | Result |
|---|---|---|
| Sky view (3D) | `process_SSOscop(self_mat, SSO.id, true, ...)` | Turned for the observer. Correct for where you stand |
| Tracking view | `process_SSOscop(..., EnableParallacticAngle, ...)` | A user toggle. On: as you see it. Off: celestial north up |
| Flat map (2D) | `process_SSOscop(self_mat, SSO.id, false, ...)` | **No observer correction, hard-coded** |

On the map the icon is then rotated so that its "up" points at the map's north pole
(`SSOScop.update_2D`: `rotation = global_position.angle_to_point(North_dir) - PI / 2.0`).

So the Moon on the flat map is the view from the centre of the Earth with celestial north toward the
map centre. It is not what any particular observer sees, and it is the same picture for everyone.

## Two things the map Moon therefore cannot do

**1. It cannot show what different observers see.** Seen from London at transit the Moon stands with
celestial north up. Seen from Sydney at transit the same Moon is upside down, because the observer
is. The sky view reproduces this through the parallactic angle. The map has one Moon and one
orientation; there is no way to draw both on one flat picture.

**2. Its lit side does not face the map's Sun.** On the sky the lit side points along the great circle
to the Sun. The flat circular map does not preserve those directions, so the lit side of the map Moon
generally points away from the map's Sun marker. Figures from `tools/moon_limb.py` for one lunar
month (angles in degrees from north through east; "difference" is how far the lit side misses the
Sun marker):

| Date (00:00 UTC) | Moon-Sun angle | Lit fraction | Lit side on the sky (chi) | Sun marker from Moon marker on the map | Difference |
|---|---|---|---|---|---|
| 10 Nov 2026 | 9 | 0.01 | 316 | 301 | +15 |
| 12 Nov 2026 | 31 | 0.07 | 282 | 295 | -12 |
| 14 Nov 2026 | 52 | 0.19 | 267 | 302 | -35 |
| 16 Nov 2026 | 74 | 0.36 | 256 | 310 | -54 |
| 18 Nov 2026 | 96 | 0.55 | 249 | 318 | -69 |
| 20 Nov 2026 | 119 | 0.74 | 248 | 327 | -79 |
| 22 Nov 2026 | 144 | 0.90 | 254 | 338 | -84 |
| 24 Nov 2026 | 170 | 0.99 | 285 | 354 | -69 |
| 26 Nov 2026 | 160 | 0.97 | 75 | 13 | +62 |
| 28 Nov 2026 | 133 | 0.84 | 97 | 33 | +65 |
| 30 Nov 2026 | 106 | 0.64 | 109 | 48 | +61 |
| 02 Dec 2026 | 81 | 0.42 | 113 | 59 | +54 |
| 04 Dec 2026 | 57 | 0.23 | 110 | 67 | +43 |
| 06 Dec 2026 | 34 | 0.09 | 102 | 74 | +27 |
| 08 Dec 2026 | 12 | 0.01 | 78 | 77 | +1 |

Largest difference in this run: 84 degrees.

Near first and last quarter the miss is 50 to 80 degrees. If the Moon on the map were a ball lit by
the Sun on the map, its lit side would face that Sun. It does not, because the picture was computed
for a Sun 150 million km away and then pasted onto the map.

These numbers assume the map icon is drawn with east on the map's east side. If the app instead
draws the Moon as seen from below (east and west swapped, as on the sky), the lit side points to the
other side and the miss is larger. Which of the two it does is the open point for the capture.

## First capture: the prediction holds  (19 Nov 2026)

`evidence/captures/S7_a_map_iphone_20261121T2018Z.png`: map view from the iPhone app, app time
2026/11/21 20:18. Measured off the screenshot (pole position judged by eye, so allow a few degrees):

| Quantity | Predicted for 21 Nov 2026 20:18 UTC | Measured from the capture |
|---|---|---|
| Moon marker position | 12.4 N, 13.2 E | Over the Niger / Nigeria / Chad area |
| Sun marker, bearing from the Moon marker | 337 | 337 |
| Lit side of the Moon icon, bearing | 253 | 256 |
| Lit side misses the Sun marker by | 84 | 81 |
| Lit fraction | 0.89 | about 0.88 (pixel count, rough) |

Bearings are degrees from map-north (toward the pole) through map-east.

This settles the open point above: the icon is **not** mirrored. Its lit side sits at the celestial
position angle, with east on the map's east side. On screen the lit side faces the lower left while
the Sun marker is to the upper left, close to a right angle apart.

Caveats: this is the iPhone app, not the Android build whose code was read, and the app version was
not recorded. The clock is assumed to be UTC (the device was in London in November, where local time
is UTC). One instant only.

## The other side

- The phase on the map is not wrong as a phase. A flat-earth reply is that the map Moon is an icon
  showing "tonight's phase", not a model of the Moon.
- That reply concedes the point: the icon's phase comes from a calculation that needs a spherical
  Moon, a distant Sun, and the observer's latitude to orient it, none of which the map can supply.
- A literal local Moon a few thousand km above a flat Earth would also show different faces and
  different phases to observers thousands of km apart. Everyone on Earth sees the same face and
  nearly the same phase. That argument does not depend on this app and is not tested here.
