#!/usr/bin/env python3
"""muse v2: the research index.

Static site generator for builtbysai/muse-redesign. Parses the 229 study
notes in study/, keeps the hand-curated theme filing, then cross-cuts the
corpus by FUNCTION (techniques to steal / avoid-list / palettes /
doorways / gaps) and renders a dark, digital-native index plus aggregate
views and per-note pages. Stdlib only. No network, no CDN, no fonts.
"""
import html
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.join(HERE, "study")
OUT = os.path.join(HERE, "site")

# ---------------------------------------------------------------- renderer --
# (spliced in from build_index.py: INLINE_PATTERNS, render_inline,
#  _split_table_row, render_markdown)

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
            out.append("".join(t))
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

# ------------------------------------------------------------------- themes --
# (spliced in from build_index.py: THEMES)

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

# (spliced in from build_index.py: SLUG_THEME, TITLE_OVERRIDES)


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

TITLE_STRIP = [
    r" - Deep Study Notes$", r": Deep Study Notes$", r" - Study Notes$",
    r": Study Notes$", r" Study Notes$",
]

# Distinct hue per theme for the facet tags (digital palette, not paper).
THEME_HUE = {
    "print": 16, "pioneers": 212, "sound": 152, "creativecode": 288,
    "color": 44, "kinetic": 188, "painters": 326, "text": 228,
    "webplay": 96, "scenes": 4,
}
THEME_BY_ID = {t[0]: t for t in THEMES}

# Functional cross-cut: what you DO with a note, derived from the section
# headings the notes actually use. Order matters: first match wins.
GROUP_RULES = [
    ("techniques", ["techniques to steal", "core techniques",
                    "technique takeaways", "the technique, as found",
                    "technique breakdown", "what to steal",
                    "key process ideas", "what to take from it"]),
    ("sings", ["what makes it sing", "what sings",
               "what makes the work good", "quality notes",
               "quality thesis", "the thesis, stated plainly"]),
    ("avoid", ["avoid-list", "avoid list", "avoidlist", "what not to do",
               "what to avoid", "overdone"]),
    ("palette", ["palette and composition"]),
    ("doorways", ["doorway", "open doors", "doorways for future"]),
    ("gaps", ["honest gaps"]),
    ("sources", ["sources"]),
]
GROUP_LABEL = {
    "techniques": "Techniques", "sings": "What sings", "avoid": "Avoid",
    "palette": "Palette", "doorways": "Doorways", "gaps": "Gaps",
    "sources": "Sources",
}
GROUP_LETTER = {
    "techniques": "T", "avoid": "A", "palette": "P",
    "doorways": "D", "gaps": "G",
}
# view accent colors
GROUP_COLOR = {
    "techniques": "#b7f34b", "avoid": "#ff7a59", "palette": "#c4a5fc",
    "doorways": "#6fd7f7", "gaps": "#f5c453",
}

AGG_VIEWS = [
    ("techniques", "Steal this",
     "Every stealable technique in the corpus, in one list. Recipes, not copies.",
     "techniques"),
    ("avoid", "The avoid-list",
     "What is overdone, what fails, what to skip. The collected traps of 229 study sessions.",
     "avoid"),
    ("palettes", "Palettes and composition",
     "Color thinking from the notes that recorded it: grounds, bands, palettes that work.",
     "palette"),
    ("doorways", "Open doorways",
     "Threads the notes left open on purpose. Where the research goes next.",
     "doorways"),
    ("gaps", "Honest gaps",
     "What the notes admit they never saw. A research backlog, kept honestly.",
     "gaps"),
]


def group_of(heading):
    h = heading.lower()
    for gid, pats in GROUP_RULES:
        for p in pats:
            if p in h:
                return gid
    return None


# ------------------------------------------------------------ note parsing --

def clean_title(raw, slug):
    t = raw.strip()
    for pat in TITLE_STRIP:
        t = re.sub(pat, "", t)
    m = re.match(r"^(.*?):?\s*[Ss]tudy Notes\s*(\(.*\))$", t)
    if m:
        t = (m.group(1) + " " + m.group(2)).strip()
        t = re.sub(r"\s*:\s*\(", " (", t)
    t = re.sub(r"\s+", " ", t).strip(" -:;,.")
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    return t


def split_catalogue(lines):
    """Pull the leading **Key:** metadata block out of the note body."""
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
        key = m.group(1).strip().rstrip(":.")
        val_prefix = ""
        if ":" in key:
            key, val_prefix = [p.strip().rstrip(".") for p in key.split(":", 1)]
        if len(key) > 28 or len(key.split()) > 3 or not re.match(
                r"^[A-Za-z][A-Za-z0-9 /-]*$", key):
            break
        val_lines = [p for p in [val_prefix, m.group(2)] if p]
        i += 1
        while i < n:
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
            continue
        in_para = True
        buf.append(s)
        if len(" ".join(buf)) > 220:
            break
    text = " ".join(buf)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sections(lines):
    """Split body lines into intro + [(heading, level, lines)]."""
    intro, sections = [], []
    cur = None
    for line in lines:
        m = re.match(r"^(#{2,3})\s+(.*)$", line.strip())
        if m:
            if cur:
                sections.append(cur)
            cur = [m.group(2).strip(), len(m.group(1)), []]
        elif cur:
            cur[2].append(line)
        else:
            intro.append(line)
    if cur:
        sections.append(cur)
    return intro, [{"heading": h, "level": lv, "lines": ls}
                   for h, lv, ls in sections]


def extract_bullets(lines):
    items = []
    cur = []

    def flush():
        if cur:
            items.append(" ".join(cur).strip())
            del cur[:]

    for line in lines:
        s = line.strip()
        m = re.match(r"^[-*+]\s+(.*)$", s) or re.match(r"^\d{1,2}[.)]\s+(.*)$", s)
        if m:
            flush()
            cur.append(m.group(1).strip())
        elif cur and s and not s.startswith("#") and not s.startswith("|"):
            cur.append(s)
    flush()
    return items


def plain_of(lines):
    t = "\n".join(lines)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[*_`#>|]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "s"


def parse_note(path, slug):
    src = open(path, encoding="utf-8", errors="replace").read()
    lines = src.split("\n")
    title_idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), 0)
    title = clean_title(lines[title_idx].lstrip("# "), slug)
    catalogue, rest = split_catalogue(lines[title_idx + 1:])
    intro_lines, sections = split_sections(rest)
    for sec in sections:
        sec["group"] = group_of(sec["heading"])
        sec["bullets"] = extract_bullets(sec["lines"])
        sec["text"] = plain_of(sec["lines"])
        body_src = "\n".join(sec["lines"]).strip("\n")
        sec["html"] = render_markdown(body_src) if body_src.strip() else ""
        sec["anchor"] = slugify(sec["heading"])
    intro_html = render_markdown("\n".join(intro_lines).strip("\n"))
    cat_html = ""
    if catalogue:
        cat_html = "".join(
            "<div><dt>%s</dt><dd>%s</dd></div>"
            % (html.escape(k), render_inline(v))
            for k, v in catalogue)
        cat_html = '<dl class="spec">%s</dl>' % cat_html
    words = len(re.findall(r"[A-Za-z0-9']+", src))
    excerpt = first_paragraph_text(rest)
    excerpt = re.sub(r"^Deep study,?\s*\d{4}-\d{2}-\d{2}\.?\s*", "", excerpt)
    excerpt = re.sub(r"^Deep study\.?\s*", "", excerpt)
    m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", src[:3000])
    date = m.group(1) if m else ""
    theme = SLUG_THEME.get(slug)
    groups = sorted({s["group"] for s in sections if s["group"]})
    return {
        "slug": slug, "title": title, "words": words,
        "minutes": max(1, round(words / 200)),
        "excerpt": excerpt, "date": date, "theme": theme,
        "catalogue_html": cat_html, "intro_html": intro_html,
        "sections": sections, "groups": groups,
    }

# --------------------------------------------------------------------- css --

CSS = r"""
:root{
  --bg:#0a0c10; --bg2:#0d1016; --panel:#11161e; --panel2:#171d27;
  --line:#202939; --line2:#2c3749;
  --text:#e9edf2; --dim:#9aa6b5; --faint:#626d7d;
  --acid:#b7f34b;
  --mono:ui-monospace,'SF Mono','Cascadia Code','Roboto Mono',Menlo,Consolas,'Liberation Mono',monospace;
  --sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,'Helvetica Neue',Arial,sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:16px;line-height:1.6}
::selection{background:var(--acid);color:#0a0c10}
a{color:var(--acid);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1060px;margin:0 auto;padding:0 24px}
.mono{font-family:var(--mono)}

/* top bar */
.topbar{position:sticky;top:0;z-index:60;background:rgba(10,12,16,.84);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.topbar .wrap{display:flex;align-items:center;gap:26px;height:60px}
.brand{font-family:var(--mono);font-weight:800;font-size:15px;letter-spacing:.06em;color:var(--text);white-space:nowrap}
.brand:hover{text-decoration:none}
.brand .blk{display:inline-block;width:11px;height:11px;background:var(--acid);margin-right:9px;vertical-align:baseline}
.brand small{color:var(--faint);font-weight:400;letter-spacing:.18em;font-size:10.5px;margin-left:10px}
.nav{display:flex;gap:4px;margin-left:auto;overflow-x:auto;scrollbar-width:none}
.nav::-webkit-scrollbar{display:none}
.nav a{font-family:var(--mono);font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--dim);padding:8px 11px;border-radius:7px;white-space:nowrap}
.nav a:hover{color:var(--text);text-decoration:none;background:var(--panel)}
.nav a.active{color:var(--acid)}
.cmdk-btn{font-family:var(--mono);font-size:12px;color:var(--dim);background:var(--panel);
  border:1px solid var(--line2);border-radius:8px;padding:7px 11px;cursor:pointer;white-space:nowrap}
.cmdk-btn:hover{color:var(--text);border-color:var(--faint)}
.cmdk-btn kbd{font-family:var(--mono);font-size:10.5px;color:var(--faint);border:1px solid var(--line2);
  border-radius:4px;padding:1px 5px;margin-left:6px}

/* hero */
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line)}
.hero canvas{position:absolute;inset:0;width:100%;height:100%;opacity:.85;
  -webkit-mask-image:linear-gradient(180deg,#000 30%,transparent 96%);
  mask-image:linear-gradient(180deg,#000 30%,transparent 96%)}
.hero .wrap{position:relative;padding-top:88px;padding-bottom:60px}
.kicker{font-family:var(--mono);font-size:12px;letter-spacing:.3em;color:var(--acid);margin:0 0 18px}
.hero h1{margin:0 0 20px;font-size:clamp(2.5rem,6vw,4.4rem);font-weight:800;
  letter-spacing:-.032em;line-height:1.02;max-width:14ch}
.hero h1 .a{color:var(--acid)}
.lede{color:var(--dim);font-size:17.5px;max-width:62ch;margin:0 0 34px}
.lede strong{color:var(--text);font-weight:600}
.stats{display:flex;flex-wrap:wrap;gap:14px 44px;margin:0;padding:0;list-style:none}
.stats li{font-family:var(--mono)}
.stats b{display:block;font-size:27px;font-weight:700;color:var(--text);letter-spacing:-.02em}
.stats b em{font-style:normal;color:var(--acid)}
.stats span{font-size:10.5px;letter-spacing:.22em;color:var(--faint);text-transform:uppercase}

/* search */
.searchzone{margin:38px 0 8px}
.searchbox{position:relative}
.searchbox input{width:100%;background:var(--panel);border:1px solid var(--line2);border-radius:12px;
  color:var(--text);font-family:var(--mono);font-size:15.5px;padding:17px 20px 17px 52px;outline:none}
.searchbox input:focus{border-color:var(--acid);box-shadow:0 0 0 3px rgba(183,243,75,.14)}
.searchbox input::placeholder{color:var(--faint)}
.searchbox .mag{position:absolute;left:19px;top:50%;transform:translateY(-50%);color:var(--faint);font-size:17px}
.searchmeta{font-family:var(--mono);font-size:12px;color:var(--faint);margin:12px 2px 0;min-height:18px}
.searchmeta b{color:var(--acid);font-weight:700}
.empty{border:1px dashed var(--line2);border-radius:12px;padding:44px 24px;text-align:center;color:var(--faint);
  font-family:var(--mono);font-size:13.5px;margin:26px 0}

/* facets */
.facets{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 6px;align-items:center}
.facet-label{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;color:var(--faint);
  text-transform:uppercase;margin-right:4px}
.chip{font-family:var(--mono);font-size:11.5px;color:var(--dim);background:transparent;
  border:1px solid var(--line2);border-radius:999px;padding:7px 13px;cursor:pointer;white-space:nowrap}
.chip:hover{color:var(--text);border-color:var(--faint)}
.chip.on{background:var(--acid);border-color:var(--acid);color:#0a0c10;font-weight:700}
.chip .n{opacity:.62;font-weight:400;margin-left:5px}
.chip.on .n{opacity:.7}
.chip.theme.on{background:hsl(var(--h) 72% 62%);border-color:hsl(var(--h) 72% 62%)}
.sortsel{margin-left:auto;font-family:var(--mono);font-size:11.5px;color:var(--dim);
  background:var(--panel);border:1px solid var(--line2);border-radius:8px;padding:7px 10px}

/* index rows */
.rows{margin:26px 0 70px;border-bottom:1px solid var(--line)}
.row{display:grid;grid-template-columns:1fr auto;gap:8px 18px;align-items:center;
  padding:17px 10px;border-top:1px solid var(--line);color:var(--text)}
.row:hover{text-decoration:none;background:var(--panel)}
.row[hidden]{display:none}
.row-title{display:block;font-size:16.5px;font-weight:650;letter-spacing:-.008em;line-height:1.35}
.row:hover .row-title{color:var(--acid)}
.row-meta{display:block;font-family:var(--mono);font-size:11px;color:var(--faint);margin-top:6px;letter-spacing:.04em}
.row-meta .tdot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;vertical-align:1px}
.fnchips{display:flex;gap:5px}
.fn{font-family:var(--mono);font-size:10px;font-weight:700;width:22px;height:22px;line-height:22px;
  text-align:center;border-radius:6px;border:1px solid}
.snip{display:block;font-family:var(--mono);font-size:12px;color:var(--dim);margin-top:7px;line-height:1.55}
.snip mark{background:rgba(183,243,75,.22);color:var(--acid);border-radius:3px;padding:0 2px}

/* section headers on aggregate pages */
.vhero{padding:64px 0 8px}
.vhero h1{margin:0 0 14px;font-size:clamp(2rem,4.6vw,3.2rem);font-weight:800;letter-spacing:-.03em}
.vhero h1 .tick{display:inline-block;width:.32em;height:.32em;background:var(--vaccent,var(--acid));
  margin-right:.35em;vertical-align:.08em}
.vhero p{color:var(--dim);max-width:64ch;margin:0 0 8px;font-size:16.5px}
.vcount{font-family:var(--mono);font-size:12px;color:var(--faint);letter-spacing:.14em;margin:18px 0 0}
.vcount b{color:var(--vaccent,var(--acid))}
.items{margin:30px 0 80px}
.item{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--vaccent,var(--acid));
  border-radius:0 10px 10px 0;padding:15px 18px;margin-bottom:10px}
.item[hidden]{display:none}
.item .txt{font-size:15.5px;line-height:1.62}
.item .txt p{margin:0}
.item .src{font-family:var(--mono);font-size:11.5px;color:var(--faint);margin-top:10px;letter-spacing:.03em}
.item .src a{color:var(--dim)}
.item .src a:hover{color:var(--vaccent,var(--acid))}
.item .src .tt{color:var(--vaccent,var(--acid))}
.item .txt mark{background:rgba(183,243,75,.2);color:var(--acid);border-radius:3px;padding:0 2px}
.palblock{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px 24px;margin-bottom:14px}
.palblock[hidden]{display:none}
.palblock h3{margin:0 0 4px;font-size:18px;font-weight:700;letter-spacing:-.01em}
.palblock h3 a{color:var(--text)}
.palblock h3 a:hover{color:var(--pal,#c4a5fc)}
.palblock .secname{font-family:var(--mono);font-size:11px;color:var(--pal,#c4a5fc);letter-spacing:.14em;
  text-transform:uppercase;margin-bottom:12px}
.palblock .body{color:var(--dim);font-size:15px;line-height:1.65}
.palblock .body p{margin:0 0 10px}
.palblock .body ul{margin:8px 0;padding-left:20px}

/* note page */
.crumb{font-family:var(--mono);font-size:11.5px;color:var(--faint);letter-spacing:.1em;margin:34px 0 20px}
.crumb a{color:var(--dim)}
.crumb a:hover{color:var(--acid)}
.note h1{margin:0 0 22px;font-size:clamp(1.8rem,4vw,2.9rem);font-weight:800;letter-spacing:-.028em;line-height:1.08;max-width:20ch}
.specs{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:0 0 34px}
.specs div{background:var(--bg2);padding:14px 16px}
.specs dt{font-family:var(--mono);font-size:10px;letter-spacing:.22em;color:var(--faint);text-transform:uppercase;margin:0 0 6px}
.specs dd{margin:0;font-family:var(--mono);font-size:13px;color:var(--text)}
.specs dd .tdot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px}
dl.spec{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:0 0 30px}
dl.spec div{background:var(--bg2);padding:13px 16px}
dl.spec dt{font-family:var(--mono);font-size:10px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--faint);margin:0 0 6px}
dl.spec dd{margin:0;font-size:13.5px;color:var(--dim);line-height:1.6}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 36px}
.toc a{font-family:var(--mono);font-size:11.5px;color:var(--dim);border:1px solid var(--line2);
  border-radius:8px;padding:6px 12px}
.toc a:hover{color:var(--acid);border-color:var(--acid);text-decoration:none}
.toc a.g-avoid:hover{color:#ff7a59;border-color:#ff7a59}
.toc a.g-techniques:hover{color:#b7f34b;border-color:#b7f34b}
.toc a.g-palette:hover{color:#c4a5fc;border-color:#c4a5fc}
.toc a.g-doorways:hover{color:#6fd7f7;border-color:#6fd7f7}
.toc a.g-gaps:hover{color:#f5c453;border-color:#f5c453}
.nbody{max-width:74ch;font-size:16.5px;line-height:1.72;color:#d5dbe3}
.nbody p{margin:0 0 1.15em}
.nbody h2{font-size:21px;font-weight:750;letter-spacing:-.015em;margin:2.4em 0 .9em;padding-left:14px;
  border-left:3px solid var(--acid);scroll-margin-top:90px}
.nbody h3{font-size:16.5px;font-weight:700;margin:1.8em 0 .6em;scroll-margin-top:90px}
.nbody ul,.nbody ol{margin:0 0 1.15em;padding-left:22px}
.nbody li{margin-bottom:.45em}
.nbody li::marker{color:var(--acid)}
.nbody strong{color:var(--text)}
.nbody code{font-family:var(--mono);font-size:.86em;background:var(--panel2);border:1px solid var(--line);
  border-radius:5px;padding:1px 6px;color:var(--acid)}
.nbody pre{background:#07090c;border:1px solid var(--line);border-radius:10px;padding:18px;overflow-x:auto;margin:0 0 1.4em}
.nbody pre code{background:none;border:none;padding:0;color:#c9d4e0;font-size:13px;line-height:1.6}
.nbody blockquote{border-left:3px solid var(--line2);margin:0 0 1.4em;padding:4px 0 4px 18px;color:var(--dim)}
.nbody table{border-collapse:collapse;width:100%;margin:0 0 1.4em;font-size:14px}
.nbody th,.nbody td{border:1px solid var(--line);padding:9px 12px;text-align:left;vertical-align:top}
.nbody th{background:var(--panel);font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;color:var(--dim)}
.nbody hr{border:none;border-top:1px solid var(--line);margin:2.4em 0}
.related{margin:64px 0 8px}
.related h2{font-family:var(--mono);font-size:11.5px;letter-spacing:.26em;color:var(--faint);
  text-transform:uppercase;margin:0 0 18px}
.relgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.relgrid a{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:15px 17px;color:var(--text)}
.relgrid a:hover{border-color:var(--acid);text-decoration:none}
.relgrid a:hover .rt{color:var(--acid)}
.relgrid .rt{display:block;font-size:14.5px;font-weight:650;line-height:1.4;margin-bottom:6px}
.relgrid .rm{font-family:var(--mono);font-size:10.5px;color:var(--faint)}
.pn{display:flex;justify-content:space-between;gap:14px;margin:40px 0 80px}
.pn a{flex:1;max-width:48%;border:1px solid var(--line);border-radius:10px;padding:14px 18px;color:var(--text)}
.pn a:hover{border-color:var(--acid);text-decoration:none}
.pn .dir{font-family:var(--mono);font-size:10.5px;letter-spacing:.2em;color:var(--faint);text-transform:uppercase;display:block;margin-bottom:6px}
.pn .t{font-size:14.5px;font-weight:650}
.pn a.next{text-align:right}

/* cmdk */
.cmdk{position:fixed;inset:0;z-index:100;display:none;align-items:flex-start;justify-content:center;
  background:rgba(4,6,9,.72);backdrop-filter:blur(6px);padding:12vh 20px 20px}
.cmdk.open{display:flex}
.cmdk-box{width:min(640px,100%);background:var(--bg2);border:1px solid var(--line2);border-radius:14px;overflow:hidden;
  box-shadow:0 30px 80px rgba(0,0,0,.6)}
.cmdk-box input{width:100%;background:transparent;border:none;outline:none;color:var(--text);
  font-family:var(--mono);font-size:16px;padding:18px 20px;border-bottom:1px solid var(--line)}
.cmdk-list{max-height:46vh;overflow-y:auto;padding:8px}
.cmdk-list a{display:block;padding:10px 14px;border-radius:8px;color:var(--text)}
.cmdk-list a:hover,.cmdk-list a.sel{background:var(--panel);text-decoration:none}
.cmdk-list .ct{display:block;font-size:14.5px;font-weight:600}
.cmdk-list .cm{font-family:var(--mono);font-size:11px;color:var(--faint);margin-top:3px;display:block}
.cmdk-hint{font-family:var(--mono);font-size:10.5px;color:var(--faint);padding:10px 18px;border-top:1px solid var(--line)}

/* footer */
footer{border-top:1px solid var(--line);margin-top:20px}
footer .wrap{display:flex;flex-wrap:wrap;gap:8px 26px;align-items:center;padding-top:26px;padding-bottom:34px;
  font-family:var(--mono);font-size:11.5px;color:var(--faint)}
footer a{color:var(--dim)}

@media (max-width:720px){
  .hero .wrap{padding-top:60px;padding-bottom:44px}
  .row{grid-template-columns:1fr}
  .fnchips{margin-top:2px}
  .sortsel{margin-left:0}
  .pn a{max-width:100%}
  .pn{flex-direction:column}
  .brand small{display:none}
}
"""

# --------------------------------------------------------------- page shell --

NAV = [
    ("index", "Index", "index.html"),
    ("techniques", "Techniques", "techniques.html"),
    ("avoid", "Avoid", "avoid.html"),
    ("palettes", "Palettes", "palettes.html"),
    ("doorways", "Doorways", "doorways.html"),
    ("gaps", "Gaps", "gaps.html"),
]


def topbar(active, root=""):
    links = "".join(
        '<a href="%s%s"%s>%s</a>' % (
            root, href, ' class="active"' if key == active else "", label)
        for key, label, href in NAV)
    return (
        '<header class="topbar"><div class="wrap">'
        '<a class="brand" href="%sindex.html"><span class="blk"></span>MUSE'
        '<small>RESEARCH INDEX</small></a>'
        '<nav class="nav">%s</nav>'
        '<button class="cmdk-btn" id="cmdkBtn" type="button">Search<kbd>&#8984;K</kbd></button>'
        '</div></header>' % (root, links))


FOOTER = (
    '<footer><div class="wrap">'
    '<span><span style="color:var(--acid)">&#9632;</span>&nbsp; MUSE research index</span>'
    '<span>229 study notes by Hans Sai</span>'
    '<span><a href="https://github.com/builtbysai/muse">source notes</a></span>'
    '<span>built static, no trackers, no fonts fetched</span>'
    '</div></footer>')


def page_shell(title, body, active, root="", extra_head="", extra_js=""):
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n'
        '<meta name="description" content="MUSE: a working research index of 229 study notes on generative art, printmaking, composition and technique.">\n'
        '<style>%s</style>\n%s</head>\n<body>\n%s\n%s\n%s\n'
        '<script>%s</script>\n</body>\n</html>'
        % (html.escape(title), CSS, extra_head, topbar(active, root), body,
           FOOTER, extra_js))


# Command-K overlay: full search on the index, deep-link elsewhere.
CMDK_JS = r"""
(function(){
  var btn = document.getElementById('cmdkBtn');
  function go(q){
    var u = 'INDEXROOTindex.html' + (q ? '?q=' + encodeURIComponent(q) : '#qfocus');
    location.href = u;
  }
  document.addEventListener('keydown', function(e){
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k'){ e.preventDefault(); go(''); }
  });
  if (btn) btn.addEventListener('click', function(){ go(''); });
})();
"""

# Full command-K with live results (index page only; INDEX_DATA embedded).
CMDK_FULL_JS = r"""
(function(){
  var data = INDEX_DATA, input = document.getElementById('cmdkInput'),
      list = document.getElementById('cmdkList'), ov = document.getElementById('cmdk'),
      sel = 0, hits = [];
  function score(n, terms){
    var s = 0, t = (n[1] + ' ' + n[7]).toLowerCase();
    for (var i = 0; i < terms.length; i++){
      var term = terms[i], ti = n[1].toLowerCase();
      if (t.indexOf(term) < 0) return -1;
      if (ti.indexOf(term) === 0) s += 9;
      else if (ti.indexOf(term) > 0) s += 5;
      else s += 1;
    }
    return s;
  }
  function render(){
    var q = input.value.trim().toLowerCase(), terms = q.split(/\s+/).filter(Boolean);
    hits = [];
    if (terms.length){
      for (var i = 0; i < data.length; i++){
        var sc = score(data[i], terms);
        if (sc >= 0) hits.push([sc, data[i]]);
      }
      hits.sort(function(a,b){ return b[0]-a[0] || (a[1][1] < b[1][1] ? -1 : 1); });
      hits = hits.slice(0, 9);
    }
    sel = 0;
    list.innerHTML = hits.map(function(h, i){
      var n = h[1];
      return '<a href="notes/' + n[0] + '.html" data-i="' + i + '" class="' + (i===0?'sel':'') + '">' +
        '<span class="ct">' + esc(n[1]) + '</span>' +
        '<span class="cm">' + esc(THEMENAMES[n[2]] || n[2]) + (n[3] ? ' &middot; ' + n[3] : '') + '</span></a>';
    }).join('') || '<div class="cmdk-hint">No matches. Try a technique, an artist, a year.</div>';
  }
  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function open(){ ov.classList.add('open'); input.value=''; render(); setTimeout(function(){ input.focus(); }, 30); }
  function close(){ ov.classList.remove('open'); }
  function choose(){
    var a = list.querySelector('a.sel') || list.querySelector('a');
    if (a) location.href = a.getAttribute('href');
  }
  document.getElementById('cmdkBtn').addEventListener('click', open);
  document.addEventListener('keydown', function(e){
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k'){ e.preventDefault(); open(); }
    else if (e.key === 'Escape') close();
    else if (ov.classList.contains('open') && e.key === 'ArrowDown'){ e.preventDefault(); move(1); }
    else if (ov.classList.contains('open') && e.key === 'ArrowUp'){ e.preventDefault(); move(-1); }
    else if (ov.classList.contains('open') && e.key === 'Enter'){ choose(); }
  });
  ov.addEventListener('click', function(e){ if (e.target === ov) close(); });
  input.addEventListener('input', render);
  function move(d){
    var as = list.querySelectorAll('a'); if (!as.length) return;
    sel = (sel + d + as.length) % as.length;
    as.forEach(function(a, i){ a.classList.toggle('sel', i === sel); });
  }
})();
"""

# Generative flow-field hero canvas: the site itself is a generative artifact.
CANVAS_JS = r"""
(function(){
  var c = document.getElementById('field');
  if (!c || !c.getContext) return;
  var ctx = c.getContext('2d'), W = 0, H = 0;
  var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
  function size(){
    W = c.clientWidth; H = c.clientHeight;
    c.width = W * dpr; c.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  size(); window.addEventListener('resize', size);
  var seed = 20261010;
  function rnd(){ seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
  var N = 380, P = [];
  function spawn(p){ p.x = rnd() * W; p.y = rnd() * H; p.s = .5 + rnd() * 1.5; return p; }
  for (var i = 0; i < N; i++) P.push(spawn({}));
  ctx.fillStyle = '#0a0c10'; ctx.fillRect(0, 0, W, H);
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    ctx.strokeStyle = 'rgba(183,243,75,.4)'; ctx.lineWidth = 1; ctx.beginPath();
    for (var j = 0; j < P.length; j++){ var q = P[j];
      ctx.moveTo(q.x, q.y); ctx.lineTo(q.x + 40 * Math.sin(q.y * .02), q.y + 40 * Math.cos(q.x * .02)); }
    ctx.stroke(); return;
  }
  var t = 0;
  function step(){
    t += .0045;
    ctx.fillStyle = 'rgba(10,12,16,.055)'; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = 'rgba(183,243,75,.42)'; ctx.lineWidth = 1;
    ctx.beginPath();
    for (var i = 0; i < P.length; i++){
      var p = P[i];
      var n = Math.sin(p.x * .011 + t) + Math.cos(p.y * .013 - t * 1.35);
      var a = n * 2.4;
      var nx = p.x + Math.cos(a) * p.s * 3.4, ny = p.y + Math.sin(a) * p.s * 3.4;
      ctx.moveTo(p.x, p.y); ctx.lineTo(nx, ny);
      p.x = nx; p.y = ny;
      if (p.x < -10 || p.x > W + 10 || p.y < -10 || p.y > H + 10) spawn(p);
    }
    ctx.stroke();
    requestAnimationFrame(step);
  }
  step();
})();
"""

# ------------------------------------------------------------------ index ---

INDEX_JS = r"""
(function(){
  var DATA = INDEX_DATA, NAMES = THEMENAMES;
  var rows = {}, order = [];
  document.querySelectorAll('.row').forEach(function(r){
    rows[r.getAttribute('data-slug')] = r; order.push(r.getAttribute('data-slug'));
  });
  var bySlug = {}; DATA.forEach(function(d){ bySlug[d[0]] = d; });
  var q = document.getElementById('q'), meta = document.getElementById('searchmeta'),
      box = document.getElementById('rows');
  var themeSel = {}, fnSel = {}, sortMode = 'date', query = '';

  function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  function score(d, terms){
    var hay = (d[1] + ' ' + d[7]).toLowerCase(), s = 0;
    for (var i = 0; i < terms.length; i++){
      var term = terms[i], ti = d[1].toLowerCase();
      if (hay.indexOf(term) < 0) return -1;
      if (ti.indexOf(term) === 0) s += 9;
      else if (ti.indexOf(term) > 0) s += 5;
      else s += 1;
    }
    return s;
  }
  function snippet(d, terms){
    var x = d[7], xl = x.toLowerCase(), best = -1;
    for (var i = 0; i < terms.length; i++){
      var p = xl.indexOf(terms[i]);
      if (p >= 0 && (best < 0 || p < best)) best = p;
    }
    if (best < 0) return '';
    var a = Math.max(0, best - 70), b = Math.min(x.length, best + 130);
    var s = esc(x.slice(a, b));
    terms.forEach(function(t){
      s = s.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
    });
    return '<span class="snip">' + (a > 0 ? '&hellip;' : '') + s + (b < x.length ? '&hellip;' : '') + '</span>';
  }
  function themePass(d){
    var keys = Object.keys(themeSel);
    return !keys.length || themeSel[d[2]];
  }
  function fnPass(d){
    var keys = Object.keys(fnSel);
    if (!keys.length) return true;
    var fl = d[6].toLowerCase();
    for (var i = 0; i < keys.length; i++) if (fl.indexOf(keys[i]) >= 0) return true;
    return false;
  }
  function cmpNoQuery(a, b){
    var da = a[1], db = b[1];
    if (sortMode === 'title')
      return da[1].toLowerCase() < db[1].toLowerCase() ? -1 : 1;
    if (sortMode === 'words')
      return (db[5] - da[5]) || (da[1].toLowerCase() < db[1].toLowerCase() ? -1 : 1);
    var xa = da[3] || '', xb = db[3] || '';
    if (xa !== xb) return xb < xa ? -1 : 1;
    return da[1].toLowerCase() < db[1].toLowerCase() ? -1 : 1;
  }
  function apply(){
    var terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    var hits = [];
    for (var i = 0; i < DATA.length; i++){
      var d = DATA[i];
      if (!themePass(d) || !fnPass(d)) continue;
      if (terms.length){
        var sc = score(d, terms);
        if (sc < 0) continue;
        hits.push([sc, d]);
      } else hits.push([0, d]);
    }
    if (terms.length) hits.sort(function(a, b){ return b[0] - a[0] || (a[1][1] < b[1][1] ? -1 : 1); });
    else hits.sort(cmpNoQuery);
    hits = hits.slice(0, terms.length ? 60 : 10000);
    var seen = {};
    hits.forEach(function(h){
      var slug = h[1][0]; seen[slug] = true;
      var r = rows[slug];
      r.hidden = false;
      var sn = r.querySelector('.snip');
      if (terms.length){
        var html = snippet(h[1], terms);
        if (sn) sn.outerHTML = html;
        else r.querySelector('.row-main').insertAdjacentHTML('beforeend', html);
      } else if (sn) sn.remove();
      box.appendChild(r);
    });
    Object.keys(rows).forEach(function(slug){ if (!seen[slug]) rows[slug].hidden = true; });
    if (terms.length) meta.innerHTML = '<b>' + hits.length + '</b> result' + (hits.length === 1 ? '' : 's') +
      (hits.length === 60 ? ' (top 60 shown)' : '') + ' for &ldquo;' + esc(query.trim()) + '&rdquo;';
    else meta.innerHTML = 'showing <b>' + hits.length + '</b> of ' + DATA.length + ' notes';
    document.getElementById('empty').hidden = hits.length > 0;
  }
  q.addEventListener('input', function(){ query = q.value; apply(); });
  document.querySelectorAll('.chip.theme').forEach(function(c){
    c.addEventListener('click', function(){
      var k = c.getAttribute('data-k');
      if (themeSel[k]) delete themeSel[k]; else themeSel[k] = 1;
      c.classList.toggle('on', !!themeSel[k]); apply();
    });
  });
  document.querySelectorAll('.chip.fnchip').forEach(function(c){
    c.addEventListener('click', function(){
      var k = c.getAttribute('data-k');
      if (fnSel[k]) delete fnSel[k]; else fnSel[k] = 1;
      c.classList.toggle('on', !!fnSel[k]); apply();
    });
  });
  document.getElementById('sortsel').addEventListener('change', function(e){
    sortMode = e.target.value; apply();
  });
  var params = new URLSearchParams(location.search);
  if (params.get('q')){ q.value = params.get('q'); query = q.value; }
  if (params.get('theme')){
    params.get('theme').split(',').forEach(function(k){
      var c = document.querySelector('.chip.theme[data-k="' + k + '"]');
      if (c){ themeSel[k] = 1; c.classList.add('on'); }
    });
  }
  apply();
  if (location.hash === '#qfocus') setTimeout(function(){ q.focus(); }, 120);
})();
"""


def theme_tag_html(tid):
    t = THEME_BY_ID[tid]
    return ('<span class="tdot" style="background:hsl(%d 72%% 62%%)"></span>%s'
            % (THEME_HUE[tid], html.escape(t[2].upper())))


def fn_chips_html(groups):
    out = []
    for gid in ("techniques", "avoid", "palette", "doorways", "gaps"):
        if gid in groups:
            col = GROUP_COLOR[gid]
            out.append(
                '<span class="fn" title="%s" style="color:%s;border-color:%s;background:%s24">%s</span>'
                % (GROUP_LABEL[gid], col, col, col, GROUP_LETTER[gid]))
    return '<span class="fnchips">%s</span>' % "".join(out)


def build_index(notes, stats):
    theme_counts = {}
    for n in notes:
        theme_counts[n["theme"]] = theme_counts.get(n["theme"], 0) + 1
    chips = "".join(
        '<button type="button" class="chip theme" data-k="%s" style="--h:%d">%s<span class="n">%d</span></button>'
        % (tid, THEME_HUE[tid], html.escape(THEME_BY_ID[tid][2]), theme_counts.get(tid, 0))
        for tid, _, _, _, _ in THEMES)
    fnchips = "".join(
        '<button type="button" class="chip fnchip" data-k="%s" style="--h:0">%s</button>'
        % (GROUP_LETTER[gid].lower(), GROUP_LABEL[gid])
        for gid in ("techniques", "avoid", "palette", "doorways", "gaps"))

    def corpus(n):
        parts = [n["title"], " ".join(s["heading"] for s in n["sections"]), n["excerpt"]]
        for s in n["sections"]:
            if s["group"] in ("techniques", "avoid", "doorways", "gaps"):
                parts.extend(s["bullets"][:6])
        text = re.sub(r"\s+", " ", " ".join(parts)).strip()
        return text[:1400]

    data = []
    row_html = []
    for n in notes:
        fnletters = "".join(GROUP_LETTER[g] for g in
                            ("techniques", "avoid", "palette", "doorways", "gaps")
                            if g in n["groups"])
        data.append([n["slug"], n["title"], n["theme"], n["date"],
                     n["minutes"], n["words"], fnletters, corpus(n)])
        meta = '%s &middot; %s &middot; %d MIN &middot; %d WORDS' % (
            theme_tag_html(n["theme"]),
            n["date"] if n["date"] else "UNDATED",
            n["minutes"], n["words"])
        row_html.append(
            '<a class="row" data-slug="%s" href="notes/%s.html">'
            '<span class="row-main"><span class="row-title">%s</span>'
            '<span class="row-meta">%s</span></span>%s</a>'
            % (n["slug"], n["slug"], html.escape(n["title"]), meta,
               fn_chips_html(n["groups"])))

    themenames = {tid: THEME_BY_ID[tid][2] for tid, _, _, _, _ in THEMES}

    def safe_json(obj):
        return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

    js = ("var INDEX_DATA = %s;\nvar THEMENAMES = %s;\n" % (
        safe_json(data), safe_json(themenames))) + INDEX_JS

    body = (
        '<section class="hero"><canvas id="field" aria-hidden="true"></canvas><div class="wrap">'
        '<p class="kicker">RESEARCH INDEX &middot; 229 STUDY NOTES</p>'
        '<h1>Steal the technique.<br><span class="a">Skip the trap.</span></h1>'
        '<p class="lede">Hans Sai&rsquo;s working research index: 229 study notes on '
        'generative art, printmaking, composition and technique, filed by <strong>what '
        'you can do with them</strong>, not by which shelf they sit on. '
        'Search everything, filter by theme, or pull the master lists of stealable '
        'techniques, avoid-list traps, palettes, open doorways and honest gaps.</p>'
        '<ul class="stats">'
        '<li><b>%d</b><span>notes</span></li>'
        '<li><b>~%dk</b><span>words</span></li>'
        '<li><b><em>%d</em></b><span>stealable techniques</span></li>'
        '<li><b><em>%d</em></b><span>avoid-list items</span></li>'
        '<li><b><em>%d</em></b><span>open doorways</span></li>'
        '</ul></div></section>'
        '<div class="wrap"><div class="searchzone"><div class="searchbox">'
        '<span class="mag">&#8981;</span>'
        '<input id="q" type="search" placeholder="Search titles, techniques, artists, ideas&hellip;" '
        'autocomplete="off" spellcheck="false" aria-label="Search all notes">'
        '</div><p class="searchmeta" id="searchmeta"></p></div>'
        '<div class="facets"><span class="facet-label">Theme</span>%s</div>'
        '<div class="facets"><span class="facet-label">Contains</span>%s'
        '<select class="sortsel" id="sortsel" aria-label="Sort notes">'
        '<option value="date">Recently studied</option>'
        '<option value="title">Title A&ndash;Z</option>'
        '<option value="words">Longest read</option>'
        '</select></div>'
        '<div class="rows" id="rows">%s</div>'
        '<div class="empty" id="empty" hidden>No notes match. Clear the search or loosen the filters.</div>'
        '</div>'
        % (stats["notes"], stats["kwords"], stats["techniques"],
           stats["avoid"], stats["doorways"], chips, fnchips,
           "\n".join(row_html)))
    cmdk = (
        '<div class="cmdk" id="cmdk"><div class="cmdk-box">'
        '<input id="cmdkInput" placeholder="Type to search all 229 notes&hellip;" autocomplete="off" spellcheck="false">'
        '<div class="cmdk-list" id="cmdkList"></div>'
        '<div class="cmdk-hint">&uarr;&darr; navigate &middot; &crarr; open &middot; esc close</div>'
        '</div></div>')
    return page_shell("MUSE: a research index of 229 study notes", body, "index",
                      extra_js=js + CMDK_FULL_JS + CANVAS_JS
                      ).replace("<script>", cmdk + "\n<script>")

# -------------------------------------------------------- aggregate views ---

AGG_JS = r"""
(function(){
  var q = document.getElementById('vq'), sel = {};
  function passTheme(el){
    var keys = Object.keys(sel);
    return !keys.length || sel[el.getAttribute('data-th')];
  }
  function apply(){
    var term = q.value.trim().toLowerCase(), shown = 0;
    document.querySelectorAll('.item,.palblock').forEach(function(el){
      var ok = passTheme(el) && (!term || el.getAttribute('data-txt').indexOf(term) >= 0);
      el.hidden = !ok;
      if (ok) shown++;
    });
    document.getElementById('vcount').innerHTML =
      'showing <b>' + shown + '</b> of TOTAL items';
    document.getElementById('vempty').hidden = shown > 0;
  }
  q.addEventListener('input', apply);
  document.querySelectorAll('.chip.theme').forEach(function(c){
    c.addEventListener('click', function(){
      var k = c.getAttribute('data-k');
      if (sel[k]) delete sel[k]; else sel[k] = 1;
      c.classList.toggle('on', !!sel[k]); apply();
    });
  });
  apply();
})();
"""


def build_agg(view_id, title, blurb, group_id, notes, active):
    accent = GROUP_COLOR[group_id]
    theme_counts = {}
    items = []
    for n in notes:
        for s in n["sections"]:
            if s["group"] != group_id:
                continue
            theme_counts[n["theme"]] = theme_counts.get(n["theme"], 0) + 1
            if group_id == "palette":
                items.append((n, s, None))
            else:
                for b in s["bullets"]:
                    items.append((n, s, b))
    items.sort(key=lambda t: (t[0]["title"].lower(),
                              t[1]["heading"].lower(), t[2] or ""))
    chips = "".join(
        '<button type="button" class="chip theme" data-k="%s" style="--h:%d">%s<span class="n">%d</span></button>'
        % (tid, THEME_HUE[tid], html.escape(THEME_BY_ID[tid][2]),
           theme_counts.get(tid, 0))
        for tid, _, _, _, _ in THEMES if theme_counts.get(tid))

    blocks = []
    for n, s, bullet in items:
        th = n["theme"]
        txt = (n["title"] + " " + s["heading"] + " " +
               (bullet if bullet else s["text"])).lower()
        srclink = ('<a href="notes/%s.html">%s</a> &middot; %s'
                   % (n["slug"], html.escape(n["title"]),
                      html.escape(THEME_BY_ID[th][2])))
        if bullet is None:
            src = ('<div class="src">%s &middot; %d MIN READ</div>'
                   % (html.escape(THEME_BY_ID[th][2]), n["minutes"]))
            blocks.append(
                '<section class="palblock" data-th="%s" data-txt="%s">'
                '<h3><a href="notes/%s.html">%s</a></h3>'
                '<div class="secname">%s</div>'
                '<div class="body">%s</div>%s</section>'
                % (th, html.escape(txt, quote=True), n["slug"],
                   html.escape(n["title"]), html.escape(s["heading"]),
                   s["html"], src))
        else:
            src = ('<div class="src"><span class="tt">%s</span> &middot; %s</div>'
                   % (html.escape(title.upper()), srclink))
            blocks.append(
                '<article class="item" data-th="%s" data-txt="%s">'
                '<div class="txt"><p>%s</p></div>%s</article>'
                % (th, html.escape(txt, quote=True),
                   render_inline(bullet), src))

    body = (
        '<div class="wrap" style="--vaccent:%s">'
        '<section class="vhero"><h1><span class="tick"></span>%s</h1><p>%s</p>'
        '<p class="vcount" id="vcount"></p></section>'
        '<div class="searchzone"><div class="searchbox"><span class="mag">&#8981;</span>'
        '<input id="vq" type="search" placeholder="Filter these items&hellip;" '
        'autocomplete="off" spellcheck="false" aria-label="Filter items"></div></div>'
        '<div class="facets"><span class="facet-label">Theme</span>%s</div>'
        '<div class="items">%s</div>'
        '<div class="empty" id="vempty" hidden>Nothing matches. Loosen the filters.</div>'
        '</div>'
        % (accent, html.escape(title), blurb, chips, "\n".join(blocks)))
    js = AGG_JS.replace("TOTAL", str(len(blocks))) + "\n" + \
        CMDK_JS.replace("INDEXROOT", "")
    return page_shell("MUSE: %s" % title, body, active, extra_js=js)


# ---------------------------------------------------------------- note page --

def build_note(n, notes_by_slug, date_order):
    th = n["theme"]
    tinfo = THEME_BY_ID[th]
    secs = n["sections"]

    toc = "".join(
        '<a class="g-%s" href="#%s">%s</a>'
        % (s["group"] or "x", s["anchor"], html.escape(s["heading"]))
        for s in secs)
    parts = []
    if n["catalogue_html"]:
        parts.append(n["catalogue_html"])
    if n["intro_html"]:
        parts.append(n["intro_html"])
    for s in secs:
        tag = "h2" if s["level"] == 2 else "h3"
        parts.append('<%s id="%s">%s</%s>' % (
            tag, s["anchor"], html.escape(s["heading"]), tag))
        if s["html"]:
            parts.append(s["html"])
    nbody = '<div class="nbody">%s</div>' % "\n".join(parts)

    fn_present = ", ".join(GROUP_LABEL[g] for g in
                           ("techniques", "avoid", "palette", "doorways", "gaps")
                           if g in n["groups"]) or "none"
    spec = (
        '<dl class="specs">'
        '<div><dt>Theme</dt><dd><span class="tdot" style="background:hsl(%d 72%% 62%%)"></span>%s</dd></div>'
        '<div><dt>Studied</dt><dd>%s</dd></div>'
        '<div><dt>Words</dt><dd>%d</dd></div>'
        '<div><dt>Read</dt><dd>~%d min</dd></div>'
        '<div><dt>Sections</dt><dd>%d</dd></div>'
        '<div><dt>Contains</dt><dd>%s</dd></div>'
        '</dl>'
        % (THEME_HUE[th], html.escape(tinfo[2]),
           n["date"] if n["date"] else "undated", n["words"],
           n["minutes"], len(secs), html.escape(fn_present)))

    # related: same theme, sharing functional groups first
    def rel_key(o):
        shared = len(set(o["groups"]) & set(n["groups"]))
        return (-shared, o["title"].lower())
    related = sorted(
        (o for o in notes_by_slug.values()
         if o["theme"] == th and o["slug"] != n["slug"]),
        key=rel_key)[:4]
    rel = ""
    if related:
        rel = ('<section class="related"><h2>More in %s</h2><div class="relgrid">%s</div></section>'
               % (html.escape(tinfo[2]), "".join(
                   '<a href="%s.html"><span class="rt">%s</span>'
                   '<span class="rm">%s &middot; %d MIN</span></a>'
                   % (o["slug"], html.escape(o["title"]),
                      o["date"] if o["date"] else "undated", o["minutes"])
                   for o in related)))

    idx = date_order.index(n["slug"])
    prev_n = notes_by_slug[date_order[idx - 1]] if idx > 0 else None
    next_n = notes_by_slug[date_order[idx + 1]] if idx + 1 < len(date_order) else None

    def pnlink(o, direction, cls):
        if not o:
            return '<span></span>'
        return ('<a class="%s" href="%s.html"><span class="dir">%s</span>'
                '<span class="t">%s</span></a>'
                % (cls, o["slug"], direction, html.escape(o["title"])))

    body = (
        '<div class="wrap"><p class="crumb"><a href="../index.html">INDEX</a> / '
        '<a href="../index.html?theme=%s">%s</a> / %s</p>'
        '<article class="note"><h1>%s</h1>%s'
        '<nav class="toc" aria-label="Sections">%s</nav>%s%s'
        '<nav class="pn">%s%s</nav></article></div>'
        % (th, html.escape(tinfo[2].upper()), html.escape(n["title"]),
           html.escape(n["title"]), spec, toc, nbody, rel,
           pnlink(prev_n, "&larr; Newer", "prev"),
           pnlink(next_n, "Older &rarr;", "next")))
    js = CMDK_JS.replace("INDEXROOT", "../")
    return page_shell("%s: %s" % ("MUSE", n["title"]), body, "", root="../",
                      extra_js=js)


# -------------------------------------------------------------------- main --

def main():
    slugs = sorted(f[:-3] for f in os.listdir(STUDY) if f.endswith(".md"))
    notes = []
    for slug in slugs:
        notes.append(parse_note(os.path.join(STUDY, slug + ".md"), slug))
    by_slug = {n["slug"]: n for n in notes}
    assert len(notes) == len(by_slug) == 229, len(notes)

    def bullet_count(gid):
        return sum(len(s["bullets"]) for n in notes for s in n["sections"]
                   if s["group"] == gid)

    stats = {
        "notes": len(notes),
        "kwords": round(sum(n["words"] for n in notes) / 1000),
        "techniques": bullet_count("techniques"),
        "avoid": bullet_count("avoid"),
        "doorways": bullet_count("doorways"),
    }

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "notes"))

    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index(notes, stats))
    for view_id, title, blurb, group_id in AGG_VIEWS:
        active = "palettes" if view_id == "palettes" else view_id
        with open(os.path.join(OUT, view_id + ".html"), "w", encoding="utf-8") as f:
            f.write(build_agg(view_id, title, blurb, group_id, notes, active))

    # newest first by study date; undated notes last, then title
    slugs_all = [n["slug"] for n in notes]
    dated = sorted(
        [s for s in slugs_all if by_slug[s]["date"]],
        key=lambda s: (by_slug[s]["date"], by_slug[s]["title"]), reverse=True)
    undated = sorted(
        [s for s in slugs_all if not by_slug[s]["date"]],
        key=lambda s: by_slug[s]["title"])
    date_order = dated + undated
    for n in notes:
        with open(os.path.join(OUT, "notes", n["slug"] + ".html"),
                  "w", encoding="utf-8") as f:
            f.write(build_note(n, by_slug, date_order))

    print("notes:", len(notes))
    print("words: %d (~%dk)" % (sum(n["words"] for n in notes), stats["kwords"]))
    for gid in ("techniques", "avoid", "palette", "doorways", "gaps"):
        if gid == "palette":
            c = sum(1 for n in notes for s in n["sections"] if s["group"] == gid)
            print("palettes: %d note-sections" % c)
        else:
            print("%s: %d bullets" % (gid, bullet_count(gid)))
    missing_themes = [n["slug"] for n in notes if not n["theme"]]
    print("missing theme:", missing_themes)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
