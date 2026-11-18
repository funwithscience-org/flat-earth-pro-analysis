# What the developer publicly says the app is

Read 18 Nov 2026 from the store listings and the developer's site. Paraphrased; one short quotation per
source. This file exists because the question "is the globe maths hidden?" depends on what is claimed.

## Sources

- Google Play, free app `com.OProjects.FLS`: https://play.google.com/store/apps/details?id=com.OProjects.FLS
- App Store, Flat Earth Pro: https://apps.apple.com/us/app/flat-earth-pro/id1664580677
- Developer site: https://www.oproject.xyz/
- Third-party copies of the older Android Pro description (Similarweb, AppBrain)

## What is claimed

| Topic | What the listing says | Source |
|---|---|---|
| What the app is | A map plus a sky simulation; both run on "the same astronomical model and the same clock" | Google Play (free) |
| Earth's shape | No listing read states that the Earth is flat. The name is "Flat Earth"; the body text talks about projections and presentation | all |
| Map | Several geographic projections with azimuthal equidistant as the default; animated transitions between projections; bodies plotted at sub-solar / sub-stellar points | Google Play (free) |
| Sky | "Telescope Mode": local sky for any latitude, longitude, date and time; animated transition between map and sky | Google Play (free) |
| Data shown per object | Right ascension and declination, altitude and azimuth, distance, apparent angular diameter, rise/transit/set | Google Play (free) |
| Older framing | Bodies shown "on a flat and simple geocentric presentation" | Similarweb copy of Android Pro description |
| iOS framing | An "azimuthal projection of the earth"; a sky dome view via the navigation tab | App Store |
| Developer site | One line calling it a geocentric presentation; sister apps include one for exploring map projections | oproject.xyz |

## Versions: there appear to be two codebases

- Free Android app: updated 17 Nov 2026. The listing describes Map Mode and Telescope Mode. Some recent
  user reviews complain that an update moved the app toward a spherical-Earth presentation.
- Android Pro: last updated Oct 2025 per AppGoblin. Probably the older design.
- iOS Pro: version notes mention astronomical calculations moved to "low level computations" (so
  possibly native code rather than script).

Record which build every observation comes from. A finding about one may not hold for the other.

## What this does and does not support

- **Against "hiding":** the current free listing openly says the two views share one astronomical model,
  offers non-flat projections, and displays RA/Dec, distance and angular diameter. The developer's site
  says "geocentric", not "flat". On the public record, the spherical astronomy is disclosed, not concealed.
- **For a narrower criticism:** the product is named and marketed to a flat-earth audience, and its
  reviews show users taking it as confirmation of a flat Earth. The app's sky view cannot be derived from
  its map view (see `star-trails/predictions.md`), and nothing in the listings tells users that.
- **Unknown until the app is in hand:** what the in-app text, onboarding and settings say; whether the
  older Pro build made stronger flat claims; what the developer has said elsewhere.

Suggested wording discipline: describe what the software does and what its users infer. Do not assert
intent to deceive without a statement from the developer that supports it.
