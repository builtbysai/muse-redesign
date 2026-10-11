#!/usr/bin/env python3
"""Build the Muse reading room (v3): the study notes as a quiet,
scholarly digital reading room.

Reads study/*.md and emits a self-contained static site:
  site/index.html          the reading room (search, shelves, catalogue)
  site/notes/<slug>.html   pre-rendered note pages
  site/before.html         plain unstyled list (the "before" baseline)

No dependencies beyond the standard library. Everything is inlined:
the site works from file:// with no network access.

v3 keeps the v1 architecture (shelves, catalogue entries, per-note pages,
prev/next, live search with ?theme= and ?q= deep links) and replaces the
warm-paper visual design with a cool, restrained reading-room design:
porcelain background, ink serif text, hairline rules, Prussian blue as the
single accent (a pigment with a genuine art-history lineage), system serif
for long-form reading and quiet sans small caps for apparatus.
No marketing language, no gamified counters, no em dashes, no emoji.
"""
import html
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.join(ROOT, "study")
OUT = os.path.join(ROOT, "site")
NOTES_OUT = os.path.join(OUT, "notes")

# ---------------------------------------------------------------- themes ---
THEMES = [
    ("print", "I", "Print & the Etched Line",
     "Four centuries of the etched line, from Rembrandt to Kollwitz. "
     "The revivalists, the poster artists, and the artist's own hand on the plate.",
     "#7a4a2b"),
    ("pioneers", "II", "The First Programmers",
     "Plotters, punch cards, and instruction sets. The people who taught "
     "computers to draw before it had a name.",
     "#3f5a7a"),
    ("sound", "III", "Sound & Music Systems",
     "Scores, tunings, and machines for listening. From Satie to SuperCollider, "
     "the note treated as a system.",
     "#5b6e3f"),
    ("creativecode", "IV", "The Living Sketch",
     "Contemporary sketchbooks in code. Flow fields, shaders, daily practice, "
     "and the open sketchbook era.",
     "#7a3f5c"),
    ("color", "V", "Light, Color & the Eye",
     "Light as material and the eye as instrument. Color systems, grids, "
     "fluorescence, and the science of seeing.",
     "#b07a1f"),
    ("kinetic", "VI", "Machines in Motion",
     "Sculpture that moves, draws, and answers back. Drawing machines, fog, "
     "and cybernetic contraptions.",
     "#4a6e6b"),
    ("painters", "VII", "Paint & Sculpture",
     "The older lineage. Painters and sculptors whose handling of line, crowd, "
     "and surface feeds everything else on these shelves.",
     "#6b4a5e"),
    ("text", "VIII", "Text, Type & Concrete Poetry",
     "Concrete poetry, typewriter grids, vector letterforms, and writing machines. "
     "Language arranged as image.",
     "#50586e"),
    ("webplay", "IX", "The Playful Web",
     "The browser as toy box. Single serving sites, drawing games, and "
     "interactive curiosities.",
     "#8c5a2e"),
    ("scenes", "X", "Scenes & Gatherings",
     "Exhibitions, festivals, galleries, and manifestos. The rooms where all "
     "of this met its public.",
     "#5e5648"),
]

