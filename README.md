# muse-redesign

Muse, a reading room: the 229 study notes in `builtbysai/muse` presented
as a quiet, scholarly digital reading room. Ten hand-curated shelves
(Print & the Etched Line, The First Programmers, Sound & Music Systems,
The Living Sketch, Light, Color & the Eye, Machines in Motion, Paint &
Sculpture, Text, Type & Concrete Poetry, The Playful Web, Scenes &
Gatherings), catalogue-style entries, per-note pages with prev/next, live
search with `?theme=` and `?q=` deep links.

v3 replaces the warm-paper v1 design with a cool porcelain/ink/Prussian-blue
visual system. v2 ("the research index", dark marketing framing) was
rejected by Hans as slop and removed.

## Build

```sh
python3 build_index.py   # reads study/, writes site/
```

`build_index.py` is stdlib only. It renders:

- `index.html` — the reading room: search, shelf filters, catalogue entries
- `notes/*.html` — one page per note, with catalogue block, prev/next
- `before.html` — plain unstyled list (the "before" baseline)

No CDN, no frameworks, no fetched fonts; everything is inlined, so the
site works from file://.

## Layout

- `build_index.py` — the generator
- `study/` — the 229 notes, vendored from `builtbysai/muse` (data, never rewritten)
- `site/` — generated output; the `gh-pages` branch carries a copy of
  `index.html`, `before.html`, and `notes/` at its root for GitHub Pages

## Deploy

The site is served from the `gh-pages` branch
(https://builtbysai.com/muse-redesign/). After merging to `main`,
rebuild and push the generated files to `gh-pages`.
