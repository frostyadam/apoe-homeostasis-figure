#!/usr/bin/env python3
"""Render apoe_tour.html's camera path to an MP4 (and optional GIF) for slide decks.

Approach, and why: the cartoon is drawn by JS, so it cannot be rasterised without a
browser. But it only has to be drawn ONCE. We use headless Edge a single time to dump
the fully-drawn <svg> plus the computed value of every CSS colour token, substitute the
var() references for literal colours, then rasterise each frame with cairosvg by
changing nothing but the viewBox attribute. That turns ~1400 browser screenshots
(infeasible) into one browser call plus fast local rasterisation.

Camera path and captions come from tour_stops.json, written by 03_build_tour.py, so
the video and the interactive page can never disagree.

ffmpeg comes from the pip package imageio-ffmpeg (a bundled static binary), so no
system install and no sudo are needed.

Usage:  python 04_render_tour_mp4.py [--w 1600] [--fps 30] [--gif] [--fast]
"""
import argparse, json, math, pathlib, re, subprocess, sys, tempfile, shutil

HERE = pathlib.Path(__file__).parent
EDGE = "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
WSL_URL = ("file://wsl.localhost/Ubuntu-24.04"
           + str(HERE / "_dump.html").replace("/home/afrost", "/home/afrost"))

ap = argparse.ArgumentParser()
ap.add_argument("--w", type=int, default=1600, help="output width in px")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--move", type=float, default=0.9, help="seconds per camera move")
ap.add_argument("--dwell", type=float, default=2.6, help="seconds held at each stop")
ap.add_argument("--gif", action="store_true", help="also write a GIF")
ap.add_argument("--fast", action="store_true", help="12 fps draft, quick preview")
A = ap.parse_args()
if A.fast:
    A.fps, A.w = 12, 1000

cfg = json.loads((HERE / "tour_stops.json").read_text())
VB, STOPS = cfg["viewBox"], cfg["stops"]
AR = VB[2] / VB[3]
W = A.w
H = int(round(W / AR))


def fit(b):
    """Expand a loose box to the master aspect ratio, then clamp it inside the
    viewBox. Must stay identical to fit() in the page (03_build_tour.py)."""
    x, y, w, h = b
    if w / h > AR:
        nh = w / AR
        y -= (nh - h) / 2
        h = nh
    else:
        nw = h * AR
        x -= (nw - w) / 2
        w = nw
    if w >= VB[2]:
        return list(VB)
    x = min(max(x, VB[0]), VB[0] + VB[2] - w)
    y = min(max(y, VB[1]), VB[1] + VB[3] - h)
    return [x, y, w, h]


# ---------------------------------------------------------------- 1. dump the drawn SVG
def dump_svg():
    probe = """
<script>
addEventListener("load",()=>setTimeout(()=>{
  const s=document.getElementById("schem");
  const names=new Set();
  for(const sh of document.styleSheets){
    let rules; try{rules=sh.cssRules}catch(e){continue}
    for(const r of rules||[]) if(r.style) for(const p of r.style)
      if(p.startsWith("--")) names.add(p);
  }
  const cs=getComputedStyle(document.documentElement), map={};
  names.forEach(n=>{const v=cs.getPropertyValue(n).trim(); if(v) map[n]=v});
  const out=document.createElement("textarea"); out.id="__dump";
  // textContent, NOT .value - the value property is not reflected into --dump-dom
  out.textContent=JSON.stringify({svg:new XMLSerializer().serializeToString(s), tokens:map});
  document.body.appendChild(out);
},900));
</script>"""
    page = (HERE / "apoe_tour.html").read_text()
    (HERE / "_dump.html").write_text(page + probe)
    url = "file://wsl.localhost/Ubuntu-24.04" + str((HERE / "_dump.html").resolve())
    r = subprocess.run(
        [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000",
         "--window-size=1600,1200", "--dump-dom", url],
        capture_output=True, text=True, timeout=180,
        cwd="/mnt/c/Program Files (x86)/Microsoft/Edge/Application")
    dom = r.stdout.replace("\r", "")
    m = re.search(r'<textarea id="__dump">(.*?)</textarea>', dom, re.S)
    if not m:
        sys.exit("could not dump the drawn SVG - is msedge.exe reachable?")
    import html as _h
    payload = json.loads(_h.unescape(m.group(1)))
    (HERE / "_dump.html").unlink(missing_ok=True)
    return payload["svg"], payload["tokens"]


print("dumping the drawn cartoon from headless Edge ...")
svg, tokens = dump_svg()
print(f"  svg {len(svg)/1024:.0f} KB, {len(tokens)} CSS tokens")
(HERE/"_dumped.svg").write_text(svg)

# ---------------------------------------------------- 2. resolve var(--x) to literals
# cairosvg does not apply the page stylesheet, so bake the colours in. Repeat until
# stable because some tokens are defined in terms of others.
def _tok(m):
    # Values land inside XML attributes, and font-stack tokens contain double
    # quotes (e.g. "Roboto Condensed", system-ui) which would terminate the
    # attribute and make the document non-well-formed. Use single quotes.
    return tokens.get(m.group(1), "#888").replace('"', "'")


