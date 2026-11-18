# How the star field gets its direction of rotation

Build: `com.OProjects.FLS` versionCode 250004 (free Android, 18 Nov 2026).
Sources read: all 102 scripts, recovered to source with `tools/gdc_decomp.py`, and the star and sky
shaders, which ship as plain text. Confidence: high. Caveat on the method is at the end.

## Short answer

Nowhere in the app is a direction of rotation set. There is no "clockwise", no "counter-clockwise",
and no branch on hemisphere or on the sign of latitude (searched: none in scripts or shaders).
The two views get their rotation from two different pieces of geometry fed by the same clock:

| | Map view | Sky view |
|---|---|---|
| Star catalogue | HYG v4.0, RA and Dec | the same |
| Clock | Greenwich sidereal time | the same, plus observer longitude to make local sidereal time |
| Extra input | none | **observer latitude** |
| Where a star is drawn | over the point on Earth where it is overhead | at the altitude and azimuth an observer at that latitude sees it |
| Rotation that results | one rigid turn about the map centre, one sense | about the celestial pole that is above the observer's horizon; sense depends on which pole that is |

## Map view

`Shader/StarMesh2D.gdshader`, vertex stage. For each star:

1. longitude = RA shifted by Greenwich sidereal time (`ra + GST - 12`, then hours to a 0-1 longitude),
   latitude = Dec. That is the star's sub-stellar point.
2. That longitude/latitude goes through `fe_mesh_project`, the same projection function used for the
   land.

`GST` is a global shader value set once per tick from `Astronify.GreenwitchSiderealtime(JD_TT, true)`
(`Script/TimeEngine.gd`). As it advances, every star's longitude changes by the same amount. On the
azimuthal-equidistant projection that is a rigid rotation of the whole field about the north pole at
the map centre, westward, which is clockwise as the map is drawn. Southern stars ride round the outer
part of the disc; a star at Dec -89 traces the rim.

So on the map there is one centre and one sense, and it comes from nothing more than
"longitude = RA - sidereal time".

## Sky view

`Shader/StarMesh3D.gdshader`, vertex stage. For each star:

    HA     = LST - RA
    sinAlt = sinLat*sinDec + cosLat*cosDec*cosHA
    az     = atan(-cosDec*sinHA, (sinDec - sinLat*sinAlt)/cosLat)

The star is then placed on a sphere centred on the camera at that altitude and azimuth (plus a
refraction correction). `LST` is set in `TimeEngine.gd` as
`LocalSiderealTime(GST, User.Location.LONGITUDE)`; latitude arrives in the global `LatLonPresTemp`.

Time enters only through `HA`. As `HA` grows, each star moves round a circle centred on the celestial
axis. Latitude sets how that axis is tilted against the observer's horizon:

- latitude > 0: the north celestial pole is `lat` degrees above the northern horizon. Facing it, the
  field turns counter-clockwise.
- latitude < 0: `sinLat` changes sign, the north pole drops below the horizon and the south celestial
  pole stands `|lat|` degrees above the southern horizon. Facing it, the same motion is seen from the
  other end of the axis, so it turns clockwise.
- latitude = 0: both poles on the horizon, stars rise straight up in the east.

The background Milky Way does the same thing in reverse (`Shader/sky.gdshader`,
`eyedir_to_equatorial`): for each view direction it rotates by latitude about the east-west axis, then
by `-LST` about the polar axis, to find which part of the sky texture to show. Same two inputs.

The counter-rotation in the south is therefore not programmed in. It is what the spherical formula
produces when the latitude is negative.

## Why this is the interesting part

The sky view needs one thing the map view does not use: latitude as the **tilt of the rotation axis
relative to the observer's local "up"**. That is a statement about the observer's vertical pointing in
a different direction at each latitude. On a plane every observer's vertical is parallel, so latitude
could change how far away the rotation centre is, but not tilt the axis, and could never bring a
second centre into view. The app's own two views show the two cases side by side.

## The map-to-sky hand-off (settles the earlier "names only" item)

`Script/bottom_bar.gd`, sky button handler, with `Script/Utility.gd`:

1. Project the user's latitude/longitude to a map position.
2. Start a 2D camera tween that zooms the map toward that position.
3. Meanwhile load the separate 3D `SkyView` scene on a background thread.
4. When the zoom tween finishes, hide `MapView` and enable the sky UI. `SkyView` becomes visible when
   `MapView` goes invisible.

The "fly-in" is a zoom on the 2D map followed by a swap to a different scene with its own camera.
Nothing is carried across except the clock and the user's latitude and longitude. The 3D scene's
"travel mode" (`MainCam3D.gd`) is a separate feature for zooming toward a body in the sky.

## Other details confirmed in this pass

- Star positions are corrected to apparent place (proper motion and related terms) by the native
  `get_star_apparent_position`, refreshed every 30 days of app time.
- Sun, Moon and planets in the sky view use topocentric RA/Dec then `Equatorial2AltAz` with the user's
  latitude and longitude, i.e. the same transform as the stars, with parallax applied first.

## Method caveat

GDRE Tools, the standard Godot decompiler, could not be run in this session, so the scripts were
recovered with a small decoder written for the purpose (`tools/gdc_decomp.py`: zstd, identifier and
constant tables, token stream, line/column maps). The token table for bytecode v101 was reconstructed
from memory of the Godot source. The output reads as coherent GDScript throughout and its names,
constants and structure agree with the shaders, but it has not been diffed against GDRE output.
Spacing is approximate. Before quoting any script line publicly, re-derive it with GDRE Tools.
The shader findings do not depend on this: shaders are plain text in the package.
