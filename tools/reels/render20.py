import sys, subprocess, pathlib, os
from playwright.sync_api import sync_playwright
HTML=(pathlib.Path(__file__).parent/'reel20.html').resolve().as_uri()
def page(p):
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto(HTML); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(700)
    return b,pg
def chunk(out,i0,i1,fps):
    with sync_playwright() as p:
        b,pg=page(p)
        tmp=out+'.part.mp4'
        cmd=['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',tmp]
        f=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for i in range(i0,i1):
            pg.evaluate(f'seek({i/fps})'); f.stdin.write(pg.screenshot(type='jpeg',quality=92))
        f.stdin.close(); r=f.wait(); b.close()
        if r==0: os.replace(tmp,out)
if __name__=='__main__':
    if sys.argv[1]=='still':
        pre=sys.argv[2]
        with sync_playwright() as p:
            b,pg=page(p)
            for t in sys.argv[3:]:
                pg.evaluate(f'seek({t})'); pg.screenshot(path=f'{pre}_{t}.png')
            b.close()
    elif sys.argv[1]=='chunk':
        chunk(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),60)
