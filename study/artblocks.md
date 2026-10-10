# Art Blocks (artblocks.io)

Deep study 2026-10-01 (subagent session for the Generative Doodles study program).
Local only; nothing pushed.

## The platform as a machine

Art Blocks is a platform for scripted generative art, founded by Erick
Calderon (Snowfro), first mints late 2020. The core mechanic: an artist
deploys a JavaScript project; each mint derives its parameters from the
buyer's transaction hash; the script re-runs in the browser every time
anyone views the token. The work is the code; the image is a cache.

Tiers (from the Art Blocks artist FAQ and the late-2022 product update):
- **Curated**: curation-board reviewed, released in quarterly sets,
  applications rolling with roughly a 10% acceptance rate. The top
  standard of the platform.
- **Playground** (legacy): for artists already accepted into Curated, a
  place to experiment without full review.
- **Factory** (legacy): open to any artist meeting baseline technical and
  quality standards; the on-ramp for new names.
- Late 2022 consolidation: Factory and Playground were folded into
  **Art Blocks Presents**, plus **Explorations**, commissioned projects
  made with the Art Blocks team. Older projects keep a Heritage
  designation.

Token-page anatomy (observed on the Ringers #427 and Archetype #302 and
#552 token pages): each token lists **Attributes** with
collection-wide rarity percentages. These come from a feature script the
artist ships, which names the traits of each output. The page also has
toggles: "Show artwork in gallery frame" and "Enable live rendering",
which re-runs the generation live in the browser. The trait legend is
part of the art, not decoration around it.

The working method the platform encourages is worth stealing: Cherniak
generated a full 1,000-output set on the Rinkeby test network before
the mainnet release and examined the trait distribution across the whole
set before shipping it. Test the whole edition, not one seed.

## Ringers — Dmitri Cherniak (project #13, Curated, January 2021)

1,000 outputs, 0.1 ETH mint, sold out in about 18 to 20 minutes.
Outputs visually inspected at full resolution: #427, #275, #328.

Cherniak's premise, from his own site: "how many ways can a string wrap
around a set of pegs?" His own count math: a 4x4 grid of 16 pegs gives
65,519 possible peg selections (2^16 minus single pegs minus the empty
set), and that is before any string path is drawn.

Construction, as read from the pixels and his trait system:
1. Pegs laid on a grid (3x3, 4x4, 5x5 layouts).
2. A subset of pegs is selected (trait: peg count).
3. A string path wraps the selected pegs. Wrap style is Loop or Weave
   (over/under at crossings); wrap orientation is Balanced or
   Off-center; pegs can be Solid or Bullseye; peg scaling varies.
4. The path is stroked as a **wide round ribbon**. The ribbon is so wide
   that it reads as a filled silhouette, not a line: the hull of the
   wrap becomes the body of the piece.
5. Pegs are punched out as holes: discs in the background color with a
   thin dark outline, sitting inside the ribbon. Unwrapped pegs render as
   rings or solids on the ground.
6. Color: a body color (the ribbon), a background, and occasionally a
   rare extra-color flourish. #427 has a single yellow bullseye peg on a
   black-on-white piece; the signature yellow peg recurs across the
   series.

What the three inspected outputs showed:
- #427 (9 pegs, 3x3, Weave, Balanced): a thick black rounded-rectangle
  loop, bullseye peg holes punched inside it, two spare rings outside
  the ribbon, one yellow bullseye. Spare and dense in one frame.
- #275 (9 pegs, 4x4, Loop): a thin string loop instead of a ribbon, with
  the interior filled yellow on a beige ground. Same system, a
  completely different picture. This is the Loop/Weave parameter doing
  visible work.
- #328 (19 pegs, 5x5, Weave): an open zigzag ribbon, black on yellow,
  white peg holes punched along it. The string path does not have to
  close.

Cherniak's working statements, from his site and the Ringers in Motion
essay: automation is his medium; he designed the rules and their
limits, and the outputs reveal possibilities inside them. "Looking
across the collection is part of the work: its range becomes apparent
through the relationships between images." He released the whole system
as a complete series rather than cherry-picking favorites. And the
collection surprised him: Ringers #879 "The Goose" reads as a bird in
profile through pure chance, was parodied in The Simpsons, and sold at
Sotheby's in June 2023 for several million dollars. He sweeps
parameters as a practice: the LACMA Iterations piece is a nine-frame
sweep of peg sampling from 10% to 100% holding the signature yellow peg
constant.

## Archetype — Kjetil Golid (project #23, Curated, February 2021)

600 outputs. Outputs visually inspected at full resolution: #302 (Mural
palette, Flat scene, framed, Balance layout, Main coloring) and #552
(Cherfi palette, Bright Evening shading).

