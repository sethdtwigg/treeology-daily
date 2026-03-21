#!/usr/bin/env python3
"""
Treeology Catechism Scraper
Downloads all 91 catechism PDFs and extracts content into catechisms.json
Run: pip install requests pypdf && python scraper.py
"""

import json
import re
import sys
import urllib.request
import io

# Exact URLs from the church website, in order
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
    (85, "https://www.mountcalvarybaptist.org/site/user/files/46/Final-number-85-_002_.pdf"),  # note: /46/ not /49/
    (86, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-86.pdf"),
    (87, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-87.pdf"),
    (88, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-88.pdf"),
    (89, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-89.pdf"),
    (90, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-90b.pdf"),
    (91, "https://www.mountcalvarybaptist.org/site/user/files/49/Final-number-91b.pdf"),
    # Thanksgiving bonus
    ("thanksgiving", "https://www.mountcalvarybaptist.org/site/user/files/49/Thanksgiving.pdf"),
]


def fetch_pdf_text(url):
    """Download a PDF from a URL and extract its text."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            pdf_bytes = response.read()

        # Try pypdf first
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        except ImportError:
            pass

        # Fallback: pdfminer
        try:
            from pdfminer.high_level import extract_text_to_fp
            from pdfminer.layout import LAParams
            output = io.StringIO()
            extract_text_to_fp(io.BytesIO(pdf_bytes), output, laparams=LAParams())
            return output.getvalue().strip()
        except ImportError:
            pass

        raise RuntimeError("No PDF library found. Run: pip install pypdf")

    except Exception as e:
        return None, str(e)


def parse_catechism(text, number):
    """
    Parse raw PDF text into structured catechism data.
    
    The PDF cards follow a rough structure:
      - Question text (first line / sentence ending in ?)
      - Scripture passages with references
      - A number (the catechism number)
      - The answer (bold/prominent text)
      - Attribution (Westminster Shorter Catechism, etc.)
    
    Because PDF extraction order varies, we use heuristics.
    """
    if not text:
        return None

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full_text = " ".join(lines)

    # --- Extract question ---
    # Usually the first sentence ending in ?
    question = ""
    for line in lines:
        if line.endswith("?"):
            question = line
            break
    if not question:
        # Try finding a ? anywhere in early lines
        for line in lines[:5]:
            if "?" in line:
                question = line[:line.index("?") + 1].strip()
                break

    # --- Extract attribution ---
    attribution = ""
    attr_match = re.search(r'\(([^)]*Catechism[^)]*|[^)]*Q\.\s*\d+[^)]*)\)', full_text, re.IGNORECASE)
    if attr_match:
        attribution = attr_match.group(0)

    # --- Extract answer ---
    # The answer is typically the last substantive block before the attribution,
    # often starting with "The" or matching a catechism-answer pattern.
    # Strategy: find the text after the last scripture reference and before attribution.
    answer = ""
    
    # Scripture references often look like (NASB; Rom. 11:36) or (KJV; I Cor. 10:31)
    # Find the last scripture reference position
    scripture_pattern = r'\([A-Z]+;\s*[A-Za-z0-9\s.:,;-]+\)'
    scripture_matches = list(re.finditer(scripture_pattern, full_text))
    
    if scripture_matches:
        last_scripture_end = scripture_matches[-1].end()
        after_scripture = full_text[last_scripture_end:].strip()
        # Remove the catechism number and attribution
        after_scripture = re.sub(r'^\d+\s*', '', after_scripture)
        after_scripture = re.sub(r'\([^)]*Catechism[^)]*\)', '', after_scripture, flags=re.IGNORECASE)
        after_scripture = re.sub(r'\([^)]*Q\.\s*\d+[^)]*\)', '', after_scripture, flags=re.IGNORECASE)
        answer = after_scripture.strip()

    # Fallback: look for lines that seem like an answer (don't contain scripture refs)
    if not answer:
        candidate_lines = []
        for line in reversed(lines):
            if re.search(scripture_pattern, line):
                break
            if line and not line.isdigit() and "Catechism" not in line:
                candidate_lines.insert(0, line)
        answer = " ".join(candidate_lines).strip()

    # --- Extract scripture passages ---
    scriptures = []
    # Each scripture block: text + (TRANSLATION; REF)
    scripture_blocks = re.findall(
        r'((?:[^(]|\([^A-Z][^)]*\))+)\(([A-Z]+);\s*([^)]+)\)',
        full_text
    )
    for passage_text, translation, reference in scripture_blocks:
        passage_text = passage_text.strip()
        # Skip if it looks like the question or answer
        if "?" in passage_text:
            passage_text = passage_text[passage_text.index("?") + 1:].strip()
        if passage_text:
            scriptures.append({
                "reference": reference.strip(),
                "translation": translation.strip(),
                "text": passage_text
            })

    return {
        "number": number,
        "question": question,
        "answer": answer,
        "scriptures": scriptures,
        "attribution": attribution,
        "raw_text": text  # keep raw so you can manually fix edge cases
    }


def main():
    print(f"Treeology Catechism Scraper")
    print(f"Downloading {len(PDF_URLS)} PDFs...\n")

    catechisms = []
    errors = []

    for i, (number, url) in enumerate(PDF_URLS):
        label = f"Q{number}" if number != "thanksgiving" else "Thanksgiving"
        print(f"[{i+1:3}/{len(PDF_URLS)}] {label}: ", end="", flush=True)

        text = fetch_pdf_text(url)

        if text is None or (isinstance(text, tuple)):
            error_msg = text[1] if isinstance(text, tuple) else "Unknown error"
            print(f"❌ FAILED — {error_msg}")
            errors.append({"number": number, "url": url, "error": error_msg})
            # Add a placeholder so the array stays complete
            catechisms.append({
                "number": number,
                "question": f"[Question {number} — download failed]",
                "answer": "",
                "scriptures": [],
                "attribution": "",
                "raw_text": "",
                "error": error_msg
            })
            continue

        parsed = parse_catechism(text, number)
        if parsed:
            catechisms.append(parsed)
            q_preview = parsed["question"][:60] + "..." if len(parsed["question"]) > 60 else parsed["question"]
            print(f"✅ {q_preview}")
        else:
            print(f"⚠️  Parsed but empty")
            catechisms.append({
                "number": number,
                "question": "",
                "answer": "",
                "scriptures": [],
                "attribution": "",
                "raw_text": text
            })

    # Write output
    output = {
        "total": len(catechisms),
        "catechisms": catechisms
    }

    with open("catechisms.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"Done! {len(catechisms) - len(errors)} succeeded, {len(errors)} failed.")
    print(f"Output written to: catechisms.json")

    if errors:
        print(f"\nFailed downloads:")
        for e in errors:
            print(f"  Q{e['number']}: {e['url']}")
            print(f"    Error: {e['error']}")
        print(f"\nYou can re-run the script or manually fill in failed entries in catechisms.json")

    print(f"\nNext step: copy catechisms.json into your app folder and open index.html")


if __name__ == "__main__":
    # Check for pypdf
    try:
        import pypdf
    except ImportError:
        print("Installing pypdf...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
        print("pypdf installed.\n")

    main()