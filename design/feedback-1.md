# Design feedback, round 1

Screenshots in `shots/d1-*.png`. Base: desktop 1440x900 and phone 400x800. Lines cited are from `src/app.html` in this version.

## 1. Grade: 3.0 / 5

| Criterion | Grade | In one sentence |
|---|---|---|
| Visual identity and fidelity to the reference | 3.5 | Palette, pins and the gold HUD get the mood right. The staircase routes and the blotchy relief take away the painted-map feel. |
| Map legibility | 2.5 | Sicily, Campania and Ithaca turn into knots of pills, loose labels and overlapping lines. |
| Hierarchy and typography | 3.0 | Good fonts, but Ithaca does not stand out and the text over the map is harsh. The interface weighs more than the map. |
| Usability and clarity of interaction | 3.5 | Itinerary, flying to a stop and playback work. The book shows the wrong route and comparing does not say which color is who. |
| Phone | 2.5 | The drawer works. The initial framing, the giant numbers and the swapped labels get in the way. |

At-a-glance answers today:
- **Where is Ithaca?** Only by searching. The label sits 20px from the pin, looks like it names Cephalonia, and the pin is the size of any other.
- **Where does Telemachus go?** A good answer after the click (`d1-int-telemaco-click`), but with subway lines.
- **Where did Odysseus pass?** The general shape is visible. The order is unreadable in Sicily and Campania.

## 2. What works (preserve)

- Single theme: black and gold panel, GFS Didot in titles, spaced Cormorant SC in callouts, Alegreya in body text. Do not change the fonts.
- The three pin shapes (diamond, hexagon, dashed circle with "?"). Honest and distinct.
- The book strip with a diamond mark on the books of the selected place, and the certainty seal on the card.
- The itinerary: numbered vertical line, `order_note`, following the current stop during playback.
- The "Invented voyage" banner and the lilac dash-dot line in `d1-mentira`. It is the most beautiful state in the project.
- Ship counter with icons in the playback bar.
- The shallow-water rings around the coast: they are the visual signature of the map (just adjust them, see item 7).
- `alts` joined by a thin dotted line (`d1-lestrigoes`).

## 3. Prioritized fixes

### P0

**1. Staircase routes look like subway lines** · `d1-sicilia`, `d1-itaca`, `d1-int-telemaco-click`, `d1-crop-seam`

Problem: `routes[].pts` comes from a 0.025° grid, so there are horizontal straights and 45°/90° corners in the middle of the sea (the 450px horizontal in `d1-sicilia`). It is the biggest "algorithm-generated" look factor. Instruction, once at load, where `seg.xy` is built, without changing `world.json`:
1. On each `mode:'sea'` leg, simplify with Douglas-Peucker, tolerance 0.10° in projected x and y, keeping the first and last point.
2. Apply Chaikin, 3 iterations, keeping the endpoints.
3. Test each new point against `land.high` (inside HB) or `land.low` with point-in-polygon. If any falls on land, redo the leg with tolerance 0.04° and, if it still falls, 0.015°. This protects the Strait of Messina.
4. Recompute `seg.cum` and `seg.total`, but always show the km from `routes[].km`. `land` and `air` legs do not go through this.

Acceptance criterion: no long horizontal in `d1-sicilia`, and no route over land.

**2. Overlapping legs and arrows that look like a cursor** · `d1-sicilia`, `d1-tirreno`, `d1-crop-cluster`, `d1-mobile`

Problem: outbound and return pass through the same corridor at Messina and become one thick line with no direction. The white arrows with a black outline look like mouse pointers. Instruction in `projSeg`/`drawRoutes`:
- **Direction hand**: after projecting, shift each point along the normal to the right of the travel direction. `lane = 2.5px` for the focused character. With several active characters, add `character index in S.active × 3px`. Cap at 8px. This way opposite legs run in parallel.
- **Stroke**: 3px in the character's color, over a `rgba(255,248,230,.9)` casing of 5.5px, no black outline. For `air`, keep the dots.
- **Direction**: replace `chevrons()` with an unfilled "›": two 4px segments, `stroke:#fff8e6`, 1.5px, `lineCap:round`, centered on the line. `gap=150px`. No arrow within 30px of a pin.
- **Leg highlight**: on `mouseenter`/focus on an itinerary stop (tap on the phone), the leg arriving at it gets opacity 1 and 4px, and the other legs of the same person get opacity .3. The same while playback is paused. This answers "where did he pass" inside the Sicily knot.

**3. Numbered pills collide and hide numbers** · `d1-crop-cluster`, `d1-inicial`, `d1-mobile`, `d1-comparar2`

