# Static analysis, first pass

- **Build:** `com.OProjects.FLS` (free Android), versionCode 250004, pulled from Google Play 18 Nov 2026.
  SHA-256 of `base.apk`: `3e1b6d93...b07535e` (full hashes in `vendor/com.OProjects.FLS/MANIFEST.txt`).
- **Not yet examined:** Android Pro (`com.OProjects.FLSPro`), the iOS build.
- **Depth:** shaders read in full (they ship as plain text). Scripts read at the level of identifier and
  constant tables only, not control flow. Native library read at the level of embedded names only.
  Anything marked *names only* needs a proper decompile before it is quoted as fact.

## How the app is built

| Layer | What it is | How readable |
|---|---|---|
| Engine | Godot 4 (`libgodot_android.so`) | n/a |
| App logic | 102 compiled GDScript files (`.gdc`, bytecode v101, zstd-compressed) | Names and constants recover trivially; full source needs a GDScript decompiler |
| Rendering | 34 shaders + 5 includes (`.gdshader`) | Plain text, with the developer's comments |
| Astronomy | Native extension `libFELIBS`, class `Astronify` | Stripped binary; exported names visible |
| Data | HYG star catalogue v4.0 (83,500 rows: RA, Dec, distance, proper motion), equirectangular Earth textures, constellation lines | Plain files |

Nothing is obfuscated. The code is not hidden from anyone who unzips the package.

## Findings by function (numbers refer to `../function-map.md`)

### 7. Sky view: stars are placed by the standard equatorial-to-horizontal transform  (confidence: high)

`Shader/StarMesh3D.gdshader` computes every star's position in the vertex shader. Its inputs are the
star's RA and Dec, the observer's latitude, and local sidereal time. The core line is the spherical
law of cosines:

    sinAlt = sinLat * sinDec + cosLat * cosDec * cosHA      (HA = LST - RA)

The star is then drawn on a sphere centred on the camera at that altitude and azimuth, with an
atmospheric-refraction correction for pressure and temperature. No quantity from the map scene enters:
no map position, no height above a plane, no distance across the map. Latitude and longitude arrive as
a global shader parameter (`LatLonPresTemp`).

This is the mechanism behind every prediction in column A of `../star-trails/predictions.md`: pole
altitude equal to latitude, a second rotation centre in the south, opposite rotation sense, stars
setting below the horizon.

### 3. Day/night on the map: per-pixel solar altitude on a sphere  (confidence: high)

`Shader/include/sun.gdshaderinc` has a function `GetAlt(LonLat)` taking the Sun's Greenwich hour angle
and declination. For each pixel of the map it computes the same law-of-cosines altitude, in longitude
and latitude, and the fragment shader shades day, twilight and night from that altitude. The lit region
on the AE map is a spherical terminator re-projected, not a pool of light from a nearby Sun.

### 2. Map projection: AE is one setting of a general re-projection of a sphere  (confidence: high)

- The Earth texture is equirectangular (longitude/latitude). `commons.gdshaderinc` maps UV to
  longitude/latitude and to a unit sphere (`uvToSphere`, `rotY`, `rotZ`) to rotate the graticule.
- Projections are a parametrised conic family blended between equidistant and equal-area.
  `Script/data/ProjData` lists: Azimuthal Equidistant, Equirectangular, two "Extrapolated Equidistant"
  variants, Azimuthal Equal-Area, Orthographic, Cassini.
- `Script/MapProjection` carries `sphere_view_pos`, `uv_to_sphere`, `sphere_to_uv` (*names only*).

The flat map is a view of spherical coordinates. Orthographic, i.e. a globe seen from outside, is in
the same list.

### 8. Eclipses: the map shader contains the Earth's radius and flattening  (confidence: high)

`Shader/Projection.gdshader`, for eclipse coverage on the map, converts geocentric to topocentric
positions of the Sun and Moon per pixel. Its constants:

    EARTH_RADIUS_KM = 6378.14      FLATTENING = 0.99664719      AU2KM = 1.496e+8

6378.14 km is the Earth's equatorial radius; 0.99664719 is the polar-to-equatorial axis ratio of the
reference ellipsoid. The eclipse shading therefore depends on an oblate spheroid of that size, with the
Sun about 150 million km away. `Script/Eclipse` also references `compute_lunar_eclipse_shadow`,
umbral and penumbral radii (*names only*): the lunar eclipse is the Earth's shadow.

### 1. Ephemeris core: heliocentric and geocentric, in native code  (confidence: medium)

`libFELIBS` exposes names including `TrueHeliocentricRectangularEcliptical`,
`TrueHeliocentricEclipticalLongitude`, `ApparentGeocentricRA`, `Equatorial2Topocentric`,
`GreenwitchSiderealTime` [sic], `RefractionFromTrue`, `TopocentricMoonSemidiameter`,
`SatelliteRectangularToEquatorial`, `get_planetary_ephemeris_interpolated`. These match the naming
style of the AA+ library (an implementation of Meeus, *Astronomical Algorithms*). That attribution is a
guess from names; it has not been confirmed. `Script/Astronomy` defines `AU2KM = 149597870.691`.
Medium, not high, because names show what is computed, not how; the series used are unverified.

### 4, 5, 6. Local alt/az, rise/set, Moon detail  (confidence: medium, *names only*)

Scripts call `Equatorial2AltAz` with `GST` and the user's latitude and longitude, `get_topocentric_RaDecl`
with observer height, `get_AzimAltiParallactic`, and read `SubSolarLon/Lat`, `SubObserverLon/Lat`,
`PhaseAngle`, `BrightLimbPositionAngle`. All are standard spherical-astronomy quantities.

### 7 (transition). Map and sky are two separate scenes  (confidence: medium, *names only*)

`Script/Main` loads `scene/MapView.tscn` (2D) and `scene/SkyView.tscn` (3D) as separate scenes.
`MapView` has `on_enabled`, `on_disabled`, `fade_in`, `fade_out` and tweens `modulate:a` (opacity).
The two views have separate cameras (`MainCam2D`, `MainCam3D`). That is consistent with a cross-fade
between two independent scenes that share only clock and observer location, and not with a camera
flying into the map. Confirming it needs the control flow, and test ST9 (frame-by-frame recording).

`MainCam3D` also has a "travel mode" (`travel_fov_threshold`, `_enteris_travel_mode` [sic]). From the
names this looks like zooming in to a body in the sky view, not the map fly-in. Unverified.

## What this does and does not establish

Established for this build: the sky view, the map's day/night shading, the eclipse shading and the map
projection are all computed from spherical coordinates, and two of them from explicit globe dimensions.
The observation that the app "switches to globe dynamics" on entering the sky view is confirmed at the
code level, with one correction: it does not switch. The map view is globe-derived too; it only looks
flat because of the projection chosen.

Not established:
- Anything about the Pro build or older versions, which may be a different codebase.
- Intent. The developer left comments in the shaders, ships a globe (orthographic) projection, and the
  listing says the views share one astronomical model. None of that reads as concealment.
- That globe formulas prove the Earth's shape. They show the app has no flat model inside it. The
  flat-earth reply ("the formulas are just fits to observation") is answered by the predictions file,
  not by this one.

## Next

1. Full decompile of the scripts (GDRE Tools or equivalent) to turn the *names only* items into
   confirmed ones, especially the map/sky hand-off.
2. Black-box captures per the test matrix, so the published claims rest on behaviour.
3. Pull and fingerprint the Pro build.