SLUG_THEME = {
    "alfred-kubin": "print", "etching-revival-whistler-haden-meryon": "print",
    "felicien-rops": "print", "francisco-goya-etcher": "print",
    "hercules-segers": "print", "honore-daumier": "print",
    "jules-cheret": "print", "kathe-kollwitz-bauernkrieg": "print",
    "los-caprichos-serial": "print", "los-disparates": "print",
    "max-klinger": "print", "nabis-printmakers": "print",
    "odilon-redon": "print", "odilon-redon-second-sitting": "print",
    "otto-dix-der-krieg": "print", "rembrandt-etcher": "print",
    "rodolphe-bresdin": "print", "rops-diaboliques": "print",
    "seurat-cheret-borrowings": "print", "toulouse-lautrec-posters": "print",
    "weber-portfolio-1903": "print", "whistler-venice-sets": "print",
    "anni-albers": "print",
    "abraham-moles": "pioneers", "computer-technique-group": "pioneers",
    "darcy-thompson-on-growth-and-form": "pioneers", "elena-asins": "pioneers",
    "frieder-nake-georg-nees": "pioneers", "hanne-darboven": "pioneers",
    "harold-cohen-aaron": "pioneers", "herbert-franke": "pioneers",
    "hiroshi-kawano": "pioneers", "joan-shogren": "pioneers",
    "ken-knowlton-stan-vanderbeek-poemfields": "pioneers",
    "manuel-barbadillo": "pioneers", "max-bense": "pioneers",
    "michael-noll-bell-labs": "pioneers", "muriel-cooper": "pioneers",
    "on-kawara": "pioneers", "roman-verostko": "pioneers",
    "sol-lewitt": "pioneers", "vera-molnar": "pioneers",
    "zdenek-sykora": "pioneers",
    "algorave-tidalcycles": "sound", "atari-amy": "sound",
    "bespoke-synth-fubble-modulator": "sound", "chrome-music-lab": "sound",
    "diana-deutsch": "sound", "diana-deutsch-speech-to-song": "sound",
    "erik-satie": "sound", "erv-wilson-hexany": "sound",
    "hal-alles-machine": "sound", "james-tenney": "sound",
    "james-tenney-clang-1972": "sound", "james-tenney-quintext-1972": "sound",
    "james-tenney-spectral-canon": "sound",
    "james-tenney-tuning-theory": "sound", "jean-claude-risset": "sound",
    "john-cage": "sound", "john-pierce-inharmonic-timbres": "sound",
    "laurie-spiegel": "sound", "marc-sabat-three-tables-for-bob": "sound",
    "max-mathews-bell-labs": "sound", "morton-feldman": "sound",
    "patatap": "sound", "shepard-zajac-pair-of-paradoxes": "sound",
    "accumulation-motifs": "creativecode", "akella": "creativecode",
    "aljaz-francic": "creativecode", "anatoly-zenkov": "creativecode",
    "anders-hoff": "creativecode", "andreas-refsgaard": "creativecode",
    "anna-ridler": "creativecode", "artblocks": "creativecode",
    "attractor-flights": "creativecode", "awesome-canvas": "creativecode",
    "awwwards-webgl": "creativecode", "bit-101": "creativecode",
    "bjorn-karmann-paragraphica": "creativecode",
    "bruno-imbrizi-interactive-particles": "creativecode",
    "char-stiles": "creativecode", "codepen-revisits-20260920": "creativecode",
    "codrops-depth-gallery": "creativecode", "codrops-threejs": "creativecode",
    "darius-kazemi": "creativecode",
    "differential-growth-practice": "creativecode",
    "donkarlssonsan": "creativecode", "francis-tseng": "creativecode",
    "fxhash-slugs": "creativecode", "fyprocessing": "creativecode",
    "galleries-fxhash-openprocessing": "creativecode", "ge1doot": "creativecode",
    "gene-kogan": "creativecode", "generative-artistry": "creativecode",
    "genuary": "creativecode", "golan-levin": "creativecode",
    "gorillasun": "creativecode", "hakim-el-hattab": "creativecode",
    "ikeryou": "creativecode", "imgur-gallery-JEq3vGz": "creativecode",
    "inigo-quilez": "creativecode",
    "inspirationfeed-minimal-geometrics": "creativecode",
    "j2rgb-jonathan-shrake": "creativecode", "jackrugile": "creativecode",
    "jacob-stanton": "creativecode",
    "josh-on-design-canvas-deep-dive": "creativecode",
    "juhani-halkomaki": "creativecode", "junkiyoshi": "creativecode",
    "kaesve": "creativecode", "khalkeus": "creativecode",
    "kyle-mcdonald": "creativecode", "lammetje-nl": "creativecode",
    "libs-elliott": "creativecode", "mathemetica": "creativecode",
    "matt-deslauriers": "creativecode", "matt-richardson": "creativecode",
    "memo-akten": "creativecode", "meodai": "creativecode",
    "mherreshoff": "creativecode", "nasibovpng": "creativecode",
    "nature-of-code": "creativecode", "okazz": "creativecode",
    "olivia-jack-hydra": "creativecode",
    "philipp-schmitt-camera-restricta": "creativecode",
    "raven-kwok": "creativecode", "refik-anadol": "creativecode",
    "robert-hodgin": "creativecode", "sam-lavigne": "creativecode",
    "satoshi-aizawa": "creativecode", "scorch": "creativecode",
    "snowesamosc-viewyonder-takawo": "creativecode",
    "sofia-crespo": "creativecode", "tarick": "creativecode",
    "tenineight": "creativecode", "text-particle-practice": "creativecode",
    "theo-watson-design-io": "creativecode", "tksiiii": "creativecode",
    "tom-white": "creativecode", "turing-reaction-diffusion": "creativecode",
    "tyler-hobbs": "creativecode", "tyler-hobbs-site": "creativecode",
    "v3ga": "creativecode", "volorf": "creativecode",
    "watercolor-tyler-hobbs": "creativecode", "xdesro": "creativecode",
    "xordev": "creativecode", "yohei-nishitsuji": "creativecode",
    "yoichiro-kawaguchi": "creativecode",
    "youtube-colorful-coding-audio-visualizer": "creativecode",
    "youtube-weidi-zhang-image-data": "creativecode",
    "yuru-yura": "creativecode", "zach-lieberman": "creativecode",
    "ad-reinhardt": "color", "agnes-martin": "color",
    "bela-julesz-random-dot-stereograms": "color",
    "bjorn-ottosson-okhsl": "color", "dan-flavin": "color",
    "elastiq-albers": "color", "ellsworth-kelly": "color",
    "farbvelo": "color", "pro-color-harmonies": "color",
    "akira-kanayama": "kinetic", "billy-kluver-eat": "kinetic",
    "david-bowen": "kinetic", "edward-ihnatowicz-senster": "kinetic",
    "fujiko-nakaya": "kinetic", "gordon-pask-musicolour": "kinetic",
    "jean-dupuy": "kinetic", "jean-tinguely-homage": "kinetic",
    "jean-tinguely-metamatics": "kinetic", "jurg-lehni": "kinetic",
    "nicolas-schoffer-cysp1": "kinetic", "patrick-tresset": "kinetic",
    "piotr-kowalski": "kinetic", "sandy-noble-polargraph": "kinetic",
    "sougwen-chung": "kinetic", "takis": "kinetic",
    "wen-ying-tsai": "kinetic",
    "adam-and-eve-ensor-1887": "painters",
    "chaim-soutine-still-lifes": "painters",
    "jean-simeon-chardin": "painters", "giorgio-de-chirico": "painters",
    "giorgio-morandi": "painters", "goya-black-paintings": "painters",
    "philip-guston": "painters", "james-ensor": "painters",
    "james-lee-byars": "painters", "max-beckmann": "painters",
    "niki-de-saint-phalle": "painters", "paul-cezanne": "painters",
    "piero-della-francesca": "painters", "robert-ryman": "painters",
    "velazquez": "painters", "whistler-nocturnes": "painters",
    "francisco-zurbaran": "painters", "franz-von-lenbach": "painters",
    "franz-von-stuck": "painters", "franz-von-stuck-suende-versions": "painters",
    "villa-lenbach-villa-stuck": "painters",
    "ensor-seven-deadly-sins": "painters", "eva-hesse": "painters",
    "allison-parrish": "text", "dom-sylvester-houedard": "text",
    "hershey-fonts": "text", "leon-sans": "text",
    "poetry-camera": "text", "ross-goodwin": "text",
    "ruth-wolf-rehfeldt": "text",
    "blank-windows": "webplay", "bored-button": "webplay",
    "dan-macnish-draw-this": "webplay", "google-experiments": "webplay",
    "interactive-classics-batch-1": "webplay",
    "interactive-classics-batch-2": "webplay",
    "neal-agarwal-deep-sea": "webplay",
    "neal-agarwal-perfect-circle": "webplay",
    "species-in-pieces": "webplay", "staggering-beauty": "webplay",
    "the-useless-web": "webplay",
    "cavs-mit-circle": "scenes", "cybernetic-serendipity-1968": "scenes",
    "new-tendencies-t4-t5": "scenes", "robert-rehfeldt": "scenes",
    "signals-london": "scenes", "tgam": "scenes",
    "tgam-articles": "scenes", "tgam-artists": "scenes",
    "tgam-issues-01-04": "scenes", "tgam-issues-05-08": "scenes",
}

# Display-title overrides for stub/handle style notes.
TITLE_OVERRIDES = {
    "tksiiii": "tksiiii", "mathemetica": "mathemetica", "kaesve": "Kaesve",
    "tarick": "Tarick", "tenineight": "tenineight", "nasibovpng": "nasibovpng",
    "mherreshoff": "mherreshoff", "okazz": "okazz", "khalkeus": "khalkeus",
    "volorf": "volorf", "xdesro": "xdesro", "xordev": "xordev",
    "v3ga": "v3ga", "ikeryou": "ikeryou", "junkiyoshi": "JUNKIYOSHI",
    "ge1doot": "ge1doot", "akella": "akella", "meodai": "meodai",
    "donkarlssonsan": "donkarlssonsan",
    "hakim-el-hattab": "Hakim El Hattab",
    "fyprocessing": "FyProcessing",
    "j2rgb-jonathan-shrake": "J2RGB, Jonathan Shrake",
    "yuru-yura": "yuru yura",
    "imgur-gallery-JEq3vGz": "Procedural animation, an imgur gallery",
    "aljaz-francic": "Aljaz Francic",
    "scorch": "Scorch",
}

# ------------------------------------------------- tiny markdown renderer ---
INLINE_PATTERNS = [
    ("code", re.compile(r"`([^`]+)`")),
    ("link", re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")),
    ("bold", re.compile(r"\*\*([^*]+)\*\*")),
    ("italic", re.compile(r"(?<![*\w])\*([^*]+)\*(?![*\w])")),
]


def render_inline(text):
    """Render inline markdown to HTML, escaping raw text first."""
    out = []
    pos = 0
    spans = []
    for kind, pat in INLINE_PATTERNS:
        for m in pat.finditer(text):
            spans.append((m.start(), m.end(), kind, m))
    spans.sort(key=lambda s: (s[0], s[1]))
    kept = []
    last_end = -1
    for s in spans:  # drop overlapping spans; earlier/longer wins
        if s[0] >= last_end:
            kept.append(s)
            last_end = s[1]
    for start, end, kind, m in kept:
        out.append(html.escape(text[pos:start]))
        if kind == "code":
            out.append("<code>%s</code>" % html.escape(m.group(1)))
        elif kind == "link":
            label = render_inline(m.group(1))
            url = m.group(2)
            if url.startswith(("http://", "https://", "mailto:")):
                out.append('<a href="%s">%s</a>' % (html.escape(url, quote=True), label))
            else:
                out.append(label)
        elif kind == "bold":
            out.append("<strong>%s</strong>" % render_inline(m.group(1)))
        elif kind == "italic":
            out.append("<em>%s</em>" % render_inline(m.group(1)))
        pos = end
    out.append(html.escape(text[pos:]))
    return "".join(out)


def _split_table_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def render_markdown(src):
    """A small, forgiving markdown renderer. Handles the constructs the
    notes actually use: h1-h3, bold, italic, inline code, links, lists,
    code blocks, blockquotes, rules, and simple pipe tables."""
    lines = src.split("\n")
    out = []
    i = 0
    n = len(lines)

    def flush_paragraph(buf):
        if buf:
            text = " ".join(b.strip() for b in buf)
            if text:
                out.append("<p>%s</p>" % render_inline(text))

    para = []
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):  # fenced code block
            flush_paragraph(para)
            para = []
            lang = stripped[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = ' class="language-%s"' % html.escape(lang) if lang else ""
            out.append("<pre><code%s>%s</code></pre>"
                       % (cls, html.escape("\n".join(buf))))
            continue

        if stripped.startswith("|") and i + 1 < n and re.match(  # table
                r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]):
            flush_paragraph(para)
            para = []
            head = _split_table_row(stripped)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(_split_table_row(lines[i].strip()))
                i += 1
            t = ["<table><thead><tr>"]
            t += ["<th>%s</th>" % render_inline(c) for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(
                    "<td>%s</td>" % render_inline(c) for c in r) + "</tr>")
            t.append("</tbody></table>")
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", stripped)  # headings
        if m:
            flush_paragraph(para)
            para = []
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, render_inline(m.group(2)), level))
            i += 1
            continue

        if re.match(r"^(\*\*\*|---|___)\s*$", stripped):  # rule
            flush_paragraph(para)
            para = []
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):  # blockquote
            flush_paragraph(para)
            para = []
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote>%s</blockquote>" % render_inline(" ".join(buf)))
            continue

        m = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", line)  # lists
        if m:
            flush_paragraph(para)
            para = []
            ordered = bool(re.match(r"\d", m.group(2)))
            tag = "ol" if ordered else "ul"
            items = []
            base_indent = len(m.group(1))
            while i < n:
                lm = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", lines[i])
                if not lm or len(lm.group(1)) < base_indent:
                    break
                items.append(lm.group(3).strip())
                i += 1
            out.append("<%s>%s</%s>" % (
                tag, "".join("<li>%s</li>" % render_inline(x) for x in items), tag))
            continue

        if not stripped:  # blank line ends paragraph
            flush_paragraph(para)
            para = []
            i += 1
            continue

        para.append(line)
        i += 1
    flush_paragraph(para)
    return "\n".join(out)

