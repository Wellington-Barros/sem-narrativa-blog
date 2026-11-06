import sys, subprocess, pathlib, json
from playwright.sync_api import sync_playwright

base = pathlib.Path(__file__).parent
data = json.load(open(base / 'reel15-data.json', encoding='utf-8'))
html = (base / 'reel15.html').read_text(encoding='utf-8').replace('__DATA__', json.dumps(data, ensure_ascii=False))
tmp = base / '_reel15_render.html'
tmp.write_text(html, encoding='utf-8')

out = sys.argv[1]
args = sys.argv[2:]
audio = None
if args and not args[0].replace('.', '', 1).isdigit():
    audio = args[0]
    args = args[1:]
times = [float(x) for x in args]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto(tmp.resolve().as_uri())
    pg.wait_for_timeout(600)
    if times:
        for t in times:
            pg.evaluate(f'seek({t})')
            pg.screenshot(path=f'{out}_{t}.png')
        b.close()
        tmp.unlink()
        sys.exit()
    FPS = 30
    dur = pg.evaluate('DUR')
    n = int(dur * FPS)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-']
    if audio:
        cmd += ['-i', audio]
    else:
        cmd += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
    cmd += ['-map', '0:v', '-map', '1:a', '-shortest', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', out]
    f = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        pg.evaluate(f'seek({i / FPS})')
        f.stdin.write(pg.screenshot(type='jpeg', quality=93))
    f.stdin.close()
    f.wait()
    b.close()
    tmp.unlink()
    print('done', out)
