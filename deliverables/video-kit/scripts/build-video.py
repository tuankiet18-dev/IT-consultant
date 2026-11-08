"""Build MVP.mp4 from the raw screen recording: cards + trimmed clips + holds + burned-in English subtitles.
Run from anywhere:  python deliverables/video-kit/scripts/build-video.py (raw recording in mvp/out/raw/)
Needs ffmpeg on PATH. Output: deliverables/MVP.mp4 (git-ignored)."""
import pathlib, subprocess, math, shutil

ROOT = pathlib.Path(__file__).resolve().parents[3]
RAW = next((ROOT / "mvp/out/raw").glob("*.mkv"))
CARDS = ROOT / "deliverables/video-kit/cards"
BUILD = ROOT / "mvp/out/build"
OUT = ROOT / "deliverables/MVP.mp4"
CPS = 15.0            # reading speed, characters per second
MIN_CUE = 2.4

# kind, args, cues.  play: (raw_start, raw_end, speed)   hold: (raw_time,)   card: (png, seconds)
ITEMS = [
    ("card", ("01-title.png", 5), []),
    ("card", ("02-changes-0of5.png", 3), []),
    ("card", ("02-changes-1of5.png", 6), []),
    ("card", ("02-changes-2of5.png", 6), []),
    ("card", ("02-changes-3of5.png", 6), []),
    ("card", ("02-changes-4of5.png", 6), []),
    ("card", ("02-changes-5of5.png", 8), []),

    ("play", (2.0, 8.8, 1.0), ["The planner starts on the Data page. The 'Synthetic data' badge is on every screen: Company A's data is not available."]),
    ("play", (8.8, 23.9, 1.0), ["The planner drops in this week's files: eight CSV files in one ZIP.",
                                "Every file is checked before anything is calculated. Valid: 2 suppliers, 3 warehouses, 6 zones, 20 products, 606 pallets."]),
    ("play", (23.9, 29.4, 1.0), ["What if the data is wrong? This file declares a loop between warehouses."]),
    ("play", (29.4, 40.9, 1.0), ["The run is blocked and the message says exactly why. There is no Calculate button: the system never guesses."]),
    ("play", (40.9, 55.1, 1.5), ["Back to the valid data set, ready to calculate."]),
    ("play", (55.1, 63.0, 1.0), ["The optimiser finds a plan costing 31,316 cost units against 32,698 for the baseline: a saving of 1,382 (4.2%).",
                                 "This is synthetic data, so it is not a forecast. The baseline is a simple preferred-warehouse rule, not Company A's real plan."]),
    ("hold", (62.9,), ["Plan checks passed: a separate verifier, which does not use the solver, re-checked supply, demand, capacity and lanes."]),
    ("play", (63.4, 87.3, 1.6), ["The diagram shows where goods move: coloured lines carry pallets, grey dashed lines are declared routes left unused.",
                                 "The ranking prices every full path, leg by leg, so the planner can see why a route is chosen."]),
    ("play", (87.3, 95.5, 1.0), ["For Zone 1 cement the cheapest path is Supplier 1 via Warehouse C, at 62 per pallet. Selecting a row highlights the whole path."]),
    ("play", (95.5, 99.7, 1.0), ["Now the planner overrides the machine. A customer contract says Zone 1 must receive its cement from Warehouse B."]),
    ("play", (99.7, 119.4, 1.3), ["The planner fixes 8 pallets of Cement standard to Warehouse B and must give a reason.",
                                  "Everything else is recalculated around that decision as a new plan version."]),
    ("play", (119.4, 128.4, 1.0), ["Result: the plan cost goes from 31,316 to 31,404, plus 88 cost units. The price of the decision is visible and the original plan is kept."]),
    ("play", (128.4, 135.5, 1.0), ["Now the explanation. Code calculates every number; the AI assistant only puts the result into words."]),
    ("play", (135.5, 147.9, 1.0), ["The text is marked 'AI draft, needs review'. If any figure is not in the calculated facts, the whole draft is rejected.",
                                   "Even so, the planner must read it: the number check is one guard, not proof that every sentence is right."]),
    ("play", (147.9, 158.8, 1.0), ["The supporting figures let the planner compare the text with the calculated numbers before approving."]),
    ("play", (158.8, 175.7, 1.0), ["Here is that guard in action, outside the app. A draft with correct figures is ACCEPTED.",
                                   "A draft that invents a figure is REJECTED, and the standard summary is used instead."]),
    ("play", (175.7, 187.6, 1.0), ["The planner edits the text if needed and approves it. AI helps; a person decides."]),
    ("play", (187.6, 196.2, 1.0), ["Now the planner approves the plan. From this moment it is locked, and only an approved plan can be exported."]),
    ("play", (199.2, 203.1, 1.0), ["The export is a ZIP for the existing ERP, warehouse and transport systems. Nordic Flow executes nothing."]),
    ("play", (203.1, 222.5, 1.0), ["The audit trail records every step: data loaded, plan calculated, the planner's decision, approvals and export.",
                                   "Each entry is linked to the one before it, so any edit is detectable: tamper-evident, not tamper-proof."]),
    ("play", (222.5, 231.0, 1.0), ["The planner can also ask 'what if'. If Warehouse A closes, no plan can meet demand."]),
    ("hold", (235.0,), ["Total warehouse capacity (684) is below the demand that needs handling (902). The system says so instead of returning a bad plan."]),
    ("play", (238.0, 248.6, 1.3), ["It lists the unserved pallets by zone and product, and never invents a route."]),
    ("card", ("09-closing.png", 14), []),
]

