import sys, subprocess, pathlib
from playwright.sync_api import sync_playwright
out=sys.argv[1]; times=[float(x) for x in sys.argv[2:]]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto((pathlib.Path(__file__).parent/'reel16.html').resolve().as_uri())
    pg.wait_for_timeout(500)
    if times:
        for t in times:
            pg.evaluate(f'seek({t})'); pg.screenshot(path=f'{out}_{t}.png')
        b.close(); sys.exit()
    FPS=30; dur=pg.evaluate('DUR'); n=int(dur*FPS)
    cmd=['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',out]
    f=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(n):
        pg.evaluate(f'seek({i/FPS})')
        f.stdin.write(pg.screenshot(type='jpeg',quality=93))
    f.stdin.close(); f.wait(); b.close(); print('done',out)
