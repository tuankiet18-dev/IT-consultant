"""Build MVP.mp4 from the raw screen recording: cards + trimmed clips + holds + burned-in English subtitles.
Run from anywhere:  python deliverables/video-kit/scripts/build-video.py (raw recording in mvp/out/raw/)
Needs ffmpeg on PATH. Output: deliverables/MVP.mp4.
Voice-over: every subtitle cue is spoken with a Windows voice (tts-cues.ps1) and each clip is held long enough for its audio,
so voice and subtitles always say the same thing.
Final submission build:  python build-video.py --edge en-US-EmmaNeural --out deliverables/MVP.mp4   (pip install edge-tts; sends the cue texts to Microsoft)
Offline fallback:        python build-video.py   (Windows voice Zira).  Silent build: add --no-voice."""
import pathlib, subprocess, math, shutil, json, wave, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
RAW = next((ROOT / "mvp/out/raw").glob("*.mkv"))
CARDS = ROOT / "deliverables/video-kit/cards"
def _arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


EDGE = _arg("--edge")                      # e.g. --edge en-US-EmmaNeural : neural voice (online, text is sent to Microsoft)
BUILD = ROOT / ("mvp/out/build-edge" if EDGE else "mvp/out/build")
OUT = ROOT / _arg("--out", "deliverables/MVP-edge-tts.mp4" if EDGE else "deliverables/MVP.mp4")
CPS = 15.0            # reading speed, characters per second
MIN_CUE = 2.4

# kind, args, cues.  play: (raw_start, raw_end, speed)   hold: (raw_time,)   card: (png, seconds)
ITEMS = [
    ("card", ("01-title.png", 5), ["Nordic Flow is a planner-approved optimisation service for goods allocation. Everything you will see runs locally, on synthetic data."]),
    ("card", ("02-changes-0of5.png", 2), []),
    ("card", ("02-changes-1of5.png", 6), ["Since our Round 1 proposal, five things changed, and here is why. First, we use synthetic data, because Company A's data is not available. Every screen says so."]),
    ("card", ("02-changes-2of5.png", 6), ["Second, we added what-if scenarios, an approval gate and an audit trail, so that the planner approves and every decision is logged is shown, not promised."]),
    ("card", ("02-changes-3of5.png", 6), ["Third, learning from overrides stays in phase two, as planned in Round 1."]),
    ("card", ("02-changes-4of5.png", 6), ["Fourth, there is no ERP connection: files in, files out."]),
    ("card", ("02-changes-5of5.png", 8), ["Fifth, as an optional extension, the engine can also move goods between existing warehouses."]),

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
    ("card", ("09-closing.png", 14), ["In short: code calculates, AI explains, and a person approves. The limits are clear: synthetic data, one planning period, no ERP integration. The Round 1 gates, such as five percent saving and thirty percent less planning time, need real data in a pilot. This MVP proves the mechanism, not the number."]),
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


def all_texts():
    return [t for _, _, texts in ITEMS for t in texts]


def polish(wavs, soft=True):
    """Resample each cue to 48 kHz with the high-quality resampler (the voice is 22.05 kHz), cut rumble, and set a steady level."""
    out = []
    for w in wavs:
        tmp = w.with_name(w.stem + "_48k.wav")
        run("-i", w, "-af", "aresample=48000:resampler=soxr:precision=28,highpass=f=90" + (",equalizer=f=3600:t=q:w=1.5:g=-2.5,equalizer=f=6500:t=q:w=1.5:g=-3,lowpass=f=8000" if soft else ""), "-ac", 1, tmp)
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
        mean = float(r.stderr.split("mean_volume:")[1].split("dB")[0])
        peak = float(r.stderr.split("max_volume:")[1].split("dB")[0])
        gain = min(-19.0 - mean, -3.0 - peak)          # speech at about -19 dB mean, never above -3 dB peak
        fin = w.with_name(w.stem + "_final.wav")
        run("-i", tmp, "-af", f"volume={gain:.2f}dB", fin)
        out.append(fin)
    return out


def speak_edge(voice, rate="+0%"):
    """Neural voice via the edge-tts package (needs internet; sends the cue texts to Microsoft's speech service)."""
    import asyncio, edge_tts
    tts = BUILD / "tts"
    tts.mkdir(parents=True, exist_ok=True)

    async def go():
        for n, t in enumerate(all_texts(), 1):
            mp3 = tts / f"cue_{n:03d}.mp3"
            await edge_tts.Communicate(t, voice, rate=rate).save(str(mp3))
            run("-i", mp3, "-ar", 24000, "-ac", 1, tts / f"cue_{n:03d}.wav")
    asyncio.run(go())
    wavs = polish(sorted(tts.glob("cue_*.wav")), soft=False)
    durs = []
    for w in wavs:
        with wave.open(str(w)) as f:
            durs.append(f.getnframes() / f.getframerate())
    return wavs, durs


def speak(voice, rate):
    """Speak every cue text; return the list of wav paths and their durations in seconds."""
    tts = BUILD / "tts"
    (BUILD).mkdir(parents=True, exist_ok=True)
    (BUILD / "cues.json").write_text(json.dumps(all_texts(), ensure_ascii=False), encoding="utf8")
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(pathlib.Path(__file__).with_name("tts-cues.ps1")),
                        "-Json", str(BUILD / "cues.json"), "-OutDir", str(tts), "-Voice", voice, "-Rate", str(rate)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stdout + r.stderr)
    wavs = polish(sorted(tts.glob("cue_*.wav")))
    durs = []
    for w in wavs:
        with wave.open(str(w)) as f:
            durs.append(f.getnframes() / f.getframerate())
    return wavs, durs


