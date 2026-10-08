"""Furigana for the practice page, using SudachiPy (installed under ./vendor).

segments("法律上、学校は") -> [["法律", "ほうりつ"], ["上", "じょう"], ["、学校は", None]]
Readings sit only on the kanji part of a word, so okurigana stay plain: 食べる -> [["食", "た"], ["べる", None]].
"""
import re
import sys
import threading
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))

KANJI = "㐀-䶿一-鿿豈-﫿々〆〇ヶ"
HAS_KANJI = re.compile(f"[{KANJI}]")
RUNS = re.compile(f"[{KANJI}]+|[^{KANJI}]+")

_lock = threading.Lock()
_tok = None


def _tokenizer():
    global _tok
    if _tok is None:
        from sudachipy import dictionary, tokenizer  # noqa: PLC0415 (lazy: dictionary load is slow)

        _tok = (dictionary.Dictionary().create(), tokenizer.Tokenizer.SplitMode.B)
    return _tok


def available():
    try:
        with _lock:
            _tokenizer()
        return True
    except Exception:  # missing vendor/ or dictionary
        return False


def _hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def _align(surface, reading):
    """Split a word into [(text, reading|None)] so only kanji runs carry a reading."""
    runs = RUNS.findall(surface)
    pattern = "".join("(.+?)" if HAS_KANJI.match(r[0]) else re.escape(_hira(r)) for r in runs)
    m = re.fullmatch(pattern, reading)
    if not m:
        return [[surface, reading]]
    out, g = [], 1
    for r in runs:
        if HAS_KANJI.match(r[0]):
            out.append([r, m.group(g)])
            g += 1
        else:
            out.append([r, None])
    return out


@lru_cache(maxsize=8192)
def _segments(text):
    with _lock:
        tok, mode = _tokenizer()
        morphemes = [(m.surface(), m.reading_form()) for m in tok.tokenize(text, mode)]
    out = []
    for surface, kata in morphemes:
        reading = _hira(kata or "")
        if HAS_KANJI.search(surface) and reading and reading != surface:
            parts = _align(surface, reading)
        else:
            parts = [[surface, None]]
        for text_, r in parts:
            if r is None and out and out[-1][1] is None:
                out[-1][0] += text_  # merge neighbouring plain text
            else:
                out.append([text_, r])
    assert "".join(s for s, _ in out) == text
    return tuple(tuple(p) for p in out)


def segments(text):
    return [list(p) for p in _segments(text)]