FPS = 30
VF_SCREEN = "crop=1280:680:0:0,scale=1792:952:flags=lanczos,pad=1920:1080:64:0:black,setsar=1"


def run(*a):
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, a)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)


def wrap(t, w=86):
    words, lines, cur = t.split(), [], ""
    for x in words:
        if len(cur) + len(x) + 1 > w and cur:
            lines.append(cur); cur = x
        else:
            cur = (cur + " " + x).strip()
    lines.append(cur)
    return "\n".join(lines)


def ts(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    segs, cues, clock = [], [], 0.0
    for i, (kind, a, texts) in enumerate(ITEMS):
        f = BUILD / f"s{i:02d}.mp4"
        if kind == "card":
            png, dur = a
            run("-loop", 1, "-framerate", FPS, "-t", dur, "-i", CARDS / png, "-vf", "format=yuv420p", "-r", FPS, "-c:v", "libx264", "-crf", 18, "-an", f)
            total = dur
        else:
            if kind == "play":
                s, e, sp = a
            else:
                s, e, sp = a[0], a[0] + 0.1, 1.0
            play = (e - s) / sp
            need = sum(max(MIN_CUE, len(t) / CPS + 0.4) for t in texts)
            hold = max(0.0, need - play) if kind == "play" else max(0.0, need - play)
            vf = f"setpts=PTS/{sp},fps={FPS},{VF_SCREEN}"
            if hold > 0:
                vf += f",tpad=stop_mode=clone:stop_duration={hold:.3f}"
            run("-ss", s, "-to", e, "-i", RAW, "-vf", vf + ",format=yuv420p", "-r", FPS, "-c:v", "libx264", "-crf", 18, "-an", f)
            total = play + hold
            # split the item's time over its cues in proportion to text length
            weights = [max(MIN_CUE, len(t) / CPS + 0.4) for t in texts]
            sw = sum(weights)
            t0 = clock
            for t, w in zip(texts, weights):
                d = total * w / sw
                cues.append((t0, t0 + d - 0.05, wrap(t)))
                t0 += d
        segs.append(f)
        clock += total
    (BUILD / "fonts").mkdir()
    for fn in ("segoeui.ttf", "segoeuib.ttf"):
        shutil.copy(pathlib.Path("C:/Windows/Fonts") / fn, BUILD / "fonts" / fn)
    (BUILD / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in segs), encoding="utf8")
    srt = "".join(f"{n}\n{ts(a)} --> {ts(b)}\n{t}\n\n" for n, (a, b, t) in enumerate(cues, 1))
    (BUILD / "subs.srt").write_text(srt, encoding="utf8")
    run("-f", "concat", "-safe", 0, "-i", BUILD / "list.txt", "-c", "copy", BUILD / "nosubs.mp4")
    style = "FontName=Segoe UI,FontSize=9,PrimaryColour=&H00FFFFFF,Outline=0,Shadow=0,Alignment=2,MarginV=6,Spacing=0.1"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "nosubs.mp4", "-vf",
                        f"subtitles=subs.srt:fontsdir=fonts:force_style='{style}'",
                        "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", "final.mp4"],
                       cwd=BUILD, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    shutil.copy(BUILD / "final.mp4", OUT)
    print(f"done: {OUT}  duration {clock:.1f}s ({int(clock // 60)}:{int(clock % 60):02d})  cues {len(cues)}")


if __name__ == "__main__":
    main()