Problem: "10-12" covers another, "6-8" is under "15", "7" is cut by the Ithaca pin and there is no link between number and pin. On the phone, with 19px pills for 23px pins on a smaller screen, the Sicily knot is illegible. Instruction:
- Size (`.bdg`, line 66): height 17px, font 700 10.5px, 1px cream border, on desktop and phone. Today they are 19px and 11.5px, and 38px wide for "19–22".
- Collision: include the pills in the same collision loop as labels and pins. Test 8 positions at 20px from the pin center (E, NE, N, NW, W, SW, S, SE). If the chosen position is not the adjacent one, draw a 1px wire in the character's color to the pin.
- Grouping: at zoom < 7, pins of the same character less than 34px apart on screen become a single pill with the ranges joined, for example "9-13" in Campania and "5·6-8·14-16" in Sicily. Clicking it calls `fitPts` on those pins with enough `maxZ` to separate them.
- With compared characters, several pills at one place (Troy in `d1-egeu`) form a row flush against the pin, with no spacing, ordered as in `S.active`.

Acceptance criterion: no overlapping number in `d1-inicial` or `d1-mobile`.

**4. Ithaca cannot be found and labels come loose from pins** · `d1-crop-cluster`, `d1-m-telemaco`, `d1-mobile-lugar`, `d1-mobile`

Problems: on the initial phone view Ithaca has no label at all. In `d1-m-telemaco` the text "Sparta" sits under the Pylos pin, which means it gives wrong information. In `d1-mobile-lugar` "Paliki" steps on "Eumaeus's Hut" and the pills cover "Ithaca". Instruction:
- **Ithaca pin**: 32px visual (others 23px), same diamond, with an outer ring `rgba(242,216,145,.55)` of 2px at 5px distance and no animation at rest. Always visible at any zoom and drawn above the other pins.
- **Ithaca label**: `var(--f-display)` (GFS Didot) 19px, `letter-spacing:.04em`, top collision priority, always the first to be positioned, never hidden. The "Within sight of Ithaca" pin and its label only appear at zoom ≥ 7.5, unless the place is selected.
- **Priority order**: Ithaca, Troy, current playback stop, selected place, stops of the focused character, then the rest by importance. At zoom 6, Sparta, Pylos, Mycenae and Crete must appear, in this order. The long ones like "Telepylus of the Laestrygonians" only afterwards.
- **Anchor**: only 4 positions (E, W, N, S), with 3px between the visual edge of the pin and the text box. If none fits, hide the label. Never shift it far away.
- **Collision**: the test box must include `alts`, Ithaca's inner points and pills. The `parent: ithaca` points do not appear below zoom 10, including on the phone.
- **Appearance** (`.lbl`, line 60): replace the white with a black outline by ink with a halo: `color:#241708; font-weight:600; font-size:12.5px; text-shadow:0 0 1px #f6ecd0,0 0 2px #f6ecd0,0 0 3px #f6ecd0,0 0 5px rgba(246,236,208,.8)`. It looks more like a printed map and stops being jagged at DPR 1. Compare in `d1-inicial`. If it loses strength over the sea, raise the last radius to 6px and do not go back to white.

**5. The interface takes up almost half the screen** · `d1-inicial`, `d1-int-play-9000`, `d1-lestrigoes`

Problem: a 342px panel, a 70px legend plus 55px books stacked, 44px buttons and a 380px card. The map is left with about 700x720 when there is a card. Gods and secondary characters fall below the fold (`GODS` at y=1046 in a 900 window). This is where the project looks like a dashboard. Instruction for desktop (≥ 761px):
- `--panelW:300px`, background `rgba(14,12,9,.84)` with the current blur.
- **Header**: one line, "Odyssey Map" at 24px, without the subtitle or the ornament. Height 56px.
- **Character rows**: a single line, 36px high, `name` 15px, role to the right of the name at 12px `--muted` with an ellipsis, count only as a number at 12px at the end. "Hide all routes" moves up to the tabs line, at 12px. Group title 26px high. All 17 must fit without scrolling at 900px.
- **Single bottom strip**: merge legend and books into one 68px block, from `left:panelW+16` to `right:16`. On top, the legend in a 28px line, 12px, without the "PLACES"/"ROUTES" titles, separating the two groups with a vertical rule. Below, books at 40px, without the "BOOKS" cell. Background `rgba(14,12,9,.78)`.
- **Zoom**: + and − stuck together, 36x36, with the frame button 36x36 separated by 6px. Scale to the left of them, not touching the strip.
- **During playback**: hide the legend line and shrink the playback bar to 520px, attached above the books.
- **Framing**: `viewFor`, `fitPts`, `flyTo` and the place focus must compute the center from the free rectangle: `left=panelW+24`, `right=` width of the open card `+24`, `bottom=68+16+24`, `top=24`. In `d1-lestrigoes` "Scylla and Charybdis" is cut by the card because this does not happen.
- **Initial state**: Odysseus appears with a route but the Itinerary tab is dimmed, which looks like a bug. Start with `S.focus='odysseus'` without switching tabs, and the Itinerary tab enabled.

