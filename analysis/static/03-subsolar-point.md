# Where the Sun marker on the map comes from

Build: `com.OProjects.FLS` versionCode 250004. Question: is the sub-solar point calculated, or read from
embedded data? Answer: calculated, every tick, from the Earth's orbit round the Sun.

## The chain

| Step | What happens | Where |
|---|---|---|
| 1 | The native engine computes the body's position for the current Julian date | `Astronomy.gd` lines 180-182: `astro.get_planetary_ephemeris(cbody, TimeEngine.JD, res, lat, lon)` (or the `_interpolated` variant) |
| 2 | Result includes the Sun's apparent geocentric right ascension and declination | `SSBody.gd`: `ApparentGeocentricRA`, `ApparentGeocentricDeclination` |
| 3 | Greenwich sidereal time from the clock | `TimeEngine.gd` line 334: `GST = Astronify.GreenwitchSiderealtime(JD_TT, true)` |
| 4 | Sub-point: latitude = declination, longitude = right ascension minus sidereal time | `SSBody.gd` line 128: `GeographicPos = Astronify.Equatorial2Geographic(TimeEngine.GST, ApparentGeocentricRA, ApparentGeocentricDeclination)` |
| 5 | For the day/night shading, the same two numbers as hour angle and declination | `MapView.gd` lines 72-73: `GHA = (TimeEngine.GST - Astronomy.Sun.ApparentGeocentricRA) * 15.0` |

Scripts are recovered source; see the method caveat in `01-star-field-rotation.md`.

## What the native engine holds

The engine (`libFELIBS`) is compiled, so its logic was not read. Its constant tables were found by
searching the binary for known values. Each of these appears exactly once, as a 64-bit float:

At offset 0x1095b8, read as triples (amplitude, phase, frequency):

    175347046, 0, 0
    3341656, 4.6692568, 6283.07585
    34894, 4.6261, 12566.1517
    3497, 2.7441, 5753.3849

These are the first terms of the VSOP87 series for the **Earth's heliocentric longitude**, in the
truncated form tabulated in Meeus, *Astronomical Algorithms*, Appendix III. 6283.07585 radians per
thousand years is the Earth's mean motion round the Sun.

At offset 0x10a278, the Earth's **distance from the Sun**, same source:

    100013989, 0, 0
    1670700, 3.0984635, 6283.07585
    13956, 3.05525, 12566.1517

At offset 0x1045d0, the main periodic terms of the Moon's longitude and distance (Meeus Table 47.A),
interleaved: 6288774, -20905355, 1274027, -3699111, 658314, -2955968, ...

Also present: 2451545.0 (J2000), 125.04452 (nutation argument), 20.49552 (constant of aberration, in
arcseconds), 149597870.691 (km per astronomical unit), 6378.14 and 0.99664719 (Earth radius and
flattening).

Not present anywhere in the package: a table of Sun positions by date, an ephemeris file, or a network
request for positions. The only network feature is weather.

## Coefficients checked against published tables  (19 Nov 2026)

Checked by a separate agent that opened the sources; it did not open the Meeus book itself.