Construction:
1. An isometric tile packing of variable-size rectangles fills the
   frame edge to edge, with a thin dark frame line.
2. Each tile is extruded: the top face carries the tile color and two
   dark side faces give it block depth. The extrusion is the whole depth
   read; there is no other shading.
3. Coloring strategies (Main, Group, Random) decide how the palette is
   distributed; shading variants (Noon, Morning, Bright Evening)
   control the mood through the side-face darkness; layouts (Balance
   and others) control the packing.
4. Palettes are committed: Mural (green/yellow/red/blue/pink), Cherfi
   (mint/cream/gold/red/salmon), Verena, Warm Duo.

Golid's statement, from the token page: repetition is the counterweight
to unruly, random structures. One dumb module, repeated under tight
rules, with color doing the variation. Golid co-founded
generativeartistry.com, the long-running generative-art tutorials site;
the hop leads there.

## Fidenza and Meridian (covered by earlier deep studies)

- **Fidenza** (Tyler Hobbs, project #78, Curated, June 2021): 999
  outputs, 0.17 ETH mint, sold out in about 28 minutes. Visually
  studied in study/tyler-hobbs.md (4 outputs inspected). The Hobbs
  lineage was already absorbed from his site, interviews, and his own
  QQL-era essays.
- **Meridian** (Matt DesLauriers, project #28, Curated, June 2021):
  1,000 outputs. Visually studied in study/matt-deslauriers.md (3
  outputs plus a FOLIO output inspected; his tiny-artblocks repo read
  in full).

Both studies hold up; no need to re-inspect for this pass.

## What makes the flagship work sing

- A deliberately dumb premise, committed all the way: one string and
  some pegs; one block module repeated. The premise fits in a sentence;
  the range does not.
- Parameters that do visible work. Loop vs Weave is not a checkbox, it
  is the difference between a thin yellow loop and a black ribbon hull.
  Coloring strategy and shading variant are the difference between two
  Archetypes.
- The trait system makes every output legible as data. The piece ships
  with its own computed readout; the viewer learns the system's
  vocabulary by reading the legend.
- The collection is the unit, not the output. The outputs-wall view is
  where the range becomes visible, and collectors curate their own
  groupings. Design the system for the wall, not the hero piece.
- Stage the whole edition before release. The Rinkeby Sessions habit:
  generate the full set on a test network, read the trait distribution,
  then mint.

## Overdone (avoid-list additions)

- Peg-and-string wrap art with punched peg holes (Ringers owns it; the
  local re-render confirms it is a solved recipe).
- Edge-to-edge isometric extruded block fields in committed palettes
  (Archetype owns it).
- Hash-as-gimmick: randomness from a seed that has no visual
  consequence, and trait lists that decorate rather than describe.
- The complete-testnet staging habit is process, not a look; fine to
  adopt openly.

## Local re-render (technical study only, /tmp)

ringers_study.html: a 5x5 peg grid, a seeded subset of pegs, a
nearest-neighbor wrap tour, the tour stroked as a wide round ribbon in
ink, pegs punched as ground-colored holes with thin outlines, one
accent peg, unwrapped pegs as plain rings, and a simple over/under
weave at one crossing (the weave gap is crude; Cherniak's tangent
geometry is finer). The screenshot reads as the same species as the
three inspected Ringers: ribbon hull, punched peg holes, one accent.
Study confirmed: the wide ribbon plus punch-outs is the whole trick.

## Honest gaps

- The artblocks.io homepage fetch timed out (RECV_TIMEOUT); the study
  went through token pages, the media pipeline, and search. The
  homepage itself was not seen.
- The "Enable live rendering" toggle was not exercised; I studied the
  static renders, not the running script.
- No generator source code was read for Ringers or Archetype; the
  constructions above are read from pixels plus the artists' own
  descriptions.
- Square Symphony (okazz) was covered by its own deep study
  (study/okazz.md), not re-done here.
- Terraforms was dropped as a target: it is not an Art Blocks project
  (Mathcastles / Haver Studios).

## Doors onward

- Cherniak: dmitricherniak.com/works/ringers/ (trait math, the Rinkeby
  Sessions masterprint) and the Ringers in Motion essay (parameter
  sweeps as installation, anti-swastika safeguards, ~50 live scenes).
- Golid: generativeartistry.com tutorials; generated.space.
- The Presents and Explorations sets on Art Blocks for where the
  platform's curation went after the tier consolidation.
