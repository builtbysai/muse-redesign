# muse-redesign

The MUSE reading room: a quiet, scholarly digital reading room for the 229
study notes in `builtbysai/muse`. Ten hand-curated shelves, catalogue cards,
live search with deep links, per-note pages with shelf navigation. Static,
stdlib-only, no CDN, no frameworks. The notes are the heroes.

## Build

```sh
python3 build_index.py   # reads study/, writes site/
```

`build_index.py` is stdlib only. It parses the 229 notes and pre-renders:

- `site/index.html` — the reading room: search, shelf filters, cards
- `site/notes/*.html` — one page per note, with catalogue, drop caps,
  prev/next shelf navigation
- `site/before.html` — plain unstyled list (the "before" baseline)

Everything is inlined; the site works from `file://` with no network access.

## Design (v3)

Non-paper by decision. Cool gallery-white surfaces (`#fbfbfa`), neutral ink,
hairline rules, one oxide-red accent (`#8c3b2e`: the red of sanguine chalk
and printers' ink). The system serif for long-form reading, drop caps on
real prose, minimal chrome. It should feel like a museum print room: calm,
precise, and out of the way of the scholarship.

## Layout

- `build_index.py` — the generator
- `study/` — the 229 notes, vendored from `builtbysai/muse` (data; never rewritten)
- `site/` — generated output; the `gh-pages` branch carries a copy of
  this directory at its root for GitHub Pages

## Deploy

The site is served from the `gh-pages` branch
(https://builtbysai.com/muse-redesign/). After merging to `main`,
rebuild and push `site/` to `gh-pages`.
