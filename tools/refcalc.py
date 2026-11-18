#!/usr/bin/env python3
"""Reference calculator for the star-trails test matrix.

Two independent predictions for what an observer sees:

  A  "globe"  - standard spherical astronomy (Meeus, Astronomical Algorithms, 2nd ed.):
                low-precision Sun (ch. 25), mean sidereal time (ch. 12), rigorous precession (ch. 21),
                equatorial -> horizontal (ch. 13). No refraction is applied to altitudes; the standard
                -0.833 deg is used only to define sunrise.
  C  "literal map" - the azimuthal-equidistant (AE) map taken as physically real: each body sits at
                height h above the flat map directly over the point where it is at the zenith
                (lat = declination, lon = RA - GMST), and is seen along a straight line.

C needs the sub-point, which this script takes from the same ephemeris as A. That is deliberate: it is
what the app's map view plots. C is then the purely flat consequence of that picture.

Pure standard library. Run:  python3 tools/refcalc.py > analysis/star-trails/predictions.md
"""
import math
from datetime import datetime, timedelta, timezone

D2R = math.pi / 180.0
R2D = 180.0 / math.pi
KM_PER_DEG = 10007.543 / 90.0          # meridian quadrant / 90: AE radial scale
HEIGHTS_KM = (3000.0, 5000.0, 6000.0)  # C is evaluated across this range; h is a free parameter

LOCATIONS = {  # key: (name, lat, lon east-positive)
    "SYD": ("Sydney", -33.87, 151.21),
    "CPT": ("Cape Town", -33.92, 18.42),
    "SCL": ("Santiago", -33.45, -70.67),
    "USH": ("Ushuaia", -54.80, -68.30),
    "UIO": ("Quito", -0.18, -78.47),
    "LON": ("London", 51.51, -0.13),
    "TOS": ("Tromso", 69.65, 18.96),
    "MCM": ("McMurdo", -77.85, 166.67),
    "TYO": ("Tokyo", 35.68, 139.69),
}

STARS_J2000 = {  # name: (RA deg, Dec deg), J2000, proper motion ignored
    "Polaris": (37.9546, 89.2641),
    "sigma Oct": (317.1950, -88.9565),
    "Acrux": (186.6496, -63.0991),
    "Gacrux": (187.7915, -57.1132),
    "Hadar": (210.9559, -60.3730),
    "Rigil Kent": (219.9021, -60.8340),
    "Canopus": (95.9880, -52.6957),
}

DATES = {  # label: UTC date used to build each location's local-day window
    "21 Dec 2026": (2026, 12, 21),
    "20 Mar 2027": (2027, 3, 20),
    "21 Jun 2027": (2027, 6, 21),
}


def utc(y, mo, d, h=0, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=timezone.utc)


def jd(dt):
    return dt.timestamp() / 86400.0 + 2440587.5


def norm360(x):
    return x % 360.0


def norm180(x):
    return (x + 180.0) % 360.0 - 180.0


# ---------- A: spherical astronomy ----------

def sun_radec(dt):
    """Apparent RA/Dec of the Sun in degrees. Meeus ch. 25 low-precision (~0.01 deg)."""
    T = (jd(dt) - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    Mr = M * D2R
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(Mr)
         + (0.019993 - 0.000101 * T) * math.sin(2 * Mr)
         + 0.000289 * math.sin(3 * Mr))
    omega = (125.04 - 1934.136 * T) * D2R
    lam = (L0 + C - 0.00569 - 0.00478 * math.sin(omega)) * D2R
    eps0 = 23.0 + 26.0 / 60 + 21.448 / 3600 - (46.8150 * T + 0.00059 * T * T - 0.001813 * T ** 3) / 3600
    eps = (eps0 + 0.00256 * math.cos(omega)) * D2R
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam)) * R2D
    dec = math.asin(math.sin(eps) * math.sin(lam)) * R2D
    return norm360(ra), dec


def gmst_deg(dt):
    """Greenwich mean sidereal time in degrees. Meeus eq. 12.4."""
    d = jd(dt) - 2451545.0
    T = d / 36525.0
    return norm360(280.46061837 + 360.98564736629 * d + 0.000387933 * T * T - T ** 3 / 38710000.0)


def precess_from_j2000(ra, dec, dt):
    """Rigorous precession J2000 -> date. Meeus eq. 21.2-21.4."""
    T = (jd(dt) - 2451545.0) / 36525.0
    zeta = (2306.2181 * T + 0.30188 * T * T + 0.017998 * T ** 3) / 3600 * D2R
    z = (2306.2181 * T + 1.09468 * T * T + 0.018203 * T ** 3) / 3600 * D2R
    theta = (2004.3109 * T - 0.42665 * T * T - 0.041833 * T ** 3) / 3600 * D2R
    a, d = ra * D2R, dec * D2R
    A = math.cos(d) * math.sin(a + zeta)
    B = math.cos(theta) * math.cos(d) * math.cos(a + zeta) - math.sin(theta) * math.sin(d)
    Cc = math.sin(theta) * math.cos(d) * math.cos(a + zeta) + math.cos(theta) * math.sin(d)
    return norm360((math.atan2(A, B) + z) * R2D), math.asin(max(-1.0, min(1.0, Cc))) * R2D


def body_radec(body, dt):
    if body == "Sun":
        return sun_radec(dt)
    return precess_from_j2000(*STARS_J2000[body], dt)


def altaz_globe(lat, lon, ra, dec, dt):
    """Altitude and azimuth (from north through east), degrees. Geometric, no refraction."""
    H = (gmst_deg(dt) + lon - ra) * D2R
    p, d = lat * D2R, dec * D2R
    alt = math.asin(math.sin(p) * math.sin(d) + math.cos(p) * math.cos(d) * math.cos(H))
    az = math.atan2(-math.cos(d) * math.sin(H),
                    math.sin(d) * math.cos(p) - math.cos(d) * math.sin(p) * math.cos(H))
    return alt * R2D, norm360(az * R2D)


def subpoint(ra, dec, dt):
    """Lat/lon where the body is at the zenith."""
    return dec, norm180(ra - gmst_deg(dt))


# ---------- C: literal AE map ----------

def ae_xy(lat, lon):
    r = (90.0 - lat) * KM_PER_DEG
    return r * math.cos(lon * D2R), r * math.sin(lon * D2R)


def altaz_flat(lat, lon, sub_lat, sub_lon, h_km):
    """Elevation, azimuth and slant distance of a body at height h over its sub-point on the AE plane.
    Azimuth is measured from the observer's map-north (toward the pole at the map centre) through
    map-east (direction of increasing longitude)."""
    px, py = ae_xy(lat, lon)
    sx, sy = ae_xy(sub_lat, sub_lon)
    vx, vy = sx - px, sy - py
    pr = math.hypot(px, py)
    nx, ny = (-px / pr, -py / pr) if pr > 0 else (1.0, 0.0)
    ex, ey = -math.sin(lon * D2R), math.cos(lon * D2R)
    d = math.hypot(vx, vy)
    az = norm360(math.atan2(vx * ex + vy * ey, vx * nx + vy * ny) * R2D)
    return math.atan2(h_km, d) * R2D, az, d, math.hypot(d, h_km)


# ---------- helpers ----------

def local_day_start(lon, ymd):
    """UTC instant of local mean midnight at the start of the given date."""
    return utc(*ymd) - timedelta(hours=lon / 15.0)


def sun_alt(lat, lon, dt):
    return altaz_globe(lat, lon, *sun_radec(dt), dt)[0]


