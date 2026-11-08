"""Final check before emailing the four Round 2 files. Reads only; changes nothing.

Run from the repository root:
    python deliverables/check-submission.py                 (looks in deliverables/)
    python deliverables/check-submission.py "D:/path/to/folder/with/the/four/files"

Checks: exact file names, page limits, video length (7:00 max), leftover placeholders in the AI Journal draft,
API keys or password-like strings inside the files. It cannot judge content: watch the video once yourself.
"""
import re
import struct
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
folder = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
REQUIRED = ["MVP.mp4", "User Journey.pdf", "System Context Diagram.pdf", "AI Journal.pdf"]
ok_all = True


def line(status, text):
    global ok_all
    if status == "FAIL":
        ok_all = False
    print(f"{status:<5} {text}")


def pdf_pages(path):
    return len(re.findall(rb"/Type\s*/Page[^s]", path.read_bytes()))


def mp4_seconds(path):
    """Duration from the movie header (mvhd). Returns None if it cannot be read."""
    with open(path, "rb") as f:
        def boxes(end, offset):
            while offset < end:
                f.seek(offset)
                head = f.read(8)
                if len(head) < 8:
                    return
                size, kind = struct.unpack(">I4s", head)
                header = 8
                if size == 1:
                    size = struct.unpack(">Q", f.read(8))[0]
                    header = 16
                elif size == 0:
                    size = end - offset
                yield kind, offset + header, offset + size
                offset += size
        size_total = path.stat().st_size
        for kind, start, stop in boxes(size_total, 0):
            if kind == b"moov":
                for k2, s2, e2 in boxes(stop, start):
                    if k2 == b"mvhd":
                        f.seek(s2)
                        version = f.read(1)[0]
                        f.read(3)
                        if version == 1:
                            f.read(16)
                            timescale, duration = struct.unpack(">IQ", f.read(12))
                        else:
                            f.read(8)
                            timescale, duration = struct.unpack(">II", f.read(8))
                        return duration / timescale if timescale else None
    return None


print(f"Folder checked: {folder}\n")

# 1. names
present = {p.name for p in folder.iterdir()} if folder.exists() else set()
for name in REQUIRED:
    if name in present:
        line("PASS", f"{name} exists ({(folder / name).stat().st_size / 1e6:.1f} MB)")
    else:
        near = [p for p in present if p.lower().replace("_", " ").startswith(name.lower().split(".")[0][:6])]
        line("FAIL", f"{name} is missing" + (f" (found similar: {', '.join(near)})" if near else ""))

# 2. page limits
for name in ("User Journey.pdf", "System Context Diagram.pdf"):
    p = folder / name
    if p.exists():
        n = pdf_pages(p)
        line("PASS" if 1 <= n <= 2 else "FAIL", f"{name}: {n} page(s), limit 2")
p = folder / "AI Journal.pdf"
if p.exists():
    line("INFO", f"AI Journal.pdf: {pdf_pages(p)} page(s) (the template has no page limit, but keep it tidy)")

# 3. video length
p = folder / "MVP.mp4"
if p.exists():
    secs = mp4_seconds(p)
    if secs is None:
        line("WARN", "MVP.mp4: could not read the duration. Open it and check it is 7:00 or less")
    else:
        line("PASS" if secs <= 420 else "FAIL", f"MVP.mp4 length {int(secs // 60)}:{int(secs % 60):02d}, limit 7:00")
    if p.stat().st_size > 25e6:
        line("WARN", "MVP.mp4 is larger than 25 MB: most email providers will reject it. Share it by a link (see docs/round2/EMAIL.md)")

# 4. AI Journal draft placeholders
draft = HERE.parent / "docs" / "round2" / "AI-Journal-DRAFT.docx"
if draft.exists():
    try:
        import docx
        d = docx.Document(str(draft))
        text = "\n".join(par.text for par in d.paragraphs)
        for t in d.tables:
            for row in t.rows:
                for cell in row.cells:
                    text += "\n" + cell.text
        left = re.findall(r"\[[^\]]*\]", text)
        line("PASS" if not left else "FAIL", "AI Journal draft has no yellow [..] placeholders left" if not left else f"AI Journal draft still has {len(left)} placeholder(s), e.g. {left[0]!r}")
    except Exception as e:  # python-docx not installed
        line("WARN", f"could not read the AI Journal draft ({e}); check the yellow cells by eye")

# 5. secrets inside the four files
for name in REQUIRED:
    p = folder / name
    if p.exists():
        data = p.read_bytes()
        hit = re.search(rb"gsk_[A-Za-z0-9]{10,}", data)
        line("FAIL" if hit else "PASS", f"{name}: " + ("contains something that looks like a Groq key!" if hit else "no API key pattern found"))
line("INFO", "PDF text is compressed, so this scan is only a first filter. Search the text of every PDF for 'gsk_', 'password' and 'secret' by eye, and watch the whole video once.")

print()
print("READY to send." if ok_all else "NOT ready: fix the FAIL lines above.")
print("Email: to EB.VN@netcompany.com, subject 'Round 2 – NEW AURA', before 18:00 (hard deadline 22:00 GMT+7, 9 Nov 2026).")
sys.exit(0 if ok_all else 1)