# ------------------------------------------------------------ note parsing ---
TITLE_STRIP = [
    r" - Deep Study Notes$", r": Deep Study Notes$", r" - Study Notes$",
    r": Study Notes$", r" Study Notes$",
]


def clean_title(raw, slug):
    t = raw.strip()
    for pat in TITLE_STRIP:
        t = re.sub(pat, "", t)
    m = re.match(r"^(.*?):?\s*[Ss]tudy Notes\s*(\(.*\))$", t)
    if m:  # e.g. "jackrugile: Study Notes (deep, both pens)"
        t = (m.group(1) + " " + m.group(2)).strip()
        t = re.sub(r"\s*:\s*\(", " (", t)
    t = re.sub(r"\s+", " ", t).strip(" -:;,.")
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    return t


def split_catalogue(lines):
    """Pull the leading **Key:** metadata block out of the note body.

    Returns (catalogue_entries, remaining_lines). Only the block before the
    first heading or prose paragraph is taken; a bold lead-in that reads
    like a sentence is left in the body.
    """
    cat = []
    i = 0
    n = len(lines)
    while i < n and not lines[i].strip():
        i += 1
    while i < n:
        s = lines[i].strip()
        if not s or s.startswith("#"):
            break
        m = re.match(r"^\*\*([^*]+?)\*\*:?\s*(.*)$", s)
        if not m:
            break
        key = m.group(1).strip().rstrip(":.").strip()
        val_prefix = ""
        if ":" in key:  # e.g. **Depth: deep.**
            key, val_prefix = [p.strip().rstrip(".") for p in key.split(":", 1)]
        if len(key) > 28 or len(key.split()) > 3 or not re.match(
                r"^[A-Za-z][A-Za-z0-9 /-]*$", key):
            break  # reads like prose, not a label; stop the block
        val_lines = [p for p in [val_prefix, m.group(2)] if p]
        i += 1
        while i < n:  # wrapped continuation lines
            t = lines[i].strip()
            if not t:
                break
            if t.startswith(("#", ">", "-", "*", "|", "```")):
                break
            if re.match(r"^\*\*[^*]+\*\*", t) or re.match(r"^\d+[.)]\s", t):
                break
            val_lines.append(t)
            i += 1
        val = " ".join(v.strip() for v in val_lines if v.strip())
        if val:
            cat.append((key, val))
        while i < n and not lines[i].strip():
            i += 1
    return cat, lines[i:]


def first_paragraph_text(lines):
    """First real paragraph, skipping metadata bold lines and headings."""
    buf = []
    in_para = False
    for line in lines:
        s = line.strip()
        if s.startswith("#") or not s:
            if in_para and buf:
                break
            in_para = False
            continue
        if re.match(r"^\*\*[^*]+\*\*[:.]?\s*", s) and len(s) < 400 and not in_para:
            continue  # metadata line
        in_para = True
        buf.append(s)
        if len(" ".join(buf)) > 220:
            break
    text = " ".join(buf)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_note(path, slug):
    src = open(path, encoding="utf-8", errors="replace").read()
    lines = src.split("\n")
    title_idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
    raw_title = lines[title_idx]
    title = clean_title(raw_title.lstrip("# "), slug)
    catalogue, rest = split_catalogue(lines[title_idx + 1:])
    body_html = render_markdown("\n".join(rest))
    headings = " ".join(
        re.sub(r"^#{2,3}\s+", "", l).strip() for l in rest
        if re.match(r"^#{2,3}\s+", l.strip()))
    headings = re.sub(r"[*_`\[\]()]|\s+", " ", headings).strip()
    if catalogue:
        cat_html = "".join(
            "<dt>%s</dt><dd>%s</dd>" % (html.escape(k), render_inline(v))
            for k, v in catalogue)
        body_html = '<dl class="catalogue">%s</dl>\n%s' % (cat_html, body_html)
    words = len(re.findall(r"[A-Za-z0-9']+", src))
    excerpt = first_paragraph_text(rest)
    excerpt = re.sub(r"^Deep study,?\s*\d{4}-\d{2}-\d{2}\.?\s*", "", excerpt)
    excerpt = re.sub(r"^Deep study\.?\s*", "", excerpt)
    if len(excerpt) > 260:
        cut = excerpt[:260].rsplit(" ", 1)[0]
        excerpt = cut + "\u2026"
    m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", src[:3000])
    date = m.group(1) if m else ""
    theme = SLUG_THEME.get(slug)
    return {
        "slug": slug, "title": title, "words": words,
        "minutes": max(1, round(words / 200)),
        "excerpt": excerpt, "date": date, "theme": theme,
        "body_html": body_html, "headings": headings,
    }

# ------------------------------------------------------------------- css ----
# v3 design: a quiet, scholarly digital reading room.
# Porcelain background, ink serif text, hairline rules, Prussian blue as the
# single accent (a pigment with a genuine art-history lineage), system serif
# for long-form reading, quiet sans small caps for apparatus (kickers,
# colophon, metadata, labels). Catalogue rows instead of cards, shelves
# numbered like a library catalogue.
CSS = r"""
:root{
  --bg:#f7f8f7; --surface:#ffffff;
  --ink:#1a1e20; --ink-soft:#4b5254; --ink-faint:#8d9496;
  --rule:#dfe3e2; --rule-soft:#ecefec;
  --accent:#10406b; --accent-ink:#0c3255;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%; scroll-behavior:smooth}
body{
  margin:0; color:var(--ink); background:var(--bg);
  font-family:var(--serif); font-size:17px; line-height:1.65;
}
a{color:var(--accent); text-decoration-thickness:1px; text-underline-offset:3px}
a:hover{color:var(--accent-ink)}
::selection{background:rgba(16,64,107,.16)}
.wrap{max-width:1080px; margin:0 auto; padding:0 32px}
.smallcaps{font-family:var(--sans); text-transform:uppercase; letter-spacing:.14em; font-size:11.5px}

/* ---------- masthead ---------- */
.topline{height:3px; background:var(--accent)}
.masthead{padding:52px 0 30px}
.masthead .kicker{font-family:var(--sans); text-transform:uppercase; letter-spacing:.24em;
  font-size:11.5px; color:var(--ink-faint); margin:0 0 16px}
.masthead h1{font-size:clamp(52px,8vw,96px); line-height:1; margin:0; font-weight:500;
  letter-spacing:-.01em}
.masthead .sub{font-style:italic; color:var(--ink-soft); font-size:clamp(16px,2.2vw,20px);
  margin:16px 0 0; max-width:36em; line-height:1.6}
.colophon{display:flex; flex-wrap:wrap; gap:10px 26px; border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule); padding:13px 0; color:var(--ink-soft);
  font-family:var(--sans); font-size:12.5px}
.colophon .lbl{text-transform:uppercase; letter-spacing:.12em; font-size:10.5px;
  color:var(--ink-faint); margin-right:7px}

/* ---------- search & shelf filter ---------- */
.controls{padding:30px 0 4px; display:flex; flex-direction:column; gap:20px}
.searchrow{display:flex; gap:12px; align-items:stretch}
.searchbox{flex:1; position:relative; border-bottom:1px solid var(--ink-faint)}
.searchbox:focus-within{border-bottom-color:var(--accent)}
.searchbox svg{position:absolute; left:2px; top:50%; transform:translateY(-50%);
  width:17px; height:17px; stroke:var(--ink-faint); fill:none; stroke-width:2}
#q{width:100%; font-family:var(--serif); font-size:19px; font-style:italic; color:var(--ink);
  background:transparent; border:none; padding:10px 4px 10px 30px}
#q::placeholder{color:var(--ink-faint)}
#q:focus{outline:none}
#clearq{display:none; font-family:var(--sans); font-size:12px; background:none;
  border:1px solid var(--rule); color:var(--ink-soft); padding:0 16px; cursor:pointer}
#clearq:hover{border-color:var(--accent); color:var(--accent)}
.shelves{display:flex; flex-wrap:wrap; gap:4px 26px}
.chip{font-family:var(--sans); font-size:13px; cursor:pointer; background:none;
  border:none; border-bottom:2px solid transparent; color:var(--ink-soft);
  padding:7px 1px; display:inline-flex; align-items:center; gap:8px}
.chip .sw{width:8px; height:8px; flex:none; background:var(--sw,#888)}
.chip .n{color:var(--ink-faint); font-size:11.5px}
.chip:hover{color:var(--ink)}
.chip[aria-pressed="true"]{color:var(--ink); font-weight:600; border-bottom-color:var(--accent)}
.chip[aria-pressed="true"] .n{color:var(--ink-soft)}
.resultline{color:var(--ink-soft); font-style:italic; font-size:15px; margin:0; min-height:1.4em}

/* ---------- shelves & catalogue entries ---------- */
.theme{margin:52px 0 8px}
.theme-head{display:flex; align-items:baseline; gap:16px; border-bottom:1px solid var(--ink);
  padding-bottom:10px}
.theme-head .num{font-style:italic; color:var(--ink-faint); font-size:15px; min-width:2.2em}
.theme-head h2{margin:0; font-size:clamp(21px,2.8vw,27px); font-weight:600; letter-spacing:.005em}
.theme-head .count{margin-left:auto; font-family:var(--sans); font-size:11.5px;
  text-transform:uppercase; letter-spacing:.12em; color:var(--ink-faint); white-space:nowrap}
.theme .blurb{color:var(--ink-soft); font-style:italic; max-width:46em;
  margin:12px 0 6px; font-size:15.5px; line-height:1.6}
.card{border-top:1px solid var(--rule); padding:20px 6px 22px; display:block}
.card:last-child{border-bottom:1px solid var(--rule)}
.card:hover{background:var(--surface)}
.card h3{margin:0 0 6px; font-size:20.5px; line-height:1.32; font-weight:600}
.card h3 a{color:var(--ink); text-decoration:none}
.card h3 a:hover{color:var(--accent); text-decoration:underline;
  text-decoration-thickness:1px; text-underline-offset:3px}
.card .meta{font-family:var(--sans); font-size:11.5px; color:var(--ink-faint);
  text-transform:uppercase; letter-spacing:.1em; margin-bottom:8px;
  display:flex; align-items:center; gap:10px; flex-wrap:wrap}
.card .meta .sw{width:8px; height:8px; flex:none}
.card .meta .sep{color:var(--rule)}
.card .ex{color:var(--ink-soft); font-size:15.5px; line-height:1.62; margin:0; max-width:62em}
.empty{padding:70px 20px; text-align:center; color:var(--ink-soft); font-style:italic; display:none}
.empty.show{display:block}

/* ---------- note page ---------- */
.backline{border-bottom:1px solid var(--rule); padding:13px 0;
  font-family:var(--sans); font-size:12.5px}
.backline a{color:var(--ink-soft); text-decoration:none;
  text-transform:uppercase; letter-spacing:.12em; font-size:11.5px}
.backline a:hover{color:var(--accent)}
.note{max-width:700px; margin:0 auto; padding:46px 32px 20px}
.note .theme-tag{display:inline-flex; align-items:center; gap:9px;
  font-family:var(--sans); font-size:11.5px; text-transform:uppercase;
  letter-spacing:.14em; color:var(--ink-soft); margin-bottom:18px}
.note .theme-tag .sw{width:9px; height:9px}
.note h1{font-size:clamp(32px,4.8vw,50px); line-height:1.1; margin:0 0 10px;
  font-weight:600; letter-spacing:-.005em}
.note .byline{font-family:var(--sans); font-size:11.5px; color:var(--ink-faint);
  text-transform:uppercase; letter-spacing:.12em; border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule); padding:11px 0; margin-bottom:30px;
  display:flex; gap:14px; flex-wrap:wrap}
.note .byline .sep{color:var(--rule)}
.catalogue{display:grid; grid-template-columns:auto 1fr; gap:0 24px; margin:0 0 34px;
  border-top:1px solid var(--rule); font-size:15px; line-height:1.6}
.catalogue dt{font-family:var(--sans); font-size:10.5px; text-transform:uppercase;
  letter-spacing:.12em; color:var(--ink-faint); white-space:nowrap;
  padding:12px 0; border-bottom:1px solid var(--rule-soft)}
.catalogue dd{margin:0; color:var(--ink-soft); padding:12px 0;
  border-bottom:1px solid var(--rule-soft)}
.note-body{font-size:18.5px; line-height:1.74}
.note-body > p:first-of-type::first-letter{font-size:3.3em; float:left; line-height:.88;
  padding:5px 12px 0 0; font-weight:600; color:var(--accent)}
.note-body h2{font-size:23px; margin:2.1em 0 .6em; font-weight:600;
  border-bottom:1px solid var(--rule); padding-bottom:8px}
.note-body h3{font-size:19px; margin:1.7em 0 .5em; font-weight:600}
.note-body p{margin:0 0 1.15em}
.note-body ul,.note-body ol{margin:0 0 1.25em; padding-left:1.4em}
.note-body li{margin-bottom:.45em}
.note-body blockquote{border-left:2px solid var(--accent); margin:1.5em 0;
  padding:2px 0 2px 20px; font-style:italic; color:var(--ink-soft)}
.note-body pre{background:#22282c; color:#e8ecec; padding:16px 18px; overflow:auto;
  font-size:13.5px; line-height:1.6}
.note-body code{font-family:var(--mono); font-size:.84em}
.note-body p code,.note-body li code,.note-body td code{background:#e7ebe9;
  padding:1px 6px}
.note-body table{border-collapse:collapse; margin:1.5em 0; font-size:15px; width:100%}
.note-body th,.note-body td{border:1px solid var(--rule); padding:9px 11px; text-align:left}
.note-body th{font-family:var(--sans); font-size:11px; text-transform:uppercase;
  letter-spacing:.08em; color:var(--ink-soft); background:#eef1f0}
.note-body hr{border:none; border-top:1px solid var(--rule); margin:2.2em auto; width:33%}
.pagenav{display:grid; grid-template-columns:1fr 1fr; gap:20px;
  margin:52px 0 6px; border-top:1px solid var(--rule); padding-top:22px}
.pagenav a{text-decoration:none; color:var(--ink); display:block}
.pagenav a:hover .t{color:var(--accent); text-decoration:underline;
  text-underline-offset:3px}
.pagenav .dir{font-family:var(--sans); font-size:11px; text-transform:uppercase;
  letter-spacing:.14em; color:var(--ink-faint); display:block; margin-bottom:5px}
.pagenav .t{font-size:16.5px; font-weight:600; line-height:1.4}
.pagenav .next{text-align:right}

footer.site{border-top:1px solid var(--ink); margin-top:64px; padding:22px 0 70px;
  color:var(--ink-soft); font-family:var(--sans); font-size:12px}
footer.site .wrap{display:flex; flex-wrap:wrap; gap:8px 28px; justify-content:space-between}
footer.site .lbl{text-transform:uppercase; letter-spacing:.12em; font-size:10.5px;
  color:var(--ink-faint)}
@media (max-width:640px){
  .wrap{padding:0 20px}
  .note{padding:34px 20px 16px}
  .pagenav{grid-template-columns:1fr}
  .pagenav .next{text-align:left}
  .catalogue{grid-template-columns:1fr; gap:0}
  .catalogue dt{border-bottom:none; padding-bottom:0}
}
"""

# ------------------------------------------------------------------- js -----
INDEX_JS = r"""
(function(){
  var q = document.getElementById('q'),
      clearBtn = document.getElementById('clearq'),
      resultline = document.getElementById('resultline'),
      empty = document.getElementById('empty'),
      chips = Array.prototype.slice.call(document.querySelectorAll('.chip')),
      cards = Array.prototype.slice.call(document.querySelectorAll('.card')),
      sections = Array.prototype.slice.call(document.querySelectorAll('.theme')),
      activeTheme = 'all',
      total = cards.length;

  function norm(s){ return (s||'').toLowerCase(); }

  function apply(){
    var term = norm(q.value).trim(),
        terms = term.split(/\s+/).filter(Boolean),
        shown = 0;
    clearBtn.style.display = term ? 'inline-block' : 'none';
    cards.forEach(function(c){
      var okTheme = (activeTheme === 'all' || c.getAttribute('data-theme') === activeTheme),
          hay = norm(c.getAttribute('data-search')),
          okTerm = terms.every(function(t){ return hay.indexOf(t) !== -1; }),
          show = okTheme && okTerm;
      c.style.display = show ? '' : 'none';
      if (show) shown++;
    });
    sections.forEach(function(s){
      var any = Array.prototype.some.call(
        s.querySelectorAll('.card'), function(c){ return c.style.display !== 'none'; });
      s.style.display = any ? '' : 'none';
    });
    empty.classList.toggle('show', shown === 0);
    if (term || activeTheme !== 'all'){
      var what = shown + ' of ' + total + ' notes';
      if (activeTheme !== 'all'){
        var chip = document.querySelector('.chip[data-theme="' + activeTheme + '"]');
        what += ' on ' + chip.getAttribute('data-name');
      }
      if (term) what += ' matching \u201C' + q.value.trim() + '\u201D';
      resultline.textContent = what + '.';
    } else {
      resultline.textContent = '';
    }
  }

  var deb;
  q.addEventListener('input', function(){
    clearTimeout(deb); deb = setTimeout(apply, 120);
  });
  clearBtn.addEventListener('click', function(){ q.value=''; apply(); q.focus(); });
  chips.forEach(function(chip){
    chip.addEventListener('click', function(){
      activeTheme = chip.getAttribute('data-theme');
      chips.forEach(function(c){ c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      apply();
    });
  });
  var params = new URLSearchParams(location.search);
  if (params.get('theme')){
    var t = params.get('theme');
    var hit = chips.filter(function(c){ return c.getAttribute('data-theme') === t; })[0];
    if (hit) hit.click();
  }
  if (params.get('q')){ q.value = params.get('q'); apply(); }
})();
"""