def find_crossings(lat, lon, t0, level=-0.833, rising=True):
    """Instants in [t0, t0+24h) where the Sun's altitude crosses `level`."""
    out, step = [], timedelta(minutes=2)
    t, a = t0, sun_alt(lat, lon, t0) - level
    for _ in range(720):
        t2 = t + step
        a2 = sun_alt(lat, lon, t2) - level
        if (a < 0 <= a2) if rising else (a >= 0 > a2):
            lo, hi = t, t2
            for _ in range(30):
                mid = lo + (hi - lo) / 2
                am = sun_alt(lat, lon, mid) - level
                if (am < 0) == rising:
                    lo = mid
                else:
                    hi = mid
            out.append(hi)
        t, a = t2, a2
    return out


def day_extremes(lat, lon, t0):
    best_hi, best_lo = (-99, None), (99, None)
    for k in range(1440):
        t = t0 + timedelta(minutes=k)
        a = sun_alt(lat, lon, t)
        if a > best_hi[0]:
            best_hi = (a, t)
        if a < best_lo[0]:
            best_lo = (a, t)
    return best_hi, best_lo


def fmt_t(dt):
    return dt.strftime("%Y-%m-%d %H:%M")


def compass(az):
    """Describe an azimuth relative to due east or due west, whichever is nearer."""
    if 0 <= az <= 180:
        off = az - 90
        return "due E" if abs(off) < 0.5 else f"{abs(off):.0f} deg {'S' if off > 0 else 'N'} of E"
    off = 270 - az
    return "due W" if abs(off) < 0.5 else f"{abs(off):.0f} deg {'S' if off > 0 else 'N'} of W"


# ---------- report sections ----------

def section_sunrise(p):
    p("## 1. Sunrise direction and height (tests ST5, ST6, ST7)\n")
    p("At the instant the globe calculation puts the Sun on the horizon, where does the literal map put it?")
    p("`C az` does not depend on the Sun's height h. `C elev` is given for h = 3000 / 5000 / 6000 km.")
    p("`size` is the Sun's apparent diameter at that instant relative to the same day's local noon under C")
    p("(h = 5000 km); on the globe it is 1.00 to within 2%.\n")
    p("| Date | Place | Sunrise UTC | A az | A | C az | C | C elev (deg) | C size vs noon |")
    p("|---|---|---|---|---|---|---|---|---|")
    for label, ymd in DATES.items():
        for key in ("SYD", "CPT", "SCL", "USH", "UIO", "LON", "TOS"):
            name, lat, lon = LOCATIONS[key]
            t0 = local_day_start(lon, ymd)
            rises = find_crossings(lat, lon, t0)
            if not rises:
                hi, lo = day_extremes(lat, lon, t0)
                why = "Sun up all day" if lo[0] > -0.833 else "Sun down all day"
                p(f"| {label} | {name} | none ({why}; A alt range {lo[0]:.1f} to {hi[0]:.1f}) | | | | | | |")
                continue
            t = rises[0]
            ra, dec = sun_radec(t)
            _, az_a = altaz_globe(lat, lon, ra, dec, t)
            sl, sn = subpoint(ra, dec, t)
            elevs, az_c = [], None
            for h in HEIGHTS_KM:
                e, az_c, _, _ = altaz_flat(lat, lon, sl, sn, h)
                elevs.append(e)
            slant_rise = altaz_flat(lat, lon, sl, sn, 5000.0)[3]
            hi, _ = day_extremes(lat, lon, t0)
            ran, decn = sun_radec(hi[1])
            slant_noon = altaz_flat(lat, lon, *subpoint(ran, decn, hi[1]), 5000.0)[3]
            p(f"| {label} | {name} | {fmt_t(t)} | {az_a:.1f} | {compass(az_a)} | {az_c:.1f} | {compass(az_c)} | "
              f"{elevs[0]:.1f} / {elevs[1]:.1f} / {elevs[2]:.1f} | {slant_noon / slant_rise:.2f} |")
    p("")


