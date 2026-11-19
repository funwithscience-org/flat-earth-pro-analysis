#!/usr/bin/env python3
"""Does the Moon's lit side, as drawn on the app's flat map, point at the map's Sun marker?

The app draws the Moon on the map with celestial north toward the map centre and no observer correction
(see analysis/static/02-moon-phase-orientation.md). On the sky, the bright limb points along the great
circle to the Sun, at position angle chi from celestial north (Meeus, Astronomical Algorithms, eq. 48.5).
On the azimuthal-equidistant map the Sun marker lies along a straight line from the Moon marker, at
some bearing from "toward the centre". This script compares the two.

Needs astropy (built-in ephemeris; no downloads).  python3 tools/moon_limb.py
"""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refcalc as rc
from datetime import datetime, timezone, timedelta
from astropy.utils import iers
iers.conf.auto_download = False
iers.conf.iers_degraded_accuracy = "ignore"
from astropy.time import Time
from astropy.coordinates import get_body, get_sun
import astropy.units as u

D2R = math.pi / 180


def radec(body, dt):
    t = Time(dt)
    c = (get_sun(t) if body == "sun" else get_body("moon", t)).tete
    return c.ra.deg, c.dec.deg


def chi_sky(ra_m, dec_m, ra_s, dec_s):
    """Position angle of the Moon's bright limb, degrees from celestial north through east."""
    da = (ra_s - ra_m) * D2R
    y = math.cos(dec_s * D2R) * math.sin(da)
    x = math.sin(dec_s * D2R) * math.cos(dec_m * D2R) - math.cos(dec_s * D2R) * math.sin(dec_m * D2R) * math.cos(da)
    return math.degrees(math.atan2(y, x)) % 360


def map_bearing(sub_m, sub_s):
    """Bearing on the AE map from the Moon marker to the Sun marker: from map-north through map-east."""
    return rc.altaz_flat(sub_m[0], sub_m[1], sub_s[0], sub_s[1], 5000.0)[1]


def elong(ra_m, dec_m, ra_s, dec_s):
    c = (math.sin(dec_m * D2R) * math.sin(dec_s * D2R)
         + math.cos(dec_m * D2R) * math.cos(dec_s * D2R) * math.cos((ra_m - ra_s) * D2R))
    return math.degrees(math.acos(max(-1, min(1, c))))


def main():
    print("| Date (00:00 UTC) | Moon-Sun angle | Lit fraction | Lit side on the sky (chi) | Sun marker from Moon marker on the map | Difference |")
    print("|---|---|---|---|---|---|")
    worst = 0
    t0 = datetime(2026, 11, 10, tzinfo=timezone.utc)
    for d in range(0, 30, 2):
        dt = t0 + timedelta(days=d)
        ra_m, dec_m = radec("moon", dt)
        ra_s, dec_s = radec("sun", dt)
        e = elong(ra_m, dec_m, ra_s, dec_s)
        k = (1 - math.cos(e * D2R)) / 2          # geocentric lit fraction, to within the Moon's small parallax
        chi = chi_sky(ra_m, dec_m, ra_s, dec_s)
        sm = rc.subpoint(ra_m, dec_m, dt)
        ss = rc.subpoint(ra_s, dec_s, dt)
        # On the map, north is toward the centre and east is the direction of increasing longitude.
        # Celestial east and geographic east agree for a sub-point, so chi can be compared directly.
        b = map_bearing(sm, ss)
        diff = (chi - b + 180) % 360 - 180
        worst = max(worst, abs(diff))
        print(f"| {dt:%d %b %Y} | {e:.0f} | {k:.2f} | {chi:.0f} | {b:.0f} | {diff:+.0f} |")
    print(f"\nLargest difference in this run: {worst:.0f} degrees.")


if __name__ == "__main__":
    main()
