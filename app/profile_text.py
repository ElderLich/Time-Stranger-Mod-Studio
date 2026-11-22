"""Field Guide profile layout for the game's multiline text table."""
import re
import textwrap
import unicodedata
from functools import lru_cache


# Horizontal advances from the English commonfont, in thousandths of an em.
# The printable ASCII range starts at space. No installed font is required.
_ASCII_ADVANCES = (
    345, 400, 500, 690, 690, 1000, 741, 345, 400, 400, 500, 690, 345, 476, 345, 400,
    690, 690, 690, 690, 690, 690, 690, 690, 690, 690, 400, 400, 690, 690, 690, 690,
    891, 727, 722, 729, 791, 678, 636, 784, 792, 342, 484, 706, 621, 934, 789, 806,
    701, 802, 726, 698, 624, 792, 710, 956, 666, 632, 683, 400, 400, 400, 690, 500,
    400, 602, 649, 584, 656, 612, 355, 644, 652, 290, 302, 575, 293, 905, 652, 649,
    649, 656, 422, 558, 391, 652, 555, 810, 531, 576, 546, 400, 345, 400, 500,
)
# 27.4 em best approximates the word breaks in the English patch table.
# Stock manually laid-out lines reach 29.856 em. Keep those breaks on export.
_WRAP_ADVANCE = 27400
_AUTHORED_ADVANCE = 30000
_HEADING = re.compile(r"(■[ \t]*Effects\s+of\s+the\s+X\s+Antibody\s+on\s+[^■:]+?\bDigiCore:)", re.I)
_PUNCTUATION = str.maketrans({"‘": "'", "’": "'", "`": "'", "“": '"', "”": '"',
                              "\u00a0": " ", "\u202f": " ", "\u200b": "", "\ufeff": ""})
_SPACED_SUFFIX = re.compile(r"(?<=[\w)])[^\S\n]*'[^\S\n]*(?=(?:s|t|re|ve|ll|d|m)\b)", re.I)


def _advance(text):
    return sum(_ASCII_ADVANCES[n - 32] if 32 <= n < 127 else 1000 for n in map(ord, text))


def _wrap_words(text):
    lines = []
    line = []
    advance = 0
    for word in text.split():
        word_width = _advance(word)
        next_width = advance + (_ASCII_ADVANCES[0] if line else 0) + word_width
        if line and next_width > _WRAP_ADVANCE:
            lines.append(" ".join(line))
            line = []
            next_width = word_width
        line.append(word)
        advance = next_width
    if line:
        lines.append(" ".join(line))
    return lines


def _layout_lines(text):
    lines = []
    for line in text.split("\n"):
        if _advance(line) <= _AUTHORED_ADVANCE:
            lines.append(line)
        else:
            lines.extend(_wrap_words(line))
    return "\n".join(lines)


def _format_english_paragraph(paragraph):
    # Captured headings alternate with prose. A heading may cross an old hard wrap.
    preface, *sections = _HEADING.split(paragraph)
    if not sections:
        return _layout_lines(preface)
    blocks = []
    if preface.strip():
        if preface.rstrip(" \t").endswith("\n"):
            blocks.append(_layout_lines(preface.rstrip("\n ")))
        else:
            blocks.append("\n".join(_wrap_words(preface)))

    for heading, body in zip(sections[::2], sections[1::2]):
        if "\n" in heading and body.startswith(" ") and not preface.strip():
            # A few authored headings (e.g. UlforceVeedramon) share their
            # continuation line with the first sentence. Keep that layout.
            blocks.append(_layout_lines(heading + body))
            continue
        title = " ".join(heading.split()).replace("■ ", "■")
        block = _layout_lines(title)
        if body.strip():
            if body.lstrip(" \t").startswith("\n"):
                prose = _layout_lines(body.lstrip(" \t").removeprefix("\n").rstrip("\n"))
            else:
                prose = "\n".join(_wrap_words(body))
            block += "\n" + prose
        blocks.append(block)
    return "\n\n".join(blocks)


# Widths are in thousandths of an em. These targets approximate the 95th
# percentile of lines in the 452 retail Field Guide entries per locale.
_LOCALIZED_TARGET = {"00": 24000, "02": 27200, "03": 23100, "04": 25000,
                     "05": 27400, "07": 27400, "09": 25500, "10": 23000,
                     "11": 23000, "30": 28500}
# Wider, hand-set retail lines can remain as authored. Italian and Portuguese
# have isolated multi-sentence stock lines far outside the normal panel width.
_LOCALIZED_AUTHORED = {"00": 27000, "02": 30000, "03": 30700, "04": 29100,
                       "05": 30000, "07": 32000, "09": 27600, "10": 28300,
                       "11": 28300, "30": 30300}