def section_min_elev(p):
    p("## 2. Does the Sun ever set under C? (test ST6)\n")
    p("Lowest elevation the literal-map Sun reaches during the whole local day, against the globe's lowest")
    p("altitude for the same day.\n")
    p("| Date | Place | A lowest alt | C lowest elev, h=3000 | h=5000 | h=6000 |")
    p("|---|---|---|---|---|---|")
    for label, ymd in DATES.items():
        for key in ("SYD", "USH", "UIO", "LON", "TOS"):
            name, lat, lon = LOCATIONS[key]
            t0 = local_day_start(lon, ymd)
            _, lo = day_extremes(lat, lon, t0)
            mins = []
            for h in HEIGHTS_KM:
                m = 90.0
                for k in range(0, 1440, 5):
                    t = t0 + timedelta(minutes=k)
                    ra, dec = sun_radec(t)
                    m = min(m, altaz_flat(lat, lon, *subpoint(ra, dec, t), h)[0])
                mins.append(m)
            p(f"| {label} | {name} | {lo[0]:.1f} | {mins[0]:.1f} | {mins[1]:.1f} | {mins[2]:.1f} |")
    p("")


def section_pole(p):
    p("## 3. Centre of rotation of the night sky (tests ST1, ST2, ST4)\n")
    p("A: the sky turns about the celestial pole, at altitude = |latitude|, due north in the northern")
    p("hemisphere (counter-clockwise) and due south in the southern (clockwise). At the equator both poles")
    p("sit on the horizon.")
    p("C: one centre only, the point over the map's north pole, always due north.\n")
    p("| Place | Lat | A centre | A sense facing it | C centre az | C centre elev h=3000 / 5000 / 6000 |")
    p("|---|---|---|---|---|---|")
    for key in ("SYD", "CPT", "SCL", "USH", "UIO", "LON", "TOS"):
        name, lat, lon = LOCATIONS[key]
        if abs(lat) < 1:
            a_c, sense = "N and S poles both on horizon", "ccw facing N, cw facing S"
        elif lat > 0:
            a_c, sense = f"az 0, alt {lat:.1f}", "counter-clockwise"
        else:
            a_c, sense = f"az 180, alt {-lat:.1f}", "clockwise"
        r = (90.0 - lat) * KM_PER_DEG
        el = [math.atan2(h, r) * R2D for h in HEIGHTS_KM]
        p(f"| {name} | {lat:.2f} | {a_c} | {sense} | 0 | {el[0]:.1f} / {el[1]:.1f} / {el[2]:.1f} |")
    p("")


def best_dark_instant(keys, ymd):
    t0 = utc(*ymd)
    best = (99, None)
    for k in range(0, 1440, 5):
        t = t0 + timedelta(minutes=k)
        worst = max(sun_alt(LOCATIONS[c][1], LOCATIONS[c][2], t) for c in keys)
        if worst < best[0]:
            best = (worst, t)
    return best


