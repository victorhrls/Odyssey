# Design feedback, round 2 (last)

Screenshots in `shots/d2-*.png`, desktop 1440x900 and phone 400x800 with touch. Lines cited are from `src/app.html` in this version.

## 1. Grade: 3.5 / 5

Today's grade. With items 1 to 4 applied, it reaches 4.0.

| Criterion | Grade | In one sentence |
|---|---|---|
| Visual identity and fidelity to the reference | 4.0 | It already looks like a game map, with curved routes and ink labels. The blue wedge in Greece breaks the illusion. |
| Map legibility | 3.5 | The opening view and Sicily improved a lot. Labels still sit on top of routes and the name of Ithaca is weak. |
| Hierarchy and typography | 3.5 | The map leads and the panel has stepped back. The translucent panel dirties the text and "Hide all" breaks onto two lines. |
| Usability and clarity of interaction | 4.0 | Book, comparison, itinerary and playback work. Agamemnon's name is missing in the comparison at zoom 6. |
| Phone | 3.5 | The drawer and itinerary came out well. Playback and the zoom controls have visible defects. |

At-a-glance answers today:
- **Where is Ithaca?** Yes, by the pin. The name is still the palest label on the map.
- **Where does Telemachus go?** Yes, sharp (`d2-telemaco`, `d2-m-telemaco`).
- **Where did Odysseus pass?** Almost: the leg within sight of Ithaca (stop 7) ends in open sea, with no pin.

## 2. What works (preserve)

- Curved routes with a direction hand and cream casing. It solved the Tyrrhenian and Messina (`d2-tirreno`, `d2-sicilia`).
- Pill groups with a wire to the pin, and the row attached to Troy (`d2-egeu`).
- The single bottom strip with legend and books, and the 17 characters with almost no scrolling.
- A book with a strong protagonist and thin others (`d2-canto3`, `d2-canto9`).
- Name tags on the compared routes (`d2-comp-itaca`).
- The playback trail and the ship counter.
- The phone itinerary drawer with "See more" (`d2-m-telemaco`). It is the best phone state.
- The Cretan lie (`d2-mentira`).

Do not touch structure, panel or fonts.

## 3. Prioritized fixes

### P0

**1. Sea-colored wedge and needles in Greece** · `d2-comp-itaca` (wedge at x 770-890, y 50-190), `d2-atena`, `d2-play-4500`, `d2-telemaco` (needles at x=890), `d2-canto3`

This is the worst defect, it shows at zoom ≥ 7.3, and it came from my instruction to smooth `land.high`. The polygons are clipped to the HB rectangle, and the curve rounds the corners and edges of the clip. In `buildLand`, replace the curve line with:

```js
if(codes[i]){fill.lineTo(X(b),Y(b));fill.lineTo(e[0],e[1])}
else fill.quadraticCurveTo(X(b),Y(b),e[0],e[1]);
```

I tested it on a copy of the build: the wedge and the needles go away, with no change to the coast. Re-photograph `flyTo(38.8,21.5,8.2)` and `selectCharacter('telemachus')`.

**2. Stop 7 ends at sea and counts toward Ithaca** · `d2-ulisses` (lines end at x=983), `d2-crop-itaca` (pill "7·19–22")

My rule to hide "Within sight of Ithaca" below zoom 7.5 went too far: there are two lines arriving at nowhere, and the pill suggests he landed at stop 7. On lines 994 and 1045, the rule only applies if no active character or the current book has a stop in `ithaca_sight`. When one does:
- The pin shows at any zoom, at 16px below zoom 7, and the label only from 7.5.
- The "7" pill is its own, not grouped with "19–22".
- Exclude `ithaca_sight` from the union with Ithaca in the grouping. At zoom 6 it may sit next to the Ithaca pin, without overlapping (the Ithaca pin is on top).

**3. Pale Ithaca name and pin covering the inner points** · `d2-crop-itaca`, `d2-itaca`, `d2-mobile-lugar`, `d2-mentira`

- `.lbl.itaca` (line 68): `font:400 20px/24px var(--f-display); letter-spacing:.05em; color:#120a02; -webkit-text-stroke:.35px #120a02; text-shadow:0 0 1px #fbf3dc,0 0 2px #fbf3dc,0 0 4px #fbf3dc,0 0 8px rgba(251,243,220,.95)`. It must be the darkest label on the map.
- At zoom ≥ 9.5, shrink the Ithaca pin to 20px, without the ring, and draw it below the `parent:ithaca` pins. In `d2-itaca` and `d2-mobile-lugar` it hides the Harbor of Phorcys.
- At zoom < 8, hide the pins with no emphasis (outside the focused route and the book) whose center is less than 24px from the center of Ithaca, like Same in `d2-mentira`.

