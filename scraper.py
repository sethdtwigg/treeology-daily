#!/usr/bin/env python3
"""
Treeology Catechism Scraper — improved parser
Run: pip install pypdf requests && python scraper.py
"""

import json, re, sys, io, urllib.request

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

def fetch_pdf_text(url):
    import pypdf
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    reader = pypdf.PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

def clean(t):
    fixes = [
        ('/f_i  ','fi'),('/f_i','fi'),('/f_l','fl'),
        ('oﬀ  ','off'),('oﬀ','off'),
        ('ofﬁ  ce','office'),('ﬁ  ','fi'),('ﬁ','fi'),('ﬂ','fl'),
        ('sacri/f_i  ces','sacrifices'),('sacri/f_i  ce','sacrifice'),
        ('/f_i  rst','first'),('justi/f_i  ','justifi'),
        ('sancti/f_i  ','sanctifi'),('cruci/f_i  ','crucifi'),
        ('con/f_i  rmed','confirmed'),('beneﬁ  ts','benefits'),
        ('beneﬁts','benefits'),('Justiﬁ  cation','Justification'),
        ('Sanctiﬁ  cation','Sanctification'),('justiﬁ  ed','justified'),
        ('sancti/f_i  cation','sanctification'),('justi/f_i  es','justifies'),
        ('glori/f_i  ed','glorified'),('sacriﬁ  ce','sacrifice'),
    ]
    for old, new in fixes:
        t = t.replace(old, new)
    t = re.sub(r'(\w)-\n(\w)', r'\1\2', t)
    return t

def parse(raw, num):
    raw = clean(raw)
    lines = [l.strip() for l in raw.splitlines() if l.strip()]

    # Question = everything up to first scripture verse
    q_end = len(lines)
    for i, line in enumerate(lines):
        if TRANS_PAT.search(line):
            q_end = i
            break
    question_raw = ' '.join(lines[:q_end])
    # Trim to actual question (up to first ?)
    m = re.match(r'^(.+?\?)', question_raw)
    question = m.group(1).strip() if m else question_raw.strip()

    # Find the number marker line that precedes the answer
    num_str = str(num)
    answer_start = None
    for i, line in enumerate(lines):
        if re.match(r'^\s*' + re.escape(num_str) + r'\s*$', line):
            answer_start = i + 1
            break
        if re.match(r'^\s*' + re.escape(num_str) + r'\s+\S', line):
            lines[i] = re.sub(r'^\s*' + re.escape(num_str) + r'\s+', '', line).strip()
            answer_start = i
            break

    # Scriptures: between question end and answer start
    scr_lines = lines[q_end : answer_start] if answer_start else lines[q_end:]
    scr_text  = ' '.join(scr_lines)
    scriptures = []
    parts = re.split(r'(\((?:NASB|KJV|ESV|NKJV|NIV)[^)]+\))', scr_text)
    i = 0
    while i < len(parts) - 1:
        verse = parts[i].strip()
        ref   = parts[i+1].strip()
        if ref and TRANS_PAT.match(ref):
            inner = ref[1:-1]
            m2 = re.match(r'(NASB|KJV|ESV|NKJV|NIV)[;,]\s*(.+)', inner)
            if m2 and verse and len(verse) > 10:
                scriptures.append({
                    'reference':   m2.group(2).strip(),
                    'translation': m2.group(1).strip(),
                    'text':        re.sub(r'\s+', ' ', verse).strip()
                })
            i += 2
        else:
            i += 1

    # Answer + attribution
    ans_lines = lines[answer_start:] if answer_start is not None else []
    attr_pat = re.compile(r'^\((?:Westminster|Adapted|C\.H\.|Belgic|Second Hel)', re.IGNORECASE)
    note_pat = re.compile(r'^\(Note:', re.IGNORECASE)
    attr_parts, ans_parts = [], []
    in_attr = False
    for line in ans_lines:
        if attr_pat.match(line) or in_attr:
            attr_parts.append(line)
            in_attr = True
        elif note_pat.match(line):
            pass
        else:
            ans_parts.append(line)

    answer      = re.sub(r'\s+', ' ', ' '.join(ans_parts)).strip()
    attribution = re.sub(r'\s+', ' ', ' '.join(attr_parts)).strip()

    return {
        'number':      num,
        'question':    question,
        'answer':      answer,
        'scriptures':  scriptures,
        'attribution': attribution,
        'raw_text':    raw,
    }

def main():
    try:
        import pypdf
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pypdf'])
        import pypdf

    print(f"Downloading {len(PDF_URLS)} PDFs...\n")
    results = []
    errors  = []

    for idx, (num, url) in enumerate(PDF_URLS):
        label = f"Q{num}" if num != 'thanksgiving' else 'Thanksgiving'
        print(f"[{idx+1:3}/{len(PDF_URLS)}] {label}: ", end='', flush=True)
        try:
            raw  = fetch_pdf_text(url)
            entry = parse(raw, num)
            results.append(entry)
            print(f"✅  {entry['question'][:55]}")
        except Exception as e:
            print(f"❌  {e}")
            errors.append({'number': num, 'url': url, 'error': str(e)})
            results.append({
                'number': num, 'question': f'[Q{num} — failed]',
                'answer': '', 'scriptures': [], 'attribution': '',
                'raw_text': '', 'error': str(e)
            })

    out = {'total': len(results), 'catechisms': results}
    with open('catechisms.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*55}")
    print(f"Done — {len(results)-len(errors)} OK, {len(errors)} failed")
    print(f"Output: catechisms.json")
    if errors:
        print("\nFailed:")
        for e in errors:
            print(f"  Q{e['number']}: {e['error']}")

if __name__ == '__main__':
    main()