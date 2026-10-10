# okazz_ (おかず / Okazz): Study Notes

**Profile:** x.com/okazz_ (not accessed, login wall) | **Key works:** Square
Symphony (Art Blocks, May 2023, fixed edition of 100, released with Bright
Moments Tokyo), KUMALEON (dynamic NFT project, minted Oct 2022), Resonant
Echo (Feral File, 65 artworks), Ephemeral Shapes (generative LED cube,
Tamagawa Takashimaya S.C.)

**Depth:** deep, two passes. Phase 1 (five artworks at full resolution, working
canvas re-render of the grid-in-grid construction). Phase 2 (2026-10-01):
systematic catalog of 20 of the 100 Square Symphony outputs (every 5th token,
54000000-54000095), trait space read off Verse, two layout modes confirmed
across the edition, plus two new visual families: Resonant Echo (Feral File,
light ground, Mondrian squares) and a dense interlace ribbon field (Bright
Moments press image). Contact sheet at /tmp/okazz2/contact_sheet.png. The X
feed itself was never accessed (login wall); that gap stands. The wustep/contraptions README cites an
okazz_ post as the direct inspiration for its grid of tiny looping machines
("Heavily inspired by Okazz"), which is the doorway this study entered
through.

## Who he is
A Japanese generative artist and creative coder working in p5.js, influenced
by anime and manga subculture. He works in editions (Art Blocks, Feral
File), character projects (KUMALEON), and public space (the LED cube piece).
His own description of Square Symphony: a grid structure inside of a grid,
inspired by "origins", his earliest memories of being an artist. Each piece
may seem simple, but within the eight motions it explores "joy" and
"comfort". Building blocks as autobiography.

## The core technique: a grid inside a grid
The construction, read off the pixels and confirmed by the re-render:

- A coarse master grid, roughly 20x20, on a dark ground (near-black in some
  seeds, deep navy in others).
- Every cell holds one miniature motif drawn from a small vocabulary:
  clock gauge (ring of 12 dots plus one hand), bullseye, checkerboard
  (2x2 up to 8x8), parallel wavy lines (5 to 7 colored sine lines), dot
  matrix, stacked bars, concentric ring pair, radial tick dial. Each motif
  is flat, unshaded, 1 to 2 colors, thick clean vector shapes.
- Some cells are empty. Negative space is part of the layout, roughly
  10 to 15 percent of cells.
- Hero merges: adjacent cells are fused into 2x2, 3x3, or 4x3 blocks
  holding one big simple shape (solid circle, checker block, bar stack,
  wave panel, dot field). Rare, maybe 5 percent of the area, and they
  carry the composition's hierarchy. This is the move that keeps a busy
  grid from reading as wallpaper.
- Cell frames are a parameter: some seeds draw a thin light border around
  every cell (the framed Verse editions), others are borderless (the press
  stills). Same system, different setting.
- Palette: 6 to 8 saturated candy colors (pink, cyan, yellow, red, blue,
  white, orange, teal, green) on the dark ground. Flat fills only, no
  gradients, no shadows, no texture. The restraint is in the rendering,
  not in the color count.

## The eight motions
The stills are frozen animation frames: clock hands sit at different angles
in different cells, which only makes sense if they turn. Each motif type
carries one parametric motion, and "eight motions" reads as the motion
vocabulary: hand rotation, wave phase scroll, bar length oscillation, dot
blink sequencing, checker color phase flip, dashed-ring rotation, ring
pulse, tick-dial rotation. Nothing travels between cells. Each cell is a
closed toy with its own loop, and the piece is the chorus. This is exactly
the architecture wustep cloned for contraptions: a grid of tiny machines,
each looping on its own.

## Second technique: the interlaced ribbon weave
A separate family, seen in one large piece: a square grid where each cell
holds an S-curve ribbon (two arcs), colored so the ribbons join into long
continuous meandering bands across the whole field, rendered with strict
over/under alternation at every crossing, like real weaving. Rounded tube
rendering, flat candy colors, no ground visible between bands. The subject
is the weave topology: band continuity plus the over/under rhythm. It reads
as a cousin of Truchet tiles but the motif is ribbons, not quarter arcs,
and the rendering problem is the interlace, not the tile pattern.