**6. The book does not show the book's voyage** · `d1-canto3`, `d1-canto9`, `d1-mobile-canto`

Problem: in Book III the title is "Telemachus at Pylos", but the screen shows Odysseus's faded route (who is not in the book) and none for Telemachus. The 16 pins have the same weight. The pills and faded routes look like stains. Instruction in `selectCanto` and `drawRoutes`:
- With a book active, ignore `S.active` when drawing. Draw only the legs whose destination has `stop.cantos` containing `n`, for each character of `canto.chars`.
- The first of `canto.chars` is the protagonist: 3px, opacity 1, with pills. The others: 1.5px, opacity .55, no pills, no arrows.
- Routes outside the book: do not draw. Remove the "ghost" state. Pins outside the book: opacity .35 and no halo. Pills outside the book: hidden.
- `places[0]` of the book gets a pin 1.3x larger and a 14px label. Frame by the protagonist's leg points when they exist, and by `places` otherwise.
- When closing the book, restore `S.active` as it was.

### P1

**7. Blotchy relief and the coast up close** · `d1-sicilia`, `d1-itaca`, `d1-int-telemaco-click`, `d1-crop-seam`, `d1-inicial`

Problems: the enlarged hillshade turns into brown blurs, and at zoom 6 it streaks Turkey and the Balkans. `land.high` has a polygonal coast, and there is a visible rectangle in Greece (a thread at lon 21.6 and lat 39.9). Instruction in `drawTerrain` (line ~644):
- Relief: `globalAlpha = lerp(.6, .28, (zoom-6)/3)` with clamp, and `globalCompositeOperation='multiply'`. It reduces the streaks at z6 and almost removes the blurs at z9.
- Paper grain: generate on a 256x256 canvas a monochrome noise with alpha 0 to .07 and fill the land with `createPattern`, multiply, after the relief. Skip when `fast` is true.
- Coast: `buildLand(WORLD.land.high,HB,true)` on line 492, with one smoothing pass.
- Seam: in `eachLand`, shrink the `LOW` hole by 1 screen px: `c.rect(HX0+1/k,HY0+1/k,HX1-HX0-2/k,HY1-HY0-2/k)`. This way the areas overlap and the thread disappears.
- Islets: in the rings, reduce the 34px one to alpha .06 and the 20px one to .09. It eliminates the target effect on tiny islands (`d1-sicilia`, x=400 y=378) without losing the signature.

**8. Visible end of the world and wasted opening on the phone** · `d1-int-zoomout`, `d1-egito-longe`, `d1-mobile`

Problem: when zooming out, the land ends in a blurred sea-colored rectangle. On the phone this shows up already at the opening (a strip at the top), and the bottom third is empty Sahara. Instruction:
- Fog (line ~684): change from `rgba(93,146,152,*)` to `#1c2a2d`, with `fw=2.6`, and paint the background outside the `bbox` with the same color. It reads as "outside the known map", like game fog, instead of a fake ocean.
- Limit the pan: if the visible height in degrees is smaller than the `bbox`, lock the center so it does not go past lat 46.5 at the top nor lat 13 at the bottom.
- Minimum zoom: the one that makes the `bbox` fit the free height, around 5.1 on desktop. Do not leave more than 15% of area outside the `bbox` in width.
- Initial framing on the phone: instead of lat 29.5-43 and lon 8-37, use lon 10-30 and lat 32.5-42 with `top=70` and `bottom` of the dock. Ithaca, Troy and Sicily stay on screen, without Sahara taking up 300px. Ethiopia remains reachable by zooming.

**9. Country and sea names cut off and under the routes** · `d1-inicial`, `d1-ulisses`, `d1-mentira`, `d1-sicilia`