| Item | Verdict | Checked against |
|---|---|---|
| Earth L0, first four terms | Match, 4 of 4 | IMCCE `VSOP87D.ear` (primary; values round to ours) and AA+ `g_L0EarthCoefficients` (identical) |
| Earth R0, first four terms | Match, 4 of 4 | Same two sources |
| Moon longitude / distance terms, first six pairs | Match, 6 of 6 | soniakeys/meeus `moonposition.go`, Meeus Table 47.A |
| 20.49552, 125.04452, 149597870.691, 6378.14, 0.99664719 | Confirmed | AA+, soniakeys/meeus, IERS Conventions 2003 Table 3.2 (the km/au value is DE405's) |

Second check, same day: the IMCCE file was downloaded directly and compared by script. Both headers read
"EARTH ... HELIOCENTRIC DYNAMICAL ECLIPTIC AND EQUINOX OF THE DATE", and the four largest terms of the
L and R series, rounded to units of 1e-8, equal the app's stored values.

Two details from the check. The fourth term in our table (3497) is fifth in the raw IMCCE file; having
it fourth is the amplitude-sorted order of the Meeus truncation, so the engine carries that truncation
and not the full file. And 6283.07585 is the Earth's sidereal mean motion in radians per Julian
millennium. The check also confirmed the method (Meeus ch. 25): Sun's longitude = Earth's heliocentric
longitude + 180 degrees, latitude = minus the Earth's, then an FK5 correction, nutation and aberration.

Sources opened by the checking agent:
- https://ftp.imcce.fr/pub/ephem/planets/vsop87/VSOP87D.ear
- https://raw.githubusercontent.com/onekiloparsec/SwiftAA/master/Sources/aaplus-v2.63/AAEarth.cpp (and AASun.cpp, AAGlobe.cpp, AAAberration.cpp, AANutation.cpp)
- https://raw.githubusercontent.com/soniakeys/meeus/master/v3/moonposition/moonposition.go (and solar.go, nutation.go, globe.go)
- https://raw.githubusercontent.com/architest/pymeeus/master/pymeeus/Earth.py
- https://iers-conventions.obspm.fr/archive/2003/chapter3/tn32_c3.pdf

## The code path, traced  (19 Nov 2026)

The engine was disassembled (`objdump`, arm64) and indexed: 4,983 functions, 34,519 calls. The tables
are reached through pointer slots, so the series functions were found by which slot they read.
Addresses are virtual addresses in `libFELIBS.android.template_release.arm64.so`, SHA-256 in
`vendor/com.OProjects.FLS/MANIFEST.txt` (the arm64 split).

| Address | What it is | How identified |
|---|---|---|
| `0x20bcb8` | Earth's heliocentric longitude | The only function reading the slots for tables L0 and L1 (`0x1095b8`, `0x109bb8`) |
| `0x20c90c` | Earth's heliocentric latitude | Reads the B0 table slot |
| `0x20caf4` | Earth's distance from the Sun | Reads the R0 table slot |
| `0x21ad04` | **The Sun's longitude** | 20 instructions, shown below |
| `0x16ea6c` | The ephemeris call that fills the result | References the key strings `ApparentGeocentricRA`, `TrueHeliocentricEclipticalLongitude`, `SubSolarLon` and calls the dictionary filler at `0x16d2ac` |

The whole of `0x21ad04`, with our labels:

    bl     0x20bcb8          ; Earth's heliocentric longitude
    mov/movk/fmov  d1 <- 0x4066800000000000   ; 180.0
    mov/movk/fmov  d8 <- 0x4076800000000000   ; 360.0
    fadd   d0, d0, d1        ; + 180
    fmov   d1, d8
    bl     fmod              ; wrap into 0..360
    fadd   d1, d0, d8
    fcmp   d0, #0.0
    fcsel  d0, d1, d0, mi    ; add 360 if negative
    ret

That is "Sun's longitude = Earth's longitude + 180 degrees", the standard step for turning the Earth's
position on its orbit into the Sun's direction as seen from the Earth. A sibling at `0x21bdd0` does
the same and also negates the Earth's latitude (`fneg` after the call to `0x20c90c`).

Call path from the ephemeris function to the tables:

    0x16ea6c -> 0x180c20 -> 0x223c94 -> 0x1f6774 -> 0x21ad04 -> 0x20bcb8 -> Earth L0..L5 tables

and directly `0x16ea6c -> 0x21f3f8 -> 0x20bcb8 / 0x20c90c / 0x20caf4`, where `0x21f3f8` also calls
some twenty further series functions (the other planets) and the two lunar functions.

What this does and does not establish: the path exists and the +180 function has no other purpose, so
the Sun's direction is derived from the Earth series. A static call graph cannot show which branch runs
for the Sun at run time; that the Sun takes this route is an inference, a strong one given that the
constants of the simpler stand-alone solar formula are absent from the binary. The method name bound to
`0x16ea6c` was inferred from its strings, not read from the binding table.

## Reading

The Sun's place on the flat map is obtained by computing where the Earth is on its orbit round the
Sun, reversing that direction to get the Sun as seen from the Earth, correcting for nutation and
aberration, and converting to the point on a rotating Earth directly beneath it.

"Embedded data" exists only in the sense that the series coefficients are compiled in. They are the
constants of a formula, evaluated for whatever date the user picks, including dates far from today.

Confidence: high that the engine holds the VSOP87 Earth series and the Meeus lunar series, since
twelve consecutive values match in each case. High that the Sun's direction is derived from that series: see the traced path above. The constants
of Meeus's simple stand-alone solar formula (280.46646, 36000.76983, 357.52911) were searched for and
not found. The coefficient values have been checked against published sources (above), though not against a
printed copy of Meeus.

`get_planetary_ephemeris_interpolated` computes positions at intervals and interpolates between them
for speed. That is a performance device, not a data source.
