# Sky view / star trails: black-box test matrix

Hypothesis (Steve, from use of the app): the map view presents flat dynamics, but on "fly-in" to a
location the app switches wholesale to globe dynamics. Each test below has a different prediction under
A = globe ephemeris and C = literal reading of the app's own map (see PLAN.md phase 1).

Capture naming: `evidence/captures/<test-id>_<location>_<yyyymmddThhmmZ>_<map|sky>.png|mp4`.
Record app version and build with every capture.

## Locations

| Key | Place | Lat | Lon | Why |
|---|---|---|---|---|
| SYD | Sydney | -33.87 | 151.21 | Southern mid-latitude |
| CPT | Cape Town | -33.92 | 18.42 | Same latitude as SYD, ~133 deg of longitude away |
| SCL | Santiago | -33.45 | -70.67 | Third southern point, completes the triangle |
| USH | Ushuaia | -54.80 | -68.30 | High south, circumpolar southern stars |
| UIO | Quito | -0.18 | -78.47 | Equator |
| LON | London | 51.51 | -0.13 | Home control |
| TOS | Tromso | 69.65 | 18.96 | Arctic, midnight sun |

## Tests

| ID | Test | Globe prediction (A) | Literal-map prediction (C) | Capture |
|---|---|---|---|---|
| ST1 | Rotation sense, facing the pole. LON facing north vs SYD facing south, time-lapse | LON counter-clockwise about Polaris; SYD clockwise about the south celestial pole | One rotation centre (over the map's north pole). Facing south from SYD there is no second centre; stars sweep left-to-right in shallow arcs | Time-lapse both |
| ST2 | Pole altitude. Altitude of the rotation centre at each location | Equals latitude: ~34 deg above the southern horizon at SYD/CPT/SCL, ~55 deg at USH, on the horizon at UIO | Northern centre only, altitude from atan(h/d), never below the horizon and never in the south | Sky still with alt/az readout |
| ST3 | Same southern stars, three continents. SYD, CPT, SCL at a common instant when all three are dark (or nearest) | All three see Crux / sigma Octantis region due south | "Due south" from the three points on an AE map are three diverging directions, ~120 deg apart, so they cannot be looking at the same stars | Map + sky at each |
| ST4 | Equator. UIO facing east, north, south | Stars rise vertically in the east; counter-clockwise looking north, clockwise looking south, both poles on the horizon | Single centre to the north at moderate altitude | Time-lapse x3 |
| ST5 | Summer sunrise azimuth, SYD on 21 Dec | Sun rises ~29 deg south of east (az ~119 deg) | Sub-solar point is over the Tropic of Capricorn ring; bearing from SYD on the AE map at local sunrise points north of east | Map + sky at sunrise |
| ST6 | Setting. Any star or the Sun at the horizon | Altitude passes through 0 deg and goes negative; body is occluded by the horizon | atan(h/d) never reaches 0 for finite d; body shrinks toward but stays above the horizon | Sky sequence across set |
| ST7 | Angular size and separation. Sun diameter and a fixed star pair (e.g. the Pointers) at culmination vs near horizon | Constant | Shrinks with distance; separations change with viewing geometry | Zoomed stills |
| ST8 | Midnight sun, TOS in June and USH region / Antarctic latitude in December | 24 h sun in both, in their respective summers | Northern case is drawable; southern 24 h sun is not, for a sun circling the Tropic of Capricorn ring | Sky time-lapse |
| ST9 | Fly-in continuity. Screen-record the transition from map into the sky at SYD with a bright body in view | Nothing to predict; this is observational | If the sky were the map scene seen from inside, the body's screen direction would be continuous through the transition | Screen recording, frame-by-frame: does the body jump, cross-fade or cut? |
| ST10 | Moon orientation, LON vs SYD, same instant | Moon appears rotated ~180 deg minus latitude effects (inverted from the south) | Same face orientation for all observers looking up at one disc | Sky stills |

## Notes

- ST3, ST5 and ST9 are the three that most directly test the "switch" claim. ST9 is the only one that
  looks at the transition itself; pair it with function-map item 7 in static analysis.
- For C, body height is a free parameter. Run C for a range (say 3,000 to 6,000 km) so the result does
  not depend on a height we chose.
- If the app exposes alt/az numbers in the sky view, record the numbers; they beat pixel measurement.