SVG_SEARCH = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
              '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>')

# ------------------------------------------------------------- page builders -
def page_shell(title, body, css=CSS, js=""):
    return ("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n"
            "<script>%s</script>\n</body>\n</html>"
            % (html.escape(title), css, body, js))


def build_index(notes):
    by_theme = {t[0]: [] for t in THEMES}
    theme_names = {t[0]: t[2] for t in THEMES}
    for n in notes:
        by_theme[n["theme"]].append(n)
    for t in by_theme:
        by_theme[t].sort(key=lambda n: n["title"].lower())

    chips = ['<button class="chip" data-theme="all" data-name="every shelf" '
             'aria-pressed="true">All shelves <span class="n">%d</span></button>'
             % len(notes)]
    for tid, num, name, blurb, color in THEMES:
        chips.append(
            '<button class="chip" data-theme="%s" data-name="%s" aria-pressed="false" '
            'style="--sw:%s"><span class="sw"></span>%s. %s <span class="n">%d</span></button>'
            % (tid, html.escape(name), color, num, html.escape(name), len(by_theme[tid])))

    sections = []
    for tid, num, name, blurb, color in THEMES:
        cards = []
        for n in by_theme[tid]:
            meta_bits = []
            if n["date"]:
                meta_bits.append("studied " + n["date"])
            meta_bits.append("%d min read" % n["minutes"])
            search = " ".join(
                [n["title"], n["excerpt"], n["headings"], theme_names[n["theme"]],
                 n["date"]]).replace('"', "")
            cards.append(
                '<article class="card" data-theme="%s" data-search="%s">'
                '<h3><a href="notes/%s.html">%s</a></h3>'
                '<div class="meta"><span class="sw" style="background:%s"></span>'
                '<span>%s.</span><span class="sep">/</span><span>%s</span></div>'
                '<p class="ex">%s</p>'
                '</article>' % (
                    tid, html.escape(search, quote=True), n["slug"],
                    html.escape(n["title"]), color, num,
                    "</span><span class=\"sep\">/</span><span>".join(meta_bits),
                    html.escape(n["excerpt"])))
        sections.append(
            '<section class="theme" id="theme-%s">'
            '<div class="theme-head"><span class="num">%s.</span><h2>%s</h2>'
            '<span class="count">%d %s</span></div>'
            '<p class="blurb">%s</p>'
            '%s</section>' % (
                tid, num, html.escape(name), len(by_theme[tid]),
                "note" if len(by_theme[tid]) == 1 else "notes",
                html.escape(blurb), "".join(cards)))

    total_words = sum(n["words"] for n in notes)
    body = (
        '<div class="topline"></div>'
        '<header class="masthead"><div class="wrap">'
        '<p class="kicker">The study notes of Hans Sai</p>'
        '<h1>Muse</h1>'
        '<p class="sub">Two hundred twenty-nine research notes on art, '
        'printmaking, and the systems artists work with. Filed on ten shelves, '
        'kept for slow reading.</p>'
        '</div></header>'
        '<div class="wrap"><div class="colophon">'
        '<span><span class="lbl">Notes</span>%d</span>'
        '<span><span class="lbl">Words</span>%s</span>'
        '<span><span class="lbl">Shelves</span>10</span>'
        '<span><span class="lbl">Source</span>'
        '<a href="https://github.com/builtbysai/muse">builtbysai/muse</a></span>'
        '</div>'
        '<div class="controls">'
        '<div class="searchrow"><div class="searchbox">%s'
        '<input id="q" type="search" placeholder="Search titles, subjects, dates" '
        'aria-label="Search the notes" autocomplete="off"></div>'
        '<button id="clearq">Clear</button></div>'
        '<nav class="shelves" aria-label="Shelves">%s</nav>'
        '<p class="resultline" id="resultline" role="status"></p>'
        '</div>'
        '%s'
        '<div class="empty" id="empty">'
        '<p>Nothing on these shelves matches. Try a shorter word, or clear the '
        'search and browse instead.</p></div>'
        '</div>'
        '<footer class="site"><div class="wrap">'
        '<span><span class="lbl">Muse</span> a reading room. Generated from the '
        'study notes; no servers involved.</span>'
        '<span>Set in the system serif.</span>'
        '</div></footer>' % (
            len(notes), "{:,}".format(total_words), SVG_SEARCH, "".join(chips),
            "".join(sections)))
    return page_shell("Muse, a Reading Room", body, js=INDEX_JS)


