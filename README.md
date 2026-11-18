# flat-earth-pro-analysis

Functional breakdown of the **Flat Earth / Flat Earth Pro** mobile app (OProjects, Othman Alzahrani;
Android packages `com.OProjects.FLS` free and `com.OProjects.FLSPro` paid; iOS App Store id 1664580677).

**Question:** which parts of the app are computed from the flat (azimuthal-equidistant) picture it shows,
and which are computed from standard spherical astronomy? Focus area: the sky / star-trails view and the
"fly-in" transition from the map into it.

- `PLAN.md` - phases, acquisition, tooling, ground rules
- `analysis/function-map.md` - the app broken down by function, with what to look for in each
- `analysis/star-trails/test-matrix.md` - the black-box test matrix for the sky view
- `analysis/static/` - findings from static analysis (prose + short excerpts only)
- `evidence/captures/` - our own screenshots / screen recordings, named per the test matrix
- `tools/` - acquisition and triage scripts
- `docs/` - reserved for the published page (GitHub Pages from /docs), once findings are reviewed
- `vendor/` - the app binaries and decompiled output. **Git-ignored. Never committed.**

- `analysis/star-trails/predictions.md` - computed globe vs literal-map predictions (from `tools/refcalc.py`)
- `analysis/public-claims.md` - what the developer's listings say the app is

Status (18 Nov 2026): predictions computed and cross-checked; public claims recorded. No binary obtained
yet, so nothing here is a measurement of the app.