def mix(wavs, starts, total):
    """Place each cue wav at its start time on one mono track."""
    with wave.open(str(wavs[0])) as f:
        rate, width, ch = f.getframerate(), f.getsampwidth(), f.getnchannels()
    buf = bytearray((int(total * rate) + rate) * width * ch)
    for w, st in zip(wavs, starts):
        with wave.open(str(w)) as f:
            data = f.readframes(f.getnframes())
        off = int(st * rate) * width * ch
        buf[off:off + len(data)] = data
    out = BUILD / "voice.wav"
    with wave.open(str(out), "wb") as f:
        f.setnchannels(ch); f.setsampwidth(width); f.setframerate(rate); f.writeframes(bytes(buf))
    return out


def main():
    voice = "--no-voice" not in sys.argv
    wavs = durs = None
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    if voice:
        wavs, durs = speak_edge(EDGE) if EDGE else speak("Microsoft Zira Desktop", 0)
    n_cue, starts = 0, []
    segs, cues, clock = [], [], 0.0
    for i, (kind, a, texts) in enumerate(ITEMS):
        f = BUILD / f"s{i:02d}.mp4"
        if kind == "card":
            png, dur = a
            if voice and texts:        # card text is on screen, so the voice is not subtitled here
                dur = max(dur, sum(durs[n_cue + k] + 0.9 for k in range(len(texts))))
                starts.append(clock + 0.3)
                n_cue += len(texts)
            run("-loop", 1, "-framerate", FPS, "-t", f"{dur:.3f}", "-i", CARDS / png, "-vf", "format=yuv420p", "-r", FPS, "-c:v", "libx264", "-crf", 18, "-an", f)
            total = dur
        else:
            if kind == "play":
                s, e, sp = a
            else:
                s, e, sp = a[0], a[0] + 0.1, 1.0
            play = (e - s) / sp
            weights = [max(MIN_CUE, len(t) / CPS + 0.4, (durs[n_cue + k] + 0.7) if voice else 0) for k, t in enumerate(texts)]
            need = sum(weights)
            hold = max(0.0, need - play) if kind == "play" else max(0.0, need - play)
            vf = f"setpts=PTS/{sp},fps={FPS},{VF_SCREEN}"
            if hold > 0:
                vf += f",tpad=stop_mode=clone:stop_duration={hold:.3f}"
            run("-ss", s, "-to", e, "-i", RAW, "-vf", vf + ",format=yuv420p", "-r", FPS, "-c:v", "libx264", "-crf", 18, "-an", f)
            total = play + hold
            # split the item's time over its cues in proportion to text length
            sw = sum(weights)
            t0 = clock
            for t, w in zip(texts, weights):
                d = total * w / sw
                cues.append((t0, t0 + d - 0.05, wrap(t)))
                starts.append(t0 + 0.2)
                t0 += d
            n_cue += len(texts)
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
    if voice:
        track = mix(wavs, starts, clock)
        run("-i", BUILD / "final.mp4", "-i", track, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", 48000, "-shortest", "-movflags", "+faststart", BUILD / "final_voice.mp4")
        shutil.copy(BUILD / "final_voice.mp4", OUT)
    else:
        shutil.copy(BUILD / "final.mp4", OUT)
    print(f"done: {OUT}  duration {clock:.1f}s ({int(clock // 60)}:{int(clock % 60):02d})  cues {len(cues)}")


if __name__ == "__main__":
    main()