def build_note_page(n, prev_n, next_n, theme_name, theme_num):
    def navlink(other, direction, cls):
        if not other:
            return ""
        return ('<a class="%s" href="%s.html"><span class="dir">%s</span>'
                '<span class="t">%s</span></a>'
                % (cls, other["slug"], direction, html.escape(other["title"])))

    meta_bits = ["%d min read" % n["minutes"],
                 "{:,} words".format(n["words"])]
    if n["date"]:
        meta_bits.insert(0, "studied " + n["date"])
    body = (
        '<div class="topline"></div>'
        '<div class="backline"><div class="wrap">'
        '<a href="../index.html">&larr; The reading room</a>'
        '</div></div>'
        '<article class="note">'
        '<span class="theme-tag"><span class="sw" style="background:%s"></span>'
        'Shelf %s, %s</span>'
        '<h1>%s</h1>'
        '<div class="byline"><span>%s</span></div>'
        '<div class="note-body">%s</div>'
        '<nav class="pagenav">%s%s</nav>'
        '</article>'
        '<footer class="site"><div class="wrap">'
        '<span><span class="lbl">Muse</span> a reading room.</span>'
        '<span><a href="../index.html">Back to the shelves</a></span>'
        '</div></footer>' % (
            dict((t[0], t[4]) for t in THEMES)[n["theme"]],
            theme_num, html.escape(theme_name), html.escape(n["title"]),
            "</span><span class=\"sep\">/</span><span>".join(meta_bits),
            n["body_html"],
            navlink(prev_n, "Previous note", ""),
            navlink(next_n, "Next note", "next")))
    return page_shell(n["title"] + " \u00b7 Muse", body)


def build_before(notes):
    items = "\n".join(
        "<li>%s</li>" % html.escape(n["title"]) for n in notes)
    return ("<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
            "<title>muse - study notes</title></head><body>"
            "<h1>muse - study notes</h1><ul>\n%s\n</ul></body></html>" % items)


def main():
    files = sorted(f for f in os.listdir(STUDY) if f.endswith(".md"))
    notes = []
    missing = []
    for f in files:
        slug = f[:-3]
        theme = SLUG_THEME.get(slug)
        if not theme:
            missing.append(slug)
            continue
        notes.append(parse_note(os.path.join(STUDY, f), slug))
    if missing:
        print("MISSING THEME:", ", ".join(missing))
        sys.exit(1)
    print("notes: %d" % len(notes))
    for tid, num, name, blurb, color in THEMES:
        c = sum(1 for n in notes if n["theme"] == tid)
        print("  %-12s %3d  %s" % (tid, c, name))

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(NOTES_OUT)
    with open(os.path.join(OUT, "index.html"), "w") as fh:
        fh.write(build_index(notes))
    with open(os.path.join(OUT, "before.html"), "w") as fh:
        fh.write(build_before(notes))

    order = sorted(notes, key=lambda n: (n["theme"], n["title"].lower()))
    theme_names = {t[0]: t[2] for t in THEMES}
    theme_nums = {t[0]: t[1] for t in THEMES}
    for i, n in enumerate(order):
        prev_n = order[i - 1] if i > 0 else None
        next_n = order[i + 1] if i < len(order) - 1 else None
        html_page = build_note_page(n, prev_n, next_n,
                                    theme_names[n["theme"]], theme_nums[n["theme"]])
        with open(os.path.join(NOTES_OUT, n["slug"] + ".html"), "w") as fh:
            fh.write(html_page)
    print("wrote %d note pages" % len(order))


if __name__ == "__main__":
    main()
