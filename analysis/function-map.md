# Function map

Feature list is taken from the App Store and Google Play listings. Nothing below is a finding yet;
the "look for" column is what would distinguish spherical astronomy from a flat construction.

| # | Function | What the app shows | Look for (static) | Black-box check |
|---|---|---|---|---|
| 1 | Ephemeris core | Sun, Moon and planet positions for any date/time | Julian date (2451545.0), obliquity (~23.4393 deg), GMST constants (280.46061837, 360.98564736629), nutation terms, VSOP87 / ELP / Meeus series, or a bundled library (SOFA, Swiss Ephemeris, etc.). Output type: RA/Dec or ecliptic lon/lat | Sub-solar point vs Skyfield at several instants |
| 2 | Map projection | AE map by default; Pro adds other projections | Forward projection from (lat, lon). Is lat/lon the native coordinate and AE just one of several skins over the same data? | Switch projection in Pro: do sub-points keep the same lat/lon? |
| 3 | Day/night terminator | Daylight coverage on the map | Per-pixel solar elevation via the spherical law of cosines (sin phi sin delta + cos phi cos delta cos H), or a great-circle at 90 deg from the sub-solar point. Twilight bands at -6/-12/-18 deg | Terminator shape at solstice vs a globe terminator re-projected to AE |
| 4 | Local sky position | Azimuth and altitude of each body for a location (navigation tab) | Equatorial-to-horizontal transform using observer latitude and local sidereal time. Any use of distance-on-the-map or a body height in km | Az/alt vs Skyfield; compare with bearing and atan(h/d) taken from the map |
| 5 | Rise / set / transit / twilight | Times for any location | Standard altitude -0.833 deg, hour-angle solution, refraction constant | Times vs almanac |
| 6 | Moon detail | Phase, libration, orientation / parallactic angle, perigee and apogee | Parallactic-angle formula (needs latitude and hour angle), optical libration terms, Earth-Moon distance in km | Moon orientation from northern vs southern locations (inverts on a globe) |
| 7 | **Sky view, star trails, fly-in** | Sky dome for a location; stars and constellations; transition from map into the dome | Star catalogue in RA/Dec. Sky sphere rotated about an axis whose elevation equals observer latitude. What the sky scene takes from the map scene at hand-off: only (time, lat, lon), or actual 3D positions? Separate camera / scene graph? Is there a horizon plane that occludes (stars set)? | See `star-trails/test-matrix.md` |
| 8 | Eclipses | Eclipse events / schedule | Besselian elements, or shadow-cone geometry with Earth radius | Eclipse path vs published path |
| 9 | Compass and directions | Local compass, direction to bodies | Great-circle initial bearing vs straight-line bearing on the AE map (they differ away from the pole) | Direction to a far southern-hemisphere target |
| 10 | Time zones, weather, notifications | Utility features | Low priority. Weather is a network call: note the provider, do not probe it | - |

## Per-function write-up template (`analysis/static/NN-name.md`)

- **App version / package / SHA-256:**
- **What it does:**
- **Inputs:** (which of: time, observer lat/lon, map-scene positions, constants)
- **Coordinate system it computes in:**
- **Evidence:** (constant, formula, call path; short excerpt only)
- **Reading:** spherical / flat / agnostic / unclear
- **Confidence:** high / medium / low, and why
- **Counter-reading:** the most charitable alternative explanation