**4. Labels over routes, over pins and in the fog** · `d2-telemaco` ("Pherae" and "Sparta" cut by the stroke), `d2-mobile-lugar` ("Paliki" over the Same pin), `d2-zoomout` ("Land of the Lotus-Eaters" dark in the fog), `d2-lestrigoes` (alts almost invisible)

When choosing among the 4 label positions:
- Add to the occupancy the points of the active routes, sampled every 12px, with a 6x6 box. Try the positions with no collision and, only if none works, use the one that collides with the fewest points. Never hide Ithaca, Troy, the current stop or a stop of the focused route.
- Eliminate positions whose box leaves the `bbox` area minus the fog (2.6 units).
- `.lbl.alt` (line 69): `color:#2c1c0a; font-weight:600`, no transparency. Alt labels collide with pins like the others. If they collide, use another side.

### P1

**5. Agamemnon without a name in the comparison of 4** · `d2-comparar`

The tag disappears in the collision at zoom 6, precisely the one the user asked for. The route tag can never disappear:
- Test 12 positions, with radii of 22px and 40px around the last stop.
- If none fits, place it at half the route length.
- If it still collides, draw it on top with priority over ordinary place labels, and hide those labels.

**6. Translucent panels dirty the text** · `d2-sicilia` (bluish panel with smudges behind the itinerary), `d2-play-12000` (pins visible through the bar), `d2-m-play` ("Syria" over books II and III), `d2-inicial` ("Hide all" on 2 lines, Poseidon cut off)

It was my .84 instruction, which was exaggerated:
- `#side`: background `rgba(14,12,9,.95)`.
- `#bottom`: `rgba(14,12,9,.94)`. On the phone, a books strip with solid `#14110c`.
- `#playbar`: solid `#14110c`.
- Line 349: text "Hide", `white-space:nowrap`, `aria-label="Hide all routes"`, only on the Characters tab. On line 1363, remove the duplicate link: "Comparing N routes".
- Line 1364: shorten to "Name opens the itinerary. Circle compares." on one line, which frees the 16px missing for Poseidon on desktop.

**7. Playback and controls on the phone** · `d2-play-4500`, `d2-crop-navio`, `d2-play-seek13`, `d2-m-play`, `d2-mobile`

- Trail: replace the grey with the character's color at alpha .3, 2.5px, no casing. The grey looks like a road and does not belong to the palette.
- Ship marker: a 16px triangle, 2px cream casing, drawn above everything on the canvas. Move a dedicated element into `#pins` if the canvas ends up below the pill.
- Start: in `d2-play-4500` the "1" pill covers the marker, and it looks like a cursor. During `phase==='move'`, remove `.cur` from the origin stop and apply it to the destination only on arrival. Hide the origin pill in the first 15% of the leg.
- When playing on the phone, hide the zoom buttons, which cover the map right above the bar (`d2-m-play`). Pinch still works.
- On the phone at rest, replace the L-shaped block with a row: frame, −, +, 44px each, flush right.

**8. Finish of the map and the legend** · `d2-crop-itaca`, `d2-inicial`, `d2-m-legenda`, `d2-itaca`, `d2-sicilia`

- `GREECE` at zoom < 7: the "CE" falls into the sea and disappears. Anchor at lat 39.6, lon 21.7, with `letter-spacing:.18em`.
- `AEGEAN SEA` at zoom < 7: today it vanishes. Draw it on two lines, "AEGEAN" and "SEA", 12px, centered at lat 39.0, lon 24.6, between the coast and the route. At zoom ≥ 7, one line as now.
- Relief at zoom 6 still streaks Turkey (`d2-mentira`): `lerp(.42,.25,…)` in place of `.6`.
- The legend samples (`.lg li svg`) became blurs. Replace with a straight 28px `<line>`: sea with cream 5px and `#c8321f` 3px on top; land with `#1f5fc4` 3px and `stroke-dasharray:6 4`; flight with `#f2d891` 3px, `stroke-dasharray:.1 5`, `linecap:round`; invented with `#c9b8e8` 3px and `stroke-dasharray:8 3 2 3`.
- Sharp corners left on the routes (`d2-itaca` at x=735 y=178, `d2-sicilia` at x=977 y=430): on the legs that fell back to the reserve tolerance, apply 2 more Chaikin passes only on vertices with an angle > 30°, repeating the land test and undoing the pass if it fails.

## Work order

1, 2, 3, 4 first, in that order. Then 6, which is the quickest, and 5, 7, 8. Before closing, photograph `flyTo(38.8,21.5,8.2)`, the comparison of 4 without pausing, `play` at 4.5 s, and the phone at rest and playing.