Problem: names such as "A R D I N I A" (Sardinia) are cut by the panel. "AEGEAN SEA" vanishes under the islands. Routes cross "IONIAN SEA" and "MEDITERRANEAN SEA". "GREECE" collides with Scheria. Instruction:
- Test the whole box against the free rectangle from item 5: if it does not fit whole, hide it. Never show a name halfway.
- Collision with pins, labels, pills and the points of the active routes (sampled every 20px): test the default position and 3 more shifts of 40px. If all collide, opacity 0.
- Color: land `rgba(74,52,26,.62)`; sea `rgba(236,248,246,.62)`. Keep spaced Cormorant SC on both, no italics (not embedded).
- `AEGEAN SEA`: move the anchor to the north, about lat 39.2, lon 24.9, where there is clean water.
- `SICILY` and other islands: only at zoom ≥ 7.3, so as not to hit "Land of the Cyclopes" (`d1-tirreno`).

**10. Comparing does not identify who is who** · `d1-comparar2`, `d1-comparar2-itaca`, `d1-egeu`

Problem: nothing on the map says the green line is Agamemnon, and the blue almost vanishes into the sea. The ring that links a route is not self-explanatory: clicking the line swaps the set and changes tab, clicking the ring adds. Instruction:
- **Route tag**: at the last stop of each active character when there are 2 or more active, a tag with the name: background in the color, 11px, 600, height 18px, text color `tc`. It enters collision with priority just below Ithaca.
- **Colors** (line 386): `telemachus:#1f5fc4`, `menelaus:#7a3fc0`, `agamemnon:#0c7d5c`, `odysseus:#c8321f`. Distinguish close pairs: `diomedes:#0e8fa8`, `idomeneus:#4b4fb8`, `orestes:#c43a7e`, `neoptolemus:#e0589a`. With the cream casing from item 2, all stand out on sea and land. Athena/Hermes/Poseidon stay light, but for these use casing `rgba(20,14,8,.75)`.
- **Fixed hint**: above the first group, at 12px `--parch-dim`: "Tap the name to open the itinerary. Tap the circle to compare." When 2 or more are on, replace with "Comparing N routes · Hide all".
- **Ring**: 18px visual, and a 44x36 target in the new row from item 5. On hover, fill 30% with the color.

**11. The playback camera loses the map** · `d1-play`, `d1-int-play-9000`

Problem: the camera oscillates between zoom 8.2, 9.14, 6.86 and 7.03. At the start only Troy is visible and, because of that, the direction of travel is lost. Instruction:
- On start, 800ms at the full framing of the route, with the whole route visible at opacity .22 as a trail. The traveled part grows on top, at opacity 1.
- Camera: frame the origin and destination of the leg with the free rectangle, `maxZ=7.6`, unless both points are `parent:ithaca`. If the next leg already fits at the current zoom, only pan, without changing the zoom.
- Ship marker at the tip: a 12px bow triangle, in the character's color, with cream casing, instead of just the advance of the stroke. The destination label appears with high priority during arrival.

**12. Phone drawer** · `d1-m-personagens`, `d1-m-telemaco`, `d1-mobile-ulisses`, `d1-mobile-lugar`, `d1-mobile`

- Remove the search field from the Characters and Itinerary tabs on the phone, since "Search" is in the dock. It gains 70px.
- Itinerary: open at 50% of the height, with the first stop visible. Show the description (`summary`) only under "see more" and put at the top the name, 3 metrics and Play in a compact column (50px high for the metrics).
- Dock: `letter-spacing:.06em`, 11px, so "CHARACTERS" does not touch the edge.
- Place card: 50% of the height with the handle to expand, `max-height:50%` on opening. In `d1-mobile-lugar`, 66% hides almost all the context. Frame with `bottom` equal to the card height, as in item 5.
- Title "Odyssey Map": disappear when a drawer is open, since it covers pins and part of the map (`d1-mobile-lugar`). When closed, reduce to 15px, with a .7 background.
- Controls: on touch, only + and − together, 44px each. Move "frame" beside − horizontally if it takes up less height.
- Bottom fade of 24px on every scrollable area (place card, Book III) to indicate there is more content; in `d1-canto3` the next-book buttons are hidden with no warning at all. On desktop, in the book card, 30px-high chips, not 40px.

## Outside the list, non-blocking

- Search shows two "×" (native and custom): `input[type=search]::-webkit-search-cancel-button{display:none}`.
- "12 ships" repeated on every itinerary stop: show only when the number changes.
- `build/index.html` has no viewport meta, which is expected because publishing wraps the page. A phone test with `isMobile:true` falls into the desktop layout. Use `--w 400 --h 800 --touch`.

## Suggested work order

Items 1, 2 and 3 together, because collision depends on geometry. Then 4, 5 and 6. Re-photograph `d1-inicial`, `d1-sicilia`, `d1-itaca`, `d1-canto3` and `d1-mobile` before moving on to the P1s.