# The remaining locales share the English commonfont. The Korean and Chinese
# commonfont files carry their own widths for ASCII embedded in CJK prose.
_CJK_ASCII_ADVANCES = {
    "09": (
        500, 371, 381, 644, 660, 940, 819, 273, 394, 394, 495, 699, 362, 679, 362, 501,
        711, 514, 640, 659, 664, 661, 670, 595, 677, 670, 365, 365, 506, 679, 511, 644,
        980, 808, 749, 800, 783, 710, 686, 829, 793, 329, 576, 771, 659, 917, 801, 830,
        724, 830, 744, 716, 703, 770, 806, 967, 738, 741, 688, 414, 501, 414, 549, 495,
        250, 679, 720, 661, 720, 691, 390, 711, 683, 329, 338, 664, 329, 932, 683, 691,
        720, 720, 464, 616, 390, 683, 636, 829, 615, 638, 601, 467, 411, 467, 921,
    ),
    "10": (
        333, 306, 361, 630, 602, 880, 778, 288, 389, 389, 444, 759, 288, 333, 288, 500,
        660, 660, 660, 660, 660, 660, 660, 660, 660, 660, 288, 288, 815, 759, 815, 565,
        889, 787, 657, 750, 824, 620, 611, 824, 731, 296, 547, 694, 509, 981, 824, 907,
        611, 907, 620, 583, 667, 815, 796, 1157, 713, 713, 759, 380, 500, 380, 556, 500,
        288, 616, 667, 565, 667, 620, 341, 611, 620, 278, 401, 602, 313, 944, 620, 667,
        667, 667, 398, 500, 404, 620, 546, 898, 574, 574, 519, 315, 269, 315, 769,
    ),
    "11": (
        333, 306, 361, 630, 602, 880, 778, 222, 389, 389, 444, 759, 288, 333, 288, 500,
        660, 660, 660, 660, 660, 660, 660, 660, 660, 660, 288, 288, 814, 759, 814, 564,
        889, 787, 657, 750, 824, 620, 611, 824, 730, 296, 547, 694, 509, 980, 824, 907,
        611, 907, 620, 583, 667, 814, 796, 1157, 713, 713, 759, 380, 500, 380, 556, 500,
        333, 616, 667, 564, 667, 620, 341, 611, 620, 278, 401, 602, 313, 944, 620, 667,
        667, 667, 398, 500, 404, 620, 546, 898, 574, 574, 519, 314, 269, 314, 769,
    ),
}
_LATIN_EXTRA_ADVANCES = {"¡": 400, "º": 315, "¿": 690, "ß": 640, "Œ": 934,
                        "œ": 985, "–": 500, " ": 345}


@lru_cache(maxsize=4096)
def _localized_glyph_advance(char, locale):
    if unicodedata.category(char) in {"Mn", "Me", "Cf"}:
        return 0
    advances = _CJK_ASCII_ADVANCES.get(locale, _ASCII_ADVANCES)
    if 32 <= ord(char) < 127:
        return advances[ord(char) - 32]
    if locale not in _CJK_ASCII_ADVANCES:
        base = unicodedata.normalize("NFD", char)[0]
        if base.isascii() and base.isalpha():
            return _ASCII_ADVANCES[ord(base) - 32]
        return _LATIN_EXTRA_ADVANCES.get(char, 1000)
    return 1000


def _localized_advance(text, locale):
    return sum(_localized_glyph_advance(char, locale) for char in text)


def _boundary_parts(text, kind):
    from PyQt6.QtCore import QTextBoundaryFinder

    finder = QTextBoundaryFinder(kind, text)
    # Qt offsets count UTF-16 units. Use a byte view to preserve astral glyphs.
    utf16 = text.encode("utf-16-le")
    start = 0
    while (end := finder.toNextBoundary()) >= 0:
        yield utf16[2 * start:2 * end].decode("utf-16-le")
        start = end


def _wrap_localized_line(text, locale, limit):
    from PyQt6.QtCore import QTextBoundaryFinder

    if locale in {"00", "10", "11"}:
        # Unicode line boundaries keep closing punctuation with the previous
        # character and opening brackets with the following character.
        parts = _boundary_parts(text, QTextBoundaryFinder.BoundaryType.Line)
    else:
        # Korean retail copy breaks at spaces between eojeol. Retain punctuation
        # and nonbreaking spaces in French and the other Latin locales as well.
        parts = re.findall(r"[^ \t]+[ \t]*|[ \t]+", text)
    lines = []
    line = ""
    for part in parts:
        if line and _localized_advance((line + part).rstrip(" \t"), locale) > limit:
            lines.append(line.rstrip(" \t"))
            line = ""
        if _localized_advance(part.rstrip(" \t"), locale) > limit:
            for cluster in _boundary_parts(part, QTextBoundaryFinder.BoundaryType.Grapheme):
                if line and _localized_advance(line + cluster, locale) > limit and not cluster.isspace():
                    lines.append(line)
                    line = ""
                line += cluster
        else:
            line += part
    if line:
        lines.append(line.rstrip(" \t"))
    return "\n".join(lines)


def format_profile_text_for_game(text: str, *, english: bool = True, locale: str | None = None) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    if not text.strip():
        return ""
    if locale in _LOCALIZED_TARGET:
        limit = _LOCALIZED_TARGET[locale]
        keep_width = _LOCALIZED_AUTHORED[locale] if "\n" in text else limit
        return "\n".join(line if _localized_advance(line, locale) <= keep_width
                         else _wrap_localized_line(line, locale, limit)
                         for line in text.split("\n"))
    if english:
        text = _SPACED_SUFFIX.sub("'", text.translate(_PUNCTUATION))
    paragraphs = re.split(r"\n(?:[ \t]*\n)+", text)
    if english:
        return "\n\n".join(_format_english_paragraph(p) for p in paragraphs)
    # Other language folders keep their punctuation and existing wrap convention.
    return "\n\n".join("\n".join(wrapped for line in p.splitlines()
                                 for wrapped in textwrap.wrap(" ".join(line.split()), width=50,
                                                              break_long_words=False, break_on_hyphens=False))
                       for p in paragraphs)


def profile_line_stats(text: str) -> str:
    lines = text.splitlines() or [""]
    return f"Lines: {len(lines)} | Longest line: {max(map(len, lines))} characters"