## Related projects (doorway hops)
- KUMALEON: character-based generative art (a bear) with a "be anything you
  want" concept. Owning a Square Symphony lets the holder transform their
  Kuma and update the NFT itself: a dynamic NFT. Less relevant technically,
  but it shows the same modular thinking (small combinable units) applied
  to character design.
- Async to Sync: a planned audio-visual generative collection with
  collaborators (hasaqui, ryota, Ara). Motion plus sound, same toy-box
  instinct extended in time.
- Ephemeral Shapes: LED cube public work in Futakotamagawa, walked through
  in the NEORT "BEYOND THE SCREEN" interview. The practice scales from a
  phone screen to architecture without changing its vocabulary.

## Palette and composition choices
Dark ground, candy brights, flat fills, geometric primitives, grid
discipline with deliberate breakage (heroes, empty cells, motifs that
slightly bleed their cell). The compositional signature is scale contrast:
tiny instruments against a few huge simple shapes. Everything aligns until
it doesn't, and the breakage is always rectangular (merged cells), never
freeform.

## What makes it sing
- The city-from-above rhythm. Each cell is a lit window with something
  moving inside it. The eye never rests but never gets lost, because the
  grid holds it.
- Scale contrast as the whole compositional strategy. Without the heroes
  this would be texture; with them it is a picture.
- Flat color discipline. No gradients means every color choice is load
  bearing, and the candy palette stays joyful instead of tipping into
  neon kitsch because the dark ground absorbs the excess.
- Motion as the medium. The stills are good, but the work is the eight
  loops running at once. A still is a specimen; the piece is an aquarium.
- Toy vocabulary. Gauges, checkers, dots, waves: every motif reads in
  under a second, so the complexity budget goes to the chorus, not to any
  single cell.

## Phase 2: the Square Symphony edition catalog (2026-10-01)

Contract 0x0a1bbd57033f57e7b6743621b79fcb9eb2ce3676, Ethereum ERC-721, tokens
54000000-54000099. Released May 2, 2023 with Bright Moments (Tokyo); fixed
edition of 100. Art Blocks collection page confirms the collaboration and
date. Downloaded every 5th token (00, 05, ... 95), 20 outputs, static PNG
captures via the media-proxy.

### The trait space (read off Verse token pages)
Five named traits, the edition's real parameter axes:
- **Background**: Black, navy, and others observed across the 20 (near-black
  in most, deep navy in several).
- **ColorPalette**: named palettes, "Seaside" seen on #24 and #62; more exist.
- **Grid**: True/False. The single biggest compositional switch.
- **Offset**: True/False. A half-cell shift of the layout.
- **Speed**: Slow/Middle (observed), presumably Fast exists. The work is
  ANIMATED; the PNGs are frozen frames. Clock hands sit at different angles
  in different cells, which only makes sense as motion. Any study that treats
  these as stills is studying the specimen, not the aquarium.

### Two layout modes, confirmed across the edition
- **Grid=True: the framed dense panel.** The phase-1 construction holds:
  ~20x20 master grid, thin light cell borders, 10-15% empty cells, hero
  merges (2x2 up to 4x3) carrying large simple shapes. Reads as circuit board
  / city from above.
- **Grid=False: the night sky.** No cell borders, no visible alignment grid.
  15-25 discrete motifs float on the dark ground at varied scales with wide
  negative space between them, plus 2-3 large hero motifs. Same vocabulary,
  completely different mood. Token 30 is a hybrid: grid bands top and bottom
  with an open navy zone in the middle holding floating heroes.
- The Bright Moments press stills (54000006, 54000011) are night-sky-mode
  outputs on black.

### Motif vocabulary, expanded (10+ types observed)
Dotted timer rings (12 dots plus a hand, his signature), checker grids
(2x2 up to 8x8), stacked horizontal bars, vertical bar pairs, wave bands
(5-7 colored sine lines), confetti dot clusters, concentric bullseyes, mini
dot matrices, striped blocks, small crosshatch squares. Two motifs recur as
personal glyphs across the edition: a pink/purple **double-bar** (present in
almost every output) and a white **triple-bar stack**. Everything flat,
unshaded, 1-2 colors per motif, thick clean vector shapes.

### Third family: Resonant Echo (Feral File, "Patterns of Flow" exhibition)
Shown in the Feral File exhibition "Patterns of Flow" (Sept 25 - Oct 6,
2024), 65 artworks. Completely different lighting from Square Symphony:
- Near-white ground. First light-ground family observed.
- Mondrian palette only: red, blue, yellow, black, gray on white.
- Hundreds of squares, varying sizes, scattered in a vertical plume/column
  centered on the page, density highest in the middle.