for _ in range(6):
    before = svg
    svg = re.sub(r"var\((--[a-z0-9-]+)\s*(?:,[^()]*)?\)", _tok, svg)
    if svg == before:
        break
leftover = re.findall(r"var\(--[a-z0-9-]+\)", svg)
if leftover:
    print(f"  warning: {len(set(leftover))} unresolved tokens, e.g. {sorted(set(leftover))[:3]}")
# cairosvg needs an explicit namespace and no HTML-only attributes
if "xmlns" not in svg[:400]:
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
svg = re.sub(r'\s(?:role|aria-label|style)="[^"]*"', "", svg, count=0)
page_bg = tokens.get("--page", "#ffffff")

# ------------------------------------------------------------------ 3. the frame plan
ease = lambda t: 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
plan = []                                     # (viewBox, stop_index)
for i, s in enumerate(STOPS):
    box = fit(s["box"])
    if i:
        prev = fit(STOPS[i - 1]["box"])
        for f in range(max(1, int(A.move * A.fps))):
            k = ease((f + 1) / max(1, int(A.move * A.fps)))
            plan.append(([prev[j] + (box[j] - prev[j]) * k for j in range(4)], i))
    for _ in range(max(1, int((A.dwell if i else A.dwell + .8) * A.fps))):
        plan.append((box, i))
print(f"  {len(plan)} frames, {len(plan)/A.fps:.1f} s at {A.fps} fps, {W}x{H}")

# --------------------------------------------------------------------- 4. rasterise
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

def font(sz, bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"
              % ("-Bold" if bold else ""),
              "/mnt/c/Windows/Fonts/segoeui%s.ttf" % ("b" if bold else "")):
        if pathlib.Path(p).exists():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

F_NUM, F_TTL, F_SUB = font(max(11, W // 118)), font(max(17, W // 62), True), font(max(13, W // 90))
PAD, MARG = max(14, W // 95), max(20, W // 62)
CARD_W = int(W * .34)


def wrap(draw, text, fnt, maxw):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            line = t
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def caption(img, idx):
    s = STOPS[idx]
    d = ImageDraw.Draw(img, "RGBA")
    inner = CARD_W - 2 * PAD
    tl = wrap(d, s["t"], F_TTL, inner)
    sl = wrap(d, s["s"], F_SUB, inner)
    lh_t = F_TTL.size + 4
    lh_s = int(F_SUB.size * 1.45)
    ch = PAD + F_NUM.size + 7 + len(tl) * lh_t + 5 + len(sl) * lh_s + PAD
    pos = s.get("pos", "bl")
    x = MARG if pos in ("bl", "tl") else W - CARD_W - MARG
    y = MARG if pos in ("tl", "tr") else H - ch - MARG
    d.rounded_rectangle([x, y, x + CARD_W, y + ch], 11,
                        fill=(255, 255, 255, 243), outline=(0, 0, 0, 30), width=1)
    cy = y + PAD
    d.text((x + PAD, cy), f"{idx+1} / {len(STOPS)}", font=F_NUM, fill=(125, 125, 130))
    cy += F_NUM.size + 7
    for l in tl:
        d.text((x + PAD, cy), l, font=F_TTL, fill=(22, 22, 26)); cy += lh_t
    cy += 5
    for l in sl:
        d.text((x + PAD, cy), l, font=F_SUB, fill=(72, 72, 80)); cy += lh_s
    return img


tmp = pathlib.Path(tempfile.mkdtemp(prefix="apoetour_"))
writer = imageio_ffmpeg.write_frames(
    str(HERE / "apoe_tour.mp4"), (W, H), fps=A.fps, quality=8,
    macro_block_size=1, output_params=["-pix_fmt", "yuv420p"])
writer.send(None)

cache, gif_frames = {}, []
for n, (box, idx) in enumerate(plan):
    key = tuple(round(v, 2) for v in box)
    if key in cache:
        img = cache[key].copy()
    else:
        s2 = re.sub(r'viewBox="[^"]*"',
                    'viewBox="%s"' % " ".join(f"{v:.2f}" for v in box), svg, count=1)
        png = cairosvg.svg2png(bytestring=s2.encode(), output_width=W,
                               output_height=H, background_color=page_bg)
        img = Image.open(__import__("io").BytesIO(png)).convert("RGB")
        if len(cache) < 40:
            cache[key] = img.copy()
    caption(img, idx)
    writer.send(img.tobytes())
    if A.gif and n % max(1, A.fps // 10) == 0:
        gif_frames.append(img.resize((W // 2, H // 2)))
    if n % 60 == 0:
        print(f"\r  frame {n+1}/{len(plan)}", end="", flush=True)
writer.close()
shutil.rmtree(tmp, ignore_errors=True)
mp4 = HERE / "apoe_tour.mp4"
print(f"\nwrote {mp4.name} ({mp4.stat().st_size/1e6:.1f} MB, {len(plan)/A.fps:.1f} s, {W}x{H})")

if A.gif and gif_frames:
    g = HERE / "apoe_tour.gif"
    gif_frames[0].save(g, save_all=True, append_images=gif_frames[1:],
                       duration=100, loop=0, optimize=True)
    print(f"wrote {g.name} ({g.stat().st_size/1e6:.1f} MB, {len(gif_frames)} frames)")
