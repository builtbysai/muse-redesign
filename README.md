# muse-redesign

The MUSE research index: a working index of the 229 study notes in
`builtbysai/muse`. Filed by what you can do with a note (stealable
techniques, avoid-list traps, palettes, open doorways, honest gaps), not by
subject shelves. Dark, digital-native, fully static. No trackers, no fonts
fetched, no CDN.

## Build

```sh
python3 build_site.py   # reads study/, writes site/
```

`build_site.py` is stdlib only. It keeps the hand-curated theme filing,
cross-cuts every note's sections by function, and renders:

- `index.html` — the index: instant search, theme + contains filters, sort
- `techniques.html` / `avoid.html` / `palettes.html` / `doorways.html` /
  `gaps.html` — aggregate views across all 229 notes
- `notes/*.html` — one page per note, with spec sheet, section TOC,
  related notes, prev/next

## Layout

- `build_site.py` — the generator
- `study/` — the 229 notes, vendored from `builtbysai/muse`
- `site/` — generated output; the `gh-pages` branch carries a copy of
  this directory at its root for GitHub Pages

## Deploy

The site is served from the `gh-pages` branch
(https://builtbysai.com/muse-redesign/). After merging to `main`,
rebuild and push `site/` to `gh-pages`.
