#!/usr/bin/env python3
"""Check catechisms.json for PDF-extraction damage and structural problems.

Run after any change to the data or to scraper.py:

    python validate_data.py

Exits non-zero if anything fails, so it can gate a commit or a deploy.

Every check here corresponds to damage that actually shipped: duplicated text
runs (Q31's answer repeated one phrase 38 times across 5716 characters),
teaching prose swallowed into the small italic attribution line, split
ligatures ("off ered"), and doubled whitespace in scripture references.
"""
import collections
import json
import os
import re
import sys

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catechisms.json")

EXPECTED_ENTRIES = 92          # 91 numbered cards + the seasonal Thanksgiving one
MAX_ATTRIBUTION = 200          # a citation, not a paragraph
MAX_ANSWER = 900
SHINGLE = 8                    # words; a repeat at this length is never accidental

# Genuine English that looks like a split ligature. Both are real phrases in
# the NASB text ("far off have been brought near", "cut off by the water").
LIGATURE_ALLOW = {"off have", "off by"}

# A spaced ellipsis is the cards' elision marker and must survive every rule
# here -- there are over 70 of them.
ELLIPSIS = re.compile(r"\.\s\.\s\.")
LIGATURE_SPLIT = re.compile(r"\b([A-Za-z]*(?:ff|ffi|ffl|fi|fl))\s+([a-z]{1,5})\b")
PUNCT_SPACE = re.compile(r"(?<![.\s])\s+[,.](?!\s*\.)")
DOUBLE_SPACE = re.compile(r"(?<!\.) {2,}")
DOT_LEADER = re.compile(r"\.\s?\.\s?\.\s?\.\s?\.\s?\.\s?\.")   # longer than an ellipsis
TRANSLATION_TAG = re.compile(r"\((?:NASB|KJV|ESV|NKJV|NIV)[;,]")

failures = []


def fail(entry, field, msg):
    failures.append(f"Q{entry}  [{field}]  {msg}")


def text_fields(c):
    yield "question", c["question"]
    yield "answer", c["answer"]
    yield "attribution", c["attribution"]
    for s in c["scriptures"]:
        yield f"scripture:{s['reference']}", s["text"]
        yield f"reference:{s['reference']}", s["reference"]


def max_repeat(text, n=SHINGLE):
    words = text.split()
    if len(words) < n:
        return 0, ""
    counts = collections.Counter(
        " ".join(words[i:i + n]) for i in range(len(words) - n + 1))
    phrase, count = counts.most_common(1)[0]
    return count, phrase


def main():
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    cats = data["catechisms"]

    # ── structure ──────────────────────────────────────────────────────
    if len(cats) != EXPECTED_ENTRIES:
        fail("-", "file", f"{len(cats)} entries, expected {EXPECTED_ENTRIES}")
    if data.get("total") != len(cats):
        fail("-", "file", f"total={data.get('total')} but {len(cats)} entries")

    numbers = [c["number"] for c in cats]
    expected = list(range(1, EXPECTED_ENTRIES)) + ["thanksgiving"]
    if numbers != expected:
        missing = set(expected) - set(numbers)
        extra = set(numbers) - set(expected)
        dupes = [n for n, k in collections.Counter(numbers).items() if k > 1]
        fail("-", "file", f"numbering off (missing={sorted(missing, key=str)} "
                          f"extra={sorted(extra, key=str)} duplicate={dupes})")

    for c in cats:
        n = c["number"]

        # A failed download used to be written out as a placeholder entry.
        if "error" in c:
            fail(n, "entry", f"carries a scrape error: {c['error']!r}")
        if not c["question"].strip():
            fail(n, "question", "empty")
        elif not c["question"].strip().endswith("?"):
            fail(n, "question", f"does not end in '?': ...{c['question'][-40:]!r}")
        if not c["answer"].strip():
            fail(n, "answer", "empty")
        if not c["scriptures"]:
            fail(n, "scriptures", "none")

        # ── extraction damage ──────────────────────────────────────────
        for field, value in text_fields(c):
            # Most cards carry no citation, so an empty attribution is normal.
            # The other fields are checked for emptiness individually above.
            if not value:
                continue

            hits = [m for m in LIGATURE_SPLIT.finditer(value)
                    if m.group(0).lower() not in LIGATURE_ALLOW]
            for m in hits:
                fail(n, field, f"split ligature: {m.group(0)!r}")

            m = DOUBLE_SPACE.search(value)
            if m:
                fail(n, field, f"doubled space near {value[max(0, m.start()-25):m.end()+25]!r}")
            m = PUNCT_SPACE.search(value)
            if m:
                fail(n, field, f"space before punctuation: {m.group(0)!r}")
            if re.search(r"\s+[”)?]", value):
                fail(n, field, "space before a closing quote, paren, or question mark")
            if re.search(r"[“(]\s", value):
                fail(n, field, "space after an opening quote or paren")

        # ── duplicated text runs ───────────────────────────────────────
        for field in ("answer", "attribution"):
            count, phrase = max_repeat(c[field])
            if count > 1:
                fail(n, field, f"phrase repeats {count}x: {phrase[:60]!r}")

        # ── misclassified content ──────────────────────────────────────
        if len(c["attribution"]) > MAX_ATTRIBUTION:
            fail(n, "attribution", f"{len(c['attribution'])} chars — prose swallowed "
                                   f"into the citation line?")
        if len(c["answer"]) > MAX_ANSWER:
            fail(n, "answer", f"{len(c['answer'])} chars — page furniture in the answer?")
        if DOT_LEADER.search(c["answer"]):
            fail(n, "answer", "contains a dot-leader run (a layout table, not prose)")
        if "Question:" in c["answer"]:
            fail(n, "answer", "contains a study prompt ('Question:')")
        for s in c["scriptures"]:
            if s["text"].startswith("(Note:"):
                fail(n, f"scripture:{s['reference']}", "starts with an editorial note")
            if not s["reference"].strip():
                fail(n, "reference", "empty")

    # ── report ─────────────────────────────────────────────────────────
    ellipses = sum(len(ELLIPSIS.findall(v)) for c in cats for _, v in text_fields(c) if v)
    print(f"{len(cats)} entries, "
          f"{sum(len(c['scriptures']) for c in cats)} scriptures, "
          f"{ellipses} elisions preserved")

    if failures:
        print(f"\n{len(failures)} problem(s):\n")
        for f in failures:
            print(f"  {f}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
