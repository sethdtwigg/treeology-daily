#!/usr/bin/env python3
"""
Treeology Catechism Scraper

Reads the cards in Catechism_PDFs/ (falling back to the network for any that
are missing) and writes catechisms.json next to this file.

    pip install -r requirements.txt
    python scraper.py
    python validate_data.py
"""

import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

PDF_URLS = [
    (1,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-1_2.pdf"),
    (2,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-2_2.pdf"),
    (3,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-3.pdf"),
    (4,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-4.pdf"),
    (5,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-5_2.pdf"),
    (6,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-6.pdf"),
    (7,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-7.pdf"),
    (8,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-8.pdf"),
    (9,  "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-9.pdf"),
    (10, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-10.pdf"),
    (11, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-11.pdf"),
    (12, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-12.pdf"),
    (13, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-13.pdf"),
    (14, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-14.pdf"),
    (15, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-15.pdf"),
    (16, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-16.pdf"),
    (17, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-17.pdf"),
    (18, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-18.pdf"),
    (19, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-19.pdf"),
    (20, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-20.pdf"),
    (21, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-21.pdf"),
    (22, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-22.pdf"),
    (23, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-23.pdf"),
    (24, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-24.pdf"),
    (25, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-25_2.pdf"),
    (26, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-26.pdf"),
    (27, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-27.pdf"),
    (28, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-28_2.pdf"),
    (29, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-29.pdf"),
    (30, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-30.pdf"),
    (31, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-31_2.pdf"),
    (32, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-32.pdf"),
    (33, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-33.pdf"),
    (34, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-34.pdf"),
    (35, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-35.pdf"),
    (36, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-36.pdf"),
    (37, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-37.pdf"),
    (38, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-38_2.pdf"),
    (39, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-39.pdf"),
    (40, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-40.pdf"),
    (41, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-41.pdf"),
    (42, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-42.pdf"),
    (43, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-43.pdf"),
    (44, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-44.pdf"),
    (45, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-45.pdf"),
    (46, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-Cardl-Number-46.pdf"),
    (47, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-47.pdf"),
    (48, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-48.pdf"),
    (49, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-49b.pdf"),
    (50, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-50.pdf"),
    (51, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-51.pdf"),
    (52, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-52.pdf"),
    (53, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-53.pdf"),
    (54, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-54.pdf"),
    (55, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-55.pdf"),
    (56, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-56.pdf"),
    (57, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-57.pdf"),
    (58, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-58.pdf"),
    (59, "https://www.mountcalvarybaptist.org/site/user/files/49/Card-Number-59_2.pdf"),
    (60, "https://www.mountcalvarybaptist.org/site/user/files/49/Card-Number-60_2.pdf"),
    (61, "https://www.mountcalvarybaptist.org/site/user/files/49/Card-Number-61.pdf"),
    (62, "https://www.mountcalvarybaptist.org/site/user/files/49/Card-Number-62.pdf"),
    (63, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-63.pdf"),
    (64, "https://www.mountcalvarybaptist.org/site/user/files/49/Question-64.pdf"),
    (65, "https://www.mountcalvarybaptist.org/site/user/files/49/Card-Number-65.pdf"),
    (66, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-66.pdf"),
    (67, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-67.pdf"),
    (68, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-68.pdf"),
    (69, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-69.pdf"),
    (70, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-70.pdf"),
    (71, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-71.pdf"),
    (72, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-72.pdf"),
    (73, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-73.pdf"),
    (74, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-74.pdf"),
    (75, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-75.pdf"),
    (76, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-76.pdf"),
    (77, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-77.pdf"),
    (78, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-78.pdf"),
    (79, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-79.pdf"),
    (80, "https://www.mountcalvarybaptist.org/site/user/files/49/Catechism-80.pdf"),
    (81, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-Number-81_2.pdf"),
    (82, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-82.pdf"),
    (83, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-83.pdf"),
    (84, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-84.pdf"),
    (85, "https://www.mountcalvarybaptist.org/site/user/files/46/Final-number-85-_002_.pdf"),
    (86, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-86.pdf"),
    (87, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-87.pdf"),
    (88, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-88.pdf"),
    (89, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-89.pdf"),
    (90, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-90b.pdf"),
    (91, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-91b.pdf"),
    ("thanksgiving", "https://www.mountcalvarybaptist.org/site/user/files/49/Thanksgiving.pdf"),
]

TRANS_PAT = re.compile(r'\((NASB|KJV|ESV|NKJV|NIV)[;,\s]')

# Where download.py puts the cards, and where we read them from by preference.
PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Catechism_PDFs")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catechisms.json")


def local_pdf_path(num, url):
    return os.path.join(PDF_DIR, f"{str(num).zfill(2)}_{url.split('/')[-1]}")


def fetch_pdf_text(url, num=None):
    """Prefer an already-downloaded card; only hit the network if it is absent.

    Re-fetching all 92 PDFs every run is slow, rude to the host, and turns a
    single transient failure into a placeholder entry (see main)."""
    import pypdf
    data = None
    if num is not None:
        path = local_pdf_path(num, url)
        if os.path.exists(path):
            data = open(path, "rb").read()
    if data is None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        last = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                break
            except (urllib.error.URLError, TimeoutError) as e:
                last = e
                time.sleep(2 ** attempt)
        if data is None:
            raise last
    reader = pypdf.PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


# Extraction splits a ligature from the rest of its word: "oﬀ  ered" -> "off ered",
# "ﬂ  esh" -> "fl esh". The same shape occurs legitimately when a real word
# follows ("far off have", "cut off by"), so the only reliable discriminator is
# whether the piece to the right is itself a word. Verified against all 91 cards:
# 20 genuine joins, and exactly those two phrases correctly left alone.
FOLLOWING_WORDS = {
    'a', 'all', 'also', 'an', 'and', 'any', 'are', 'as', 'at', 'back', 'be', 'because',
    'been', 'before', 'being', 'both', 'but', 'by', 'came', 'can', 'come', 'could',
    'did', 'do', 'does', 'done', 'down', 'each', 'even', 'ever', 'every', 'first',
    'for', 'from', 'get', 'give', 'go', 'goes', 'had', 'has', 'have', 'he', 'her',
    'here', 'him', 'his', 'how', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'last',
    'let', 'like', 'made', 'make', 'man', 'many', 'may', 'me', 'men', 'might', 'more',
    'most', 'much', 'must', 'my', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'one',
    'only', 'or', 'other', 'our', 'out', 'over', 'own', 'said', 'same', 'say', 'see',
    'shall', 'she', 'should', 'since', 'so', 'some', 'still', 'such', 'than', 'that',
    'the', 'their', 'them', 'then', 'there', 'these', 'they', 'this', 'those', 'though',
    'through', 'thus', 'to', 'too', 'two', 'under', 'unto', 'up', 'upon', 'us', 'very',
    'was', 'we', 'well', 'were', 'what', 'when', 'where', 'which', 'while', 'who',
    'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your',
}
LIGATURE_SPLIT = re.compile(r'([A-Za-z]*)(ff|ffi|ffl|fi|fl)\s+([a-z]{1,5})\b')


def _join_ligature(m):
    pre, lig, tail = m.groups()
    if tail in FOLLOWING_WORDS:
        return m.group(0)
    return pre + lig + tail

# Space before a comma or period — but never inside a spaced ellipsis. The cards
# use ". . ." for elisions and a naive rule destroys every one of them.
PUNCT_SPACE = re.compile(r'(?<![.\s])\s+([,.])(?!\s*\.)')


def fix_ligatures(t):
    for bad, good in [('ﬁ', 'fi'), ('ﬂ', 'fl'), ('ﬀ', 'ff'), ('ﬃ', 'ffi'), ('ﬄ', 'ffl'),
                      ('/f_i', 'fi'), ('/f_l', 'fl')]:
        t = t.replace(bad, good)
    # The previous rule required *two* spaces and only covered fl/fi, so every
    # ff/ffi/ffl case ("off ered", "suff ered", "scoff s") survived into the data.
    t = LIGATURE_SPLIT.sub(_join_ligature, t)
    t = re.sub(r'(\w)-\n(\w)', r'\1\2', t)
    t = re.sub(r'(\w) -\n(\w)', r'\1\2', t)
    return t


def tidy(t):
    """Normalise whitespace and the punctuation spacing the cards extract with."""
    if not t:
        return ''
    t = LIGATURE_SPLIT.sub(_join_ligature, t)
    t = t.replace('“ ', '“')
    t = re.sub(r'\s+”', '”', t)
    t = re.sub(r'\(\s+', '(', t)
    t = re.sub(r'\s+\)', ')', t)
    t = re.sub(r'\s+\?', '?', t)
    t = PUNCT_SPACE.sub(r'\1', t)
    t = re.sub(r'(?<!\.) {2,}', ' ', t)   # collapse runs, but keep ". . ."
    return t.strip()


def dedup_runs(t, n=8):
    """Cut at the first n-word shingle that repeats an earlier one.

    Several source PDFs carry overlapping text layers, so extraction emits the
    same phrase dozens of times. Without this the repetition lands in the data
    and renders verbatim in the app."""
    w = t.split()
    seen = {}
    for i in range(len(w) - n + 1):
        s = ' '.join(w[i:i + n])
        if s in seen:
            return ' '.join(w[:i]).strip()
        seen[s] = i
    return t


def parse(raw, num):
    raw = fix_ligatures(raw)
    lines = [l.strip() for l in raw.splitlines() if l.strip()]

    # Question: up to first scripture
    q_end = len(lines)
    for i, line in enumerate(lines):
        if TRANS_PAT.search(line):
            q_end = i
            break
    question_raw = ' '.join(lines[:q_end])
    m = re.match(r'^(.+?\?)', question_raw)
    question = m.group(1).strip() if m else question_raw.strip()

    # Find the number marker that separates scriptures from the answer.
    # Search only from q_end onward and require the line to be exactly the
    # number: several cards quote verse-numbered passages ("1 Then I saw a new
    # heaven...", "5 The rest of the dead..."), and a card numbered 1-6 would
    # otherwise split on the verse number and lose every scripture.
    num_str = str(num)
    marker = re.compile(r'^\s*' + re.escape(num_str) + r'\s*$', re.IGNORECASE)
    inline = re.compile(r'^\s*' + re.escape(num_str) + r'\s+(\S.*)$', re.IGNORECASE)
    answer_start = None
    for i in range(q_end, len(lines)):
        if marker.match(lines[i]):
            answer_start = i + 1
            break
        m2 = inline.match(lines[i])
        if m2:
            lines[i] = m2.group(1).strip()
            answer_start = i
            break

    # Scriptures: between question and answer
    scr_lines = lines[q_end:answer_start] if answer_start is not None else lines[q_end:]
    scr_text = ' '.join(scr_lines)

    scriptures = []
    parts = re.split(r'(\((?:NASB|KJV|ESV|NKJV|NIV)[^)]+\))', scr_text)
    i = 0
    while i < len(parts) - 1:
        verse = parts[i].strip()
        ref_tag = parts[i + 1].strip()
        if ref_tag and TRANS_PAT.match(ref_tag):
            inner = ref_tag[1:-1]
            m2 = re.match(r'(NASB|KJV|ESV|NKJV|NIV)[;,]\s*(.+)', inner)
            if m2:
                # Editorial notes are printed alongside the verses; they are not
                # scripture and must not be shown to the reader as though they were.
                verse = re.sub(r'^\(Note:[^)]*\)\s*', '', verse).strip()
                if verse and len(verse) > 10:
                    scriptures.append({
                        'reference':   re.sub(r'\s+', ' ', m2.group(2)).strip(),
                        'translation': m2.group(1).strip(),
                        'text':        tidy(re.sub(r'\s+', ' ', verse)),
                    })
                else:
                    print(f"    [skip] {num}: empty/short verse for {ref_tag}", file=sys.stderr)
            else:
                print(f"    [skip] {num}: unparsed tag {ref_tag}", file=sys.stderr)
            i += 2
        else:
            i += 1

    # Answer and attribution.
    ans_lines = lines[answer_start:] if answer_start is not None else []

    # Allow whitespace after the paren: cards print "( Westminster Shorter
    # Catechism , Q. 26)" and the old anchored pattern silently missed those,
    # leaving the citation stranded in the answer body.
    attr_pat = re.compile(r'^\(\s*(?:Westminster|Adapted|C\.\s*H\.|Belgic|Second Hel|Drawn|Note:)', re.I)

    attr_parts, ans_parts = [], []
    for line in ans_lines:
        # Only the citation itself is attribution. The previous version set a
        # sticky flag that never reset, so every following line — the card's
        # teaching note — was swallowed into the small italic credit line.
        (attr_parts if attr_pat.match(line) and not attr_parts else ans_parts).append(line)

    answer = tidy(dedup_runs(re.sub(r'\s+', ' ', ' '.join(ans_parts))))
    attribution = tidy(re.sub(r'\s+', ' ', ' '.join(attr_parts)))

    return {
        'number':      num,
        'question':    tidy(question),
        'answer':      answer,
        'scriptures':  scriptures,
        'attribution': attribution,
    }


def main():
    try:
        import pypdf  # noqa: F401  (probe only)
    except ImportError:
        sys.exit("pypdf is required. Install it with:  pip install -r requirements.txt")

    print(f"Reading {len(PDF_URLS)} catechism cards...\n")
    results, errors = [], []

    for idx, (num, url) in enumerate(PDF_URLS):
        label = f"Q{num}" if num != 'thanksgiving' else 'Thanksgiving'
        print(f"[{idx+1:3}/{len(PDF_URLS)}] {label}: ", end='', flush=True)
        try:
            entry = parse(fetch_pdf_text(url, num), num)
            results.append(entry)
            print(f"OK   {entry['question'][:60]}")
        except Exception as e:
            print(f"FAIL {e}")
            errors.append(num)

    # Never overwrite good data with a partial run: a failed download used to
    # become a "[Q5 - download failed]" placeholder that shipped to the app,
    # with the process still exiting 0 so CI saw nothing wrong.
    if errors:
        print(f"\n{len(errors)} card(s) failed: {errors}")
        print(f"{OUT_PATH} left unchanged.")
        return 1

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump({'total': len(results), 'catechisms': results}, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"\n{'='*55}")
    print(f"Done - {len(results)} cards written to {OUT_PATH}")
    print("Now run:  python validate_data.py")
    return 0


if __name__ == '__main__':
    # Emoji in status output crashes on a cp1252 console (and the old except
    # branch printed another emoji, so the handler raised too and no JSON was
    # ever written). Plain ASCII markers, plus a UTF-8 stdout for the content.
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())