def section_shared_south(p):
    p("## 4. The same southern stars from three continents (test ST3)\n")
    p("On the AE map 'due south' is radially outward, so the three cities' south directions diverge by their")
    p("longitude differences: Sydney-Cape Town 133 deg, Cape Town-Santiago 89 deg, Santiago-Sydney 138 deg.\n")
    worst, t_all = best_dark_instant(("SYD", "CPT", "SCL"), DATES["21 Jun 2027"])
    p(f"All three are never in darkness together: on 21 Jun 2027 the best instant ({fmt_t(t_all)} UTC) still")
    p(f"has the Sun at {worst:+.1f} deg at one of them. So the test is run pairwise, at the darkest shared")
    p("instant for each pair on that date.\n")
    p("| Instant UTC | Place | Sun alt (A) | Star | A alt | A az | C az | C elev h=5000 | A separation | C az separation |")
    p("|---|---|---|---|---|---|---|---|---|---|")
    for pair in (("SYD", "CPT"), ("CPT", "SCL"), ("SCL", "SYD")):
        _, t = best_dark_instant(pair, DATES["21 Jun 2027"])
        for star in ("sigma Oct", "Acrux"):
            ra, dec = body_radec(star, t)
            sl, sn = subpoint(ra, dec, t)
            rows = []
            for key in pair:
                name, lat, lon = LOCATIONS[key]
                alt_a, az_a = altaz_globe(lat, lon, ra, dec, t)
                el_c, az_c, _, _ = altaz_flat(lat, lon, sl, sn, 5000.0)
                rows.append((name, sun_alt(lat, lon, t), alt_a, az_a, az_c, el_c))
            for i, (name, sa, alt_a, az_a, az_c, el_c) in enumerate(rows):
                tail = ""
                if i == 1:
                    tail_a = abs(norm180(rows[0][3] - rows[1][3]))
                    tail_c = abs(norm180(rows[0][4] - rows[1][4]))
                    tail = f" {tail_a:.1f} | {tail_c:.1f} |"
                else:
                    tail = " | |"
                p(f"| {fmt_t(t)} | {name} | {sa:+.1f} | {star} | {alt_a:.1f} | {az_a:.1f} | {az_c:.1f} | {el_c:.1f} |{tail}")
    p("")
    p("Read the last two columns as: how far apart the two observers' compass bearings to the same star are.")
    p("For a star near the south celestial pole the globe gives both observers a bearing close to 180.\n")


def section_midnight_sun(p):
    p("## 5. Midnight Sun, and why a range cut-off does not rescue C (test ST8)\n")
    p("Under straight-line C the Sun never sets anywhere (section 2). The usual repair is a maximum range")
    p("beyond which the Sun is not seen. This compares map distances from the sub-solar point at one instant.\n")
    for key, ymd, dark_key in (("MCM", DATES["21 Dec 2026"], "TYO"), ("TOS", DATES["21 Jun 2027"], None)):
        name, lat, lon = LOCATIONS[key]
        t0 = local_day_start(lon, ymd)
        _, lo = day_extremes(lat, lon, t0)
        t = lo[1]
        ra, dec = sun_radec(t)
        sl, sn = subpoint(ra, dec, t)
        d_lit = altaz_flat(lat, lon, sl, sn, 5000.0)[2]
        p(f"- **{name}**, {fmt_t(t)} UTC (the Sun's lowest point that day): globe altitude {lo[0]:+.1f} deg, so it is")
        p(f"  up all 24 hours. Map distance from the sub-solar point ({sl:.1f}, {sn:.1f}): {d_lit:,.0f} km.")
        if dark_key:
            dn, dlat, dlon = LOCATIONS[dark_key]
            a = sun_alt(dlat, dlon, t)
            d_dark = altaz_flat(dlat, dlon, sl, sn, 5000.0)[2]
            p(f"  At the same instant **{dn}** has the Sun at {a:+.1f} deg (night) and is {d_dark:,.0f} km from the")
            p(f"  sub-solar point on the map. The sunlit place is {d_lit / d_dark:.1f}x farther from the map Sun than")
            p("  the dark one, so no single visibility range reproduces both.")
    p("")


def main():
    lines = []
    p = lines.append
    p("# Predictions for the star-trails test matrix\n")
    p("Generated by `tools/refcalc.py`. Do not edit by hand; change the script and regenerate.\n")
    p("- **A** = spherical astronomy (Meeus algorithms; Sun good to about 0.01 deg, stars precessed from J2000,")
    p("  no proper motion, no refraction on altitudes).")
    p("- **C** = the app's own map taken literally: body at height h over its sub-point on the AE plane,")
    p("  straight-line sight. h is a free parameter, so C is shown for 3000, 5000 and 6000 km.")
    p("- Azimuths are degrees from north through east. These are predictions, not measurements of the app.\n")
    section_sunrise(p)
    section_min_elev(p)
    section_pole(p)
    section_shared_south(p)
    section_midnight_sun(p)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
