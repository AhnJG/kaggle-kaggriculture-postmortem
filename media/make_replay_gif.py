"""Render a hosted Kaggriculture replay to a GIF with team names masked.

usage: python3 media/make_replay_gif.py <replay.json[.gz]> <our_team_name> <opponent_label> <our_label> <out.gif>
Needs kaggle-environments==1.32.7, playwright (Chromium) and Pillow.
Used for media/hosted_loss_115289957.gif (episode 115289957, 2026-09-29); the score banner on its last frame was added separately.
"""
import asyncio, gzip, json, sys, tempfile, pathlib
from PIL import Image
from playwright.async_api import async_playwright
from kaggle_environments import make

src, ours, opp_label, our_label, out = sys.argv[1:6]
raw = json.load(gzip.open(src) if src.endswith(".gz") else open(src))
names = raw["info"]["TeamNames"]
s = json.dumps(raw)
for n in names:                      # replace every occurrence of both team names
    s = s.replace(json.dumps(n)[1:-1], our_label if n == ours else opp_label)
rep = json.loads(s)
rep["info"]["Agents"] = [{"Name": our_label if n == ours else opp_label} for n in names]
env = make("kaggriculture", configuration=rep["configuration"], steps=rep["steps"], info=rep["info"])
tmp = pathlib.Path(tempfile.mkdtemp()); (tmp / "r.html").write_text(env.render(mode="html", width=900, height=700))
seat_labels = [our_label if n == ours else opp_label for n in names]   # visualizer shows "Player 1/2"

async def capture():
    frames = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1100, "height": 760})
        await pg.goto((tmp / "r.html").as_uri()); await pg.wait_for_timeout(5000)
        for k, step in enumerate(list(range(0, 720, 24)) + [719]):
            await pg.evaluate("""v=>{const el=document.querySelector('input[type=range]');
              Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,String(v));
              el.dispatchEvent(new Event('input',{bubbles:true}));}""", step + 1)
            await pg.wait_for_timeout(350)
            await pg.evaluate("""l=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
              while((n=w.nextNode())){const t=n.nodeValue.trim(); if(t==='Player 1')n.nodeValue=l[0]; else if(t==='Player 2')n.nodeValue=l[1];}}""", seat_labels)
            f = tmp / f"f{k:03d}.png"; await pg.screenshot(path=str(f), clip={"x": 0, "y": 0, "width": 1100, "height": 688})
            frames.append(f)
        await b.close()
    return frames

files = asyncio.run(capture())
W = 760
ims = [Image.open(f).convert("RGB").resize((W, int(688 * W / 1100)), Image.LANCZOS) for f in files]
pal = ims[len(ims) // 2].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in ims]
dur = [400] * len(q); dur[0] = 1000; dur[-1] = 3500
q[0].save(out, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True)
print("wrote", out)
