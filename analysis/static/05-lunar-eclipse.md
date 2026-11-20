# 05. Lunar eclipses

Question: does the app handle lunar eclipses, and how?

## Scripts (`Script/Eclipse.gd`, `Script/ui_events.gd`)

- `Astronify.get_lunar_eclipses(year-2, year+2)` gives a list with `JD`, `UmbralMagnitude`,
  `PenumbralMagnitude`, `IsPenumbral`. `ui_events.gd` labels each Total / Partial / Penumbral.
- Within 1.1 days of a listed eclipse, `Eclipse.gd` calls
  `Astronify.compute_lunar_eclipse_shadow(TimeEngine.JD_TT, true)` every second and registers
  `setup_lunar_eclipse_spot` for both the "3D" (sky) and "2D" (map) pipelines.
- That passes `xShadow`, `yShadow`, `penumbralRadius`, `umbralRadius` to the Moon's material
  (`SSObject.gdshader`, loop at lines ~602-614), which multiplies the Moon's colour by a dark red
  (0.141, 0.035, 0.039), graded between the penumbra and umbra radii. Circular shadow.
- `Astronomy.RefractionFromTrue(moon.Altitude)` is passed into the occlusion fraction.
- `draw_test_lunar_eclipse` (Eclipse.gd) and `test_lunarecliips` (MapView.gd) have no callers in the
  recovered scripts: leftover debug code.

## Engine (`libFELIBS`, arm64)

Binder wrapper at `0x177be4` (fills the result dictionary: shadowRA, shadowDec, umbralRadiusDeg,
penumbralRadiusDeg, gamma, moonParallaxDeg, moonRA, moonDec, sunRA, sunDec, ...). It calls
`0x1fee10`, which calls the core routine `0x1fec00`. Read instruction by instruction:

1. `bl 0x20bcb8` (VSOP87 Earth longitude, see note 03), `+180.0`, `fmod 360` -> Sun longitude.
   `bl 0x20c90c` (Earth latitude), `bl 0x20caf4` (Earth radius vector R).
2. Ecliptic -> equatorial (`0x1fba88`) -> Sun RA, Dec.
3. `s_sun = 0.2665638889 / R` deg (959.63"), `pi_sun = 0.0024427778 / R` deg (8.794").
4. Moon longitude / latitude / distance (`0x202814`, `0x202e80`, `0x202c00`), -> Moon RA, Dec.
   `pi_moon = f(distance)` via `0x203280`. Also `asin(1737.4 / distance)` for the Moon's semidiameter.
5. `umbra    = pi_sun + (1.01 * pi_moon - s_sun)`   (fnmsub at `0x1fed64`)
   `penumbra = pi_sun + (1.01 * pi_moon + s_sun)`   (fmadd at `0x1fed68`)
6. `shadowRA = fmod(sunRA + 12, 24)`, `shadowDec = -sunDec` (fneg at `0x1fed98`).
7. Separation Moon-shadow (`0x1f9f24`), `gamma = sin(sep) / sin(pi_moon)`, signed.

This is the classical shadow geometry (Meeus ch. 54 uses the same quantities; 1.01 is close to the
traditional 1/85 - 1/594 enlargement for the atmosphere).

## Not read

- `get_lunar_eclipses` (the date list).
- The sibling function at `0x1787ac` with `umbralEllipticity` / `penumbralEllipticity`. Its string
  neighbour is `compute_planetMoon_shadow_disk`, so it is probably for moons' shadows on planets
  (Jupiter, Saturn), not the Earth's shadow. Unverified.

## Other side

Eclipse dates can be predicted from Saros cycles without a globe. That does not cover what the
drawing code does: a round shadow, sized by the Earth's parallax at the Moon, at the anti-solar point.
The 1.01 factor is empirical. Not yet seen running in the app.
