import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

FPS = 30
TRANS = 0.4

MOTION_CSS = """
section.s{background-size:130% 130%;animation:drift var(--dur) linear both}
section.s > *:not(.top){animation:enter .7s cubic-bezier(.2,.8,.2,1) both}
section.s > *:nth-child(2){animation-delay:.05s}
section.s > *:nth-child(3){animation-delay:.15s}
section.s > *:nth-child(4){animation-delay:.25s}
section.s > *:nth-child(5){animation-delay:.35s}
section.s > *:nth-child(6){animation-delay:.45s}
section.s > *:nth-child(7){animation-delay:.55s}
.vs > div,.li{animation:enter .6s cubic-bezier(.2,.8,.2,1) both}
.vs > div:nth-child(1),.li:nth-of-type(1){animation-delay:.35s}
.vs > div:nth-child(2),.li:nth-of-type(2){animation-delay:.5s}
.vs > div:nth-child(3),.li:nth-of-type(3){animation-delay:.65s}
.big{animation:pop .8s cubic-bezier(.2,1.4,.4,1) both;animation-delay:.2s;transform-origin:left center}
@keyframes enter{from{opacity:0;transform:translateY(60px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:none}}
@keyframes drift{from{background-position:0% 0%}to{background-position:100% 60%}}
"""


def render(html_path, durations, out_path, workdir):
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    n = len(durations)
    lens = [d + (TRANS if i < n - 1 else 0) for i, d in enumerate(durations)]
    clips = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(Path(html_path).resolve().as_uri())
        pg.add_style_tag(content=MOTION_CSS + "body{margin:0}section.s{display:none}section.s.on{display:flex}")
        pg.wait_for_timeout(800)
        for i, length in enumerate(lens):
            pg.evaluate(
                """([i,dur])=>{const ss=[...document.querySelectorAll('section.s')];
                ss.forEach((s,k)=>{s.classList.toggle('on',k===i);s.style.setProperty('--dur',dur+'s')});
                document.getAnimations().forEach(a=>a.pause());}""",
                [i, length],
            )
            sec = pg.query_selector_all("section.s")[i]
            frames = int(round(length * FPS))
            clip = workdir / f"m{i+1}.mp4"
            tmp = workdir / f"tmp_m{i+1}.mp4"
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                 "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), str(tmp)],
                stdin=subprocess.PIPE,
            )
            for f in range(frames):
                t = f / FPS * 1000
                pg.evaluate("(t)=>document.getAnimations().forEach(a=>{a.currentTime=t})", t)
                ff.stdin.write(sec.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            ff.wait()
            if ff.returncode != 0:
                raise SystemExit(f"ffmpeg falhou na cena {i+1}")
            tmp.rename(clip)
            clips.append(clip)
            print(f"cena {i+1}/{n} ok ({frames} quadros)", flush=True)
        b.close()

    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]
    filt = []
    prev = "[0:v]"
    offset = 0.0
    for k in range(1, n):
        offset += durations[k - 1]
        start = offset - TRANS
        lab = f"[x{k}]"
        filt.append(f"{prev}[{k}:v]xfade=transition=slideleft:duration={TRANS}:offset={start:.3f}{lab}")
        prev = lab
    tmp = Path(out_path).with_name("tmp_" + Path(out_path).name)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt), "-map", prev,
         "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), str(tmp)],
        check=True,
    )
    tmp.rename(out_path)


if __name__ == "__main__":
    html, durs, out, wd = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3], sys.argv[4]
    render(html, durs, out, wd)
