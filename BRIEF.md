# Odyssey Map: brief

**User**: a Brazilian reading the Odyssey (the whole book, no spoiler protection). The whole interface is in English.

**The user's request**: "an interactive map where I can see all the places Odysseus went, all the islands. On today's map of Greece etc., where are these places. Where is Ithaca, where does Telemachus go, where is Odysseus heading, where each character went, Menelaus, Agamemnon. Each one's trajectory." Inspiration: **the Assassin's Creed Odyssey map**.

**AC Odyssey reference**: a full-screen game map, translucent grey-turquoise Aegean, land in a light parchment tone with painted relief, country and region names in spaced serif, gold diamond/hexagon icons, free zoom and drag, a thin dark HUD side panel, a detail card on click. It is an inspiration; do not copy logos or assets.

## Data is ready, do not change the facts
- `src/data.json`: `places` (coords, `certainty`: real|traditional|mythic, `desc`, `cantos`, `alts`, `parent` for the points inside Ithaca), `characters` (`stops` in chronological order, each with book, note, `time`, `ships`), `cantos` (24, with summary, places, characters). The books of the character Odysseus appear out of order on purpose: Books IX to XII are a flashback.
- `src/world.json`: `land.low` and `land.high` (polygons [lon,lat], format [[ring,...],...]; `high` is the detailed coast of the Ionian Islands only, lon 19.2-21.6, lat 37.3-39.9), `routes[charId]` = list of legs `{stop, mode: sea|land|air, km, pts:[[lon,lat]...]}` where `stop` is the index of the destination stop. The sea routes already steer around land. `relief.jpg` is a hillshade as a data URI, grey 128 = neutral, framed by `bbox` [lonW,latS,lonE,latN], with equirectangular projection. `bbox`=6.5,13,38.5,46.5.
- Projection: equirectangular, `x = lon*cos(37°)`, `y = -lat`. Simple and aligned with the relief.

## What the page must do
1. **Open useful**: a map of the whole Mediterranean with Odysseus's route drawn and numbered, and the main places labeled. Frame lat ~29.5-43, lon ~8-37; Ethiopia lies to the south and only shows when zooming out.
2. **Fluid zoom and drag**: mouse wheel, +/- buttons, pinch and touch drag, with enough zoom to see the points inside Ithaca (`parent: ithaca`, which only appear up close). Place names appear by zoom level and do not collide with each other.
3. **Choose a character**: a list with all 17, grouped: `main`, `returns`, `secondary`, `gods`. Several can be switched on to compare routes, each with its own color. Selecting one shows the route with numbered stops, approximate km (sum of `routes`) and a side itinerary in order. Clicking a stop flies to it.
4. **Voyage timeline**: a "play" button that animates the character's route stop by stop. For Odysseus, a ship counter (`ships`: 12, 1, 0).
5. **Browse by book**: a strip from I to XXIV. Clicking a book shows its title and summary, highlights its places (`places`) and characters (`chars`) and frames the map on them. This is how a reader knows "where am I". Suggested initial state: no book active.
6. **Place card**: clicking a pin opens the Homeric name, the modern name and country, `desc`, the books where it appears (clickable), the characters who pass there (clickable), and a **certainty seal**: Real place / Traditional identification / Mythic, no consensus. The `alts` appear as secondary pins joined by a thin line when the place is selected.
7. **Visual honesty**: real, traditional and mythic must differ in the shape of the pin, not just the color, with a visible legend. Routes: sea (solid line), land (dashes), a god's flight (dots, arc), `invented: true` (the Cretan lie, with its own treatment). The character's `order_note` must appear in the itinerary. Modern names of countries and seas as a discreet layer help: Greece, Turkey, Italy, Sicily, Crete, Egypt, Tunisia, Libya, Ionian Sea, Aegean Sea, Tyrrhenian Sea etc. The request is to see the places on today's map.
8. Simple **search** by place or character.

## Technical rules
- Output: `src/app.html` containing the `<title>` (`Odyssey Map`), the `<meta name="claude:viewport-fit-sides" content="cover">`, an inline `<style>` and `<script>`, with placeholders `/*__FONTS__*/` in the CSS, `const DATA=/*__DATA__*/;` and `const WORLD=/*__WORLD__*/;` in the JS. **No `<!doctype>`, `<html>`, `<head>` or `<body>`** (the page is wrapped on publishing), and no external resource at all: no network, no CDN. `python3 build/bundle.py` produces `build/index.html`.
- To test locally, `build/index.html` opens directly: `node tools/shot.js shots/name.png [--w 1440 --h 900] [--js "code"] [--wait ms] [--dark]`. The command prints `overflowX` and console errors. `require('playwright')` already works. Run with `NODE_PATH=$(npm root -g)` if needed.
- Expose `window.__map` with test methods: `selectCharacter(id)`, `selectPlace(id)`, `selectCanto(n)`, `flyTo(lat,lon,zoom)`, `play(id)`, so the designer can photograph states.
- Fonts: `npm i @fontsource/<name>` in `geo/` and list them in `src/fonts.json` (latin subset only, few weights; the bundle embeds them). Google Fonts does not load in this environment, which is why they are embedded. Do not use Inter or Space Grotesk.
- Rendering: canvas 2D for land and relief (Path2D, cached as a bitmap during the gesture), SVG or canvas on top for routes and pins. It must be fluid on a phone. Use `land.high` in place of `land.low` over the Ionian Islands when close in.
- A single-world identity (one deliberate theme): define `color-scheme` and all colors as tokens in `:root` and give `body` an explicit `background`. One-screen app: `height:100%` on html and body, never `100vh`. `:root` already receives safe-area padding.
- Phone (~400px): no horizontal scroll, the map fills the screen and the panels become a bottom drawer; 44px touch targets. Respect `prefers-reduced-motion`, visible keyboard focus. Devices without hover must not depend on hover.
- Do not use alert/confirm/prompt, nor localStorage outside try/catch.
- Interface text: plain, direct English, no cascades of dashes and no catchphrases.