- Thin connector lines join some near-neighbor squares: connective tissue,
  the "resonance" made visible.
- Squares, not circles: the particle shape is the constraint that makes it
  his and not generic particle art.

### Fourth family: dense interlace ribbon field
A Bright Moments quarterly press image (123866) shows another mode: S-curve
ribbon tiles edge to edge, no ground visible anywhere, rainbow candy colors
on dark. Confirms the phase-1 "interlaced ribbon weave" as a real family and
adds the all-over variant: at full density it reads as fabric, not pattern.

### Scene context
"Patterns of Flow" was curated by Shunsuke Takawo (founder of Processing
Community Japan, daily-coding practitioner) and framed around Hiroshi
Kawano, the pioneer of Japanese computer art. Okazz showed alongside
Senbaku, mole^3, ykxotks and others: the new generation of Japanese code
artists, exhibited in explicit lineage from Kawano. He is not an isolated
NFT artist; he sits inside a national scene with a history.

### In his own words (Bright Moments quarterly, May 2023)
- Works in p5.js; influenced by anime and manga subculture.
- "This grid structure inside of a grid goes back to my earliest memories
  of being an artist."
- "Each piece may seem simple, but within the eight motions, exploring
  'joy' and 'comfort'."
- "Returning to my 'origin' as an artist for a moment and looking back at
  what I have built up over the years was somewhat like being a little kid
  again building up the blocks."

### Phase-2 corrections to Phase 1
- The night-sky (Grid=False) mode was only seen in press stills in phase 1;
  it is a first-class edition mode, roughly as common as the framed grid.
- Speed is a trait: the work moves. Still captures understate it.
- No fxhash/Tezos presence found. Ethereum only (Art Blocks Engine, Verse).

## Phase 2: techniques to steal (additions)
- The Grid boolean: one flag choosing framed-panel vs night-sky from the
  same engine. Two moods, zero new code paths.
- Named trait axes as the edition's vocabulary: design 4-6 named parameters
  with named settings (not raw numbers) and the parameter space becomes the
  piece's identity.
- Personal glyphs: one or two tiny motifs repeated across a whole family
  (his double-bar) work like a potter's mark. A family with a recurring
  glyph reads as signed.
- Light-ground restraint: when the palette is limited to five colors
  (Mondrian set), the ground can go white and the work still holds.
- Square particles with connective lines: the "echo" family shows that
  neighbor-linking turns confetti into resonance. The line is the subject,
  not the dot.

## Phase 2: what NOT to do (additions)
- Do not treat his outputs as stills. If the piece has a motion vocabulary,
  the study notes must say what moves.
- Do not copy the double-bar glyph itself. The potter's-mark move is free;
  his mark is not.

## Techniques to steal (not copy)
- Nested grid with hero merges: lay a strict grid, then fuse a few cell
  blocks into large simple shapes. Instant hierarchy in any grid piece.
- Motif vocabulary crossed with motion vocabulary as two independent
  axes: N small drawings times M small motions gives a large space from
  tiny parts. Design the axes separately.
- Cell frames as a parameter: the same layout reads as circuit board
  (framed) or night sky (borderless). One boolean, two moods.
- Negative-space cells as rests: leave a fixed fraction of cells empty
  so the busy ones can be busy.
- Over/under ribbon rendering on a tile grid: the weave alternation is
  a small amount of code and it completely changes the read from
  "pattern" to "fabric".

## What NOT to do (avoid-list additions)
- Do not ship a grid-of-tiny-machines piece in candy colors on dark. That
  family is taken twice over: okazz_ owns it, wustep cloned it, and №9032
  already holds our adjacent seat. Anything in this exact space needs a
  different subject (instruments, not machines), a different ground, or a
  different motion logic.
- Do not copy the clock-gauge motif. The ring of 12 dots plus one hand is
  his signature the way a brushstroke is a painter's. It is recognizable
  at thumbnail size.
- Do not confuse busy with rich. His density works because every motif is
  trivially readable. A grid of complicated cells is just noise.
- The full candy palette on dark is his lighting setup. Borrow the
  flatness and the discipline, not the exact colors.
