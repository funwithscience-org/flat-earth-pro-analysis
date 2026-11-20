# Observer height: what it changes and what it does not

Build: `com.OProjects.FLS` versionCode 250004. Sources: recovered scripts and the disassembled engine
(`libFELIBS`, arm64). Confidence: high for the rise/set formula (read instruction by instruction);
medium for "nowhere else", which rests on searches.

## Rise and set times: yes, through the dip of the horizon on a sphere

The scripts pass the height to the engine's event functions:

    Astronify.get_celestial_body_events(id, JD0, JD1, User.Location.LONGITUDE, User.Location.LATITUDE, User.Location.Height)

(`Script/ui_horizontal_graph.gd`, lines 123-125; a sibling handles stars.) In the engine, the function
at `0x172428` picks the altitude at which a body counts as rising or setting. With our labels:

    if height > 0:
        x  = acos( 6371008.0 / (6371008.0 + height) )      ; radians
        h0 = base - x * 57.29577951308232                  ; degrees
    else:
        h0 = base
    base = -0.8333 for one body id (the Sun's standard altitude), -0.5667 for the others

Constants as found: `0x41584DB000000000` = 6371008.0 (the Earth's mean radius in metres), -0.8333,
-0.5667, -57.29577951308232, and a call to `acos`. The star-events function at `0x1725fc` also calls
`acos`. The Moon takes a separate branch that was not read.

`acos(R / (R + h))` is the geometric dip of the horizon for an observer h above a sphere of radius R.
Examples from the formula: 100 m gives 0.32 degrees, 1,000 m gives 1.02 degrees, 3,000 m gives 1.76
degrees. Sunrise comes earlier and sunset later by the time the Sun takes to cover that extra angle.

So the app's sunrise and sunset times for an elevated observer depend on the Earth being a ball of
radius 6,371 km. On a plane there is no dip: height would not move the horizon.

Not applied: any refraction adjustment to the dip itself (it is the purely geometric value).

## The Sun's angle in the sky view: effectively no

Height reaches the altitude calculation only through parallax
(`astro.get_topocentric_RaDecl(..., User.Location.Height)`, `Astronomy.gd` line 185). For the Sun that
is a few thousandths of an arcsecond per kilometre of height; for the Moon a little more. No dip is
applied to the displayed altitude, and no search found the drawn horizon being lowered with height.

Net effect to expect: change the height and the Sun's altitude readout will not move visibly, but the
listed rise and set times will.

## A display bug to know about before testing

`Script/location_tab.gd` line 113 writes the height into the pressure box, just after writing the
pressure there:

    % pressure_input.text = "%0.2f" % User.Location.Pressure
    ...
    % pressure_input.text = "%0.2f" % User.Location.Height

That matches the iPhone captures, where the box labelled Pressure reads 194.00 and the box labelled
Height reads 1010. The input handlers store typed values in the right variables, so type the height
into the Height box; the Pressure box may then show it. Not tested.
