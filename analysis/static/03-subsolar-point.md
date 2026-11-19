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

## Reading

The Sun's place on the flat map is obtained by computing where the Earth is on its orbit round the
Sun, reversing that direction to get the Sun as seen from the Earth, correcting for nutation and
aberration, and converting to the point on a rotating Earth directly beneath it.

"Embedded data" exists only in the sense that the series coefficients are compiled in. They are the
constants of a formula, evaluated for whatever date the user picks, including dates far from today.

Confidence: high that the engine holds the VSOP87 Earth series and the Meeus lunar series, since
twelve consecutive values match in each case. Medium that the Sun's position is taken from that
series and not from a second, simpler formula elsewhere in the binary: the function names
(`TrueHeliocentricEclipticalLongitude`, `ApparentGeocentricRA`) and the absence of the constants of
Meeus's simple solar formula (280.46646, 36000.76983, 357.52911 were searched for and not found) both
point that way, but the code path was not traced. The coefficient values are identified from memory of
the published tables and should be checked against a printed copy before being cited.

`get_planetary_ephemeris_interpolated` computes positions at intervals and interpolates between them
for speed. That is a performance device, not a data source.
