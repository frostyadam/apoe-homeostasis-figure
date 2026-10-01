#!/usr/bin/env python3
"""Build apoe_tour.html - a standalone guided zoom tour over the master cartoon.

The cartoon drawing code is EXTRACTED from page_template.html at build time, never
hand-copied, so the tour cannot drift from the master figure. Re-run this after any
change to drawA()/drawMTOR() in the template.

drawA + drawMTOR are self-contained: they need only $, css, el, txt, NS, FONT_SCALE
and the :root CSS tokens. Verified 2026-09-26 - no reference to the figdata blob.
"""
import re, sys, pathlib

HERE = pathlib.Path(__file__).parent
SRC = HERE / "page_template.html"
OUT = HERE / "apoe_tour.html"

src = SRC.read_text()

# ---- 1. the CSS token block (carries :root light/dark colour tokens drawA reads) ----
style = src[src.index("<style>"): src.index("</style>") + 8]

# ---- 2. the cartoon SVG shell, so viewBox + aria-label stay in sync ----
m = re.search(r'<svg id="schem"[^>]*>', src)
if not m:
    sys.exit("could not find svg#schem in the template")
shell = m.group(0)
vb = re.search(r'viewBox="([^"]+)"', shell).group(1)
VB = [float(v) for v in vb.split()]
aria = re.search(r'aria-label="([^"]*)"', shell)
aria = aria.group(1) if aria else ""

# ---- 3. the script: helpers + drawA + drawMTOR ----
js = src[src.rindex("<script>") + 8: src.rindex("</script>")]
lines = js.split("\n")

# Transitive dependency closure from drawA/drawMTOR over TOP-LEVEL declarations
# (column 0 only - indented matches are locals). We collect the line SPANS the
# closure needs and emit deduplicated spans in source order, so single-letter
# aliases that resolve to a real definition's span collapse harmlessly.
defs = {}
for i, l in enumerate(lines):
    if re.match(r"\s", l):
        continue
    m = (re.match(r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=", l)
         or re.match(r"function\s+([A-Za-z_$][\w$]*)\s*\(", l))
    if not m:
        continue
    depth, end = 0, i
    for j in range(i, len(lines)):
        depth += (lines[j].count("{") - lines[j].count("}")
                  + lines[j].count("(") - lines[j].count(")"))
        if depth <= 0:
            end = j
            break
    for pair in re.findall(
            r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=|,\s*([A-Za-z_$][\w$]*)\s*=\s*[\{\[]", l):
        for n in pair:
            if n:
                defs.setdefault(n, (i, end))
    defs.setdefault(m.group(1), (i, end))

KW = set("if for while return function const let var new typeof of in else do switch case "
         "break continue true false null undefined this try catch throw class delete void "
         "instanceof yield await async".split())
GL = set("document window Math Object Array String Number JSON Set Map console performance "
         "requestAnimationFrame cancelAnimationFrame getComputedStyle matchMedia addEventListener "
         "parseInt parseFloat isNaN Infinity NaN Boolean Date RegExp Promise URLSearchParams "
         "location setTimeout clearTimeout MutationObserver navigator".split())


def idents(text):
    return {t for t in re.findall(r"[A-Za-z_$][\w$]*", text)
            if t not in KW and t not in GL}


need, seen = {"drawA", "drawMTOR"}, set()
while need - seen:
    n = next(iter(need - seen))
    seen.add(n)
    if n not in defs:
        continue
    a, b = defs[n]
    for r in idents("\n".join(lines[a:b + 1])):
        if r in defs:
            need.add(r)

spans = sorted({defs[n] for n in need if n in defs})
merged = []
for a, b in spans:
    if merged and a <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], b))
    else:
        merged.append((a, b))
cartoon = "\n".join("\n".join(lines[a:b + 1]) for a, b in merged)

for req in ("function drawA(", "function drawMTOR(", "catCol", "geneSpans"):
    if req not in cartoon:
        sys.exit("extraction lost " + req)

# Only the figdata keys the closure actually reads get embedded (keeps the page small).
DKEYS = sorted(set(re.findall(r"\bD\.([A-Za-z_]\w*)", cartoon)))
import json
fd = json.load(open(HERE / "figdata.json"))
missing = [k for k in DKEYS if k not in fd]
if missing:
    sys.exit("figdata.json lacks keys the cartoon needs: " + ", ".join(missing))
dblob = json.dumps({k: fd[k] for k in DKEYS},
                   separators=(",", ":")).replace("</", "<\\/")

# ---- 4. the camera path ------------------------------------------------------------
# Boxes are [x, y, w, h] in cartoon user units (viewBox 0 -36 1100 766). They are
# normalised to the master aspect ratio at runtime by fit(), so loose framing is fine.
# Coordinates come from a headless getBBox() sweep of every <text> in the cartoon.
STOPS = [
    dict(t="APOE homeostasis", s="The whole cell. Synthesis and secretion on the left, uptake and lysosomal traffic on the right. Gene names appear only where there is disease or APOE-dependent evidence.",
         box=[0, -36, 1100, 766], side="right", glyphs=["apoe", "particle", "chol"]),
    dict(t="Lipoparticle biogenesis", s="APOE is inserted into the ER as it is translated. Alongside it the mevalonate enzymes end at DHCR24, which makes cholesterol from desmosterol. The first particle forms at the Golgi with ABCA1.",
         box=[102, 330, 367, 256], side="right", glyphs=["apoe", "particle", "chol"]),
    dict(t="Lipoparticle secretion and maturation", s="The vesicle fuses with the membrane and ABCA1 and ABCA7 lipidate APOE. Outside, particles carry APOC1, APOC2 and CLU/APOJ, and PLTP remodels them.",
         box=[10, -36, 482, 145], side="right", glyphs=["apoe", "particle", "chol"]),
    dict(t="Lipoparticle receptors", s="HSPG captures the particle and hands it to a receptor. Each receptor is filled with its evidence colour.",
         box=[470, -36, 414, 288], side="right", glyphs=["particle"],
         notes=["<b>Therapeutic hypothesis 1</b> \u2014 the antibody gripping the particle is an <b>anti-APOE4 mAb</b>, drawn to block uptake sterically at the moment HSPG hands the particle to the receptors. APOE4 binds LDLR most tightly of the three isoforms (K<sub>d</sub> 9 nM vs 16 and 800 nM), so uptake is where the isoform difference is largest.", "It is a <b>hypothesis, not a result</b>: nothing in our data speaks to it, it must cross the blood-brain barrier, and E4 and E3 particles differ by one buried residue.", "The series above ranks the isoforms by LDLR affinity. <b>APOE3</b> is the reference (Cys112, Arg158).", "<b>APOE2</b> is <b>R158C</b> (Arg158\u2192Cys). <b>APOE4</b> is <b>C112R</b> (Cys112\u2192Arg).", "<b>E3-Cc</b> is <b>APOE3-Christchurch</b>, <b>R136S</b> (Arg136\u2192Ser), on an APOE3 backbone \u2014 a protective variant.", "Residue numbers are for the mature protein; add 18 for precursor numbering."]),
    dict(t="Receptor-mediated endocytosis", s="PICALM and BIN1 drive internalisation. The neck undergoes scission, then the coat uncoats. Cargo legend at top right.",
         box=[626.4, -10.4, 473.66, 329.91], side="right", glyphs=["particle", "abeta"],
         notes=["<b>Second interception, top right</b> \u2014 the same anti-APOE4 antibody drawn ENGAGED rather than approaching: both paratopes on the particle surface, the Fc trailing, and the route to the clathrin pit dashed and barred. It asserts only that <b>uptake is the step being targeted</b>; isoform selectivity is the unsolved part, since APOE3 and APOE4 differ by C112R, which is not surface-exposed on the lipidated particle.", "<b>E3-Cc</b> is <b>APOE3-Christchurch</b>, <b>R136S</b> (Arg136\u2192Ser), on an APOE3 backbone. APOE2 is R158C, APOE4 is C112R.", "<b>LDLR K<sub>d</sub></b> on lipidated nanodiscs by SPR: E2 <b>800 nM</b> \u00b7 E3 <b>16 nM</b> \u00b7 E4 <b>9 nM</b>.", "E3-Cc has <b>no published K<sub>d</sub></b>; it binds at <b>41%</b> of E3 in a fibroblast assay.", "The E4 step is ~<b>1.8-fold</b> by SPR, but runs with our finding that <b>APOE4 lipoparticles accumulate intracellularly</b> more than APOE3 \u2014 plausibly extra receptor engagement or slower recycling."]),
    dict(t="Early endosome", s="Mildly acidic, and still holding APOE. A vesicle buds off to recycle receptors; the rest matures onward.",
         box=[680.4, 169, 419.6, 292.2], side="right", glyphs=["apoe", "particle"]),
    dict(t="Lipid and sterol catabolism, mTORC1 activation", s="LIPA frees cholesterol from cholesteryl ester, and NPC2 with NPC1 export it at ER contact sites. TM6SF1 and SLC38A9 sense it and recruit mTORC1. Cholesterol and BMP rise here in APOE4. At left, a lysosome carrying undigested amyloid-\u03b2 and tau heads for exocytosis.",
         box=[505, 315.7, 595, 414.3], side="right", glyphs=["chol", "bmp", "whorl", "particle", "abeta", "tau"],
         notes=["<b>Therapeutic hypothesis 2</b> \u2014 the <b>rapalog</b> at right inhibits mTORC1 where cholesterol activates it on the lysosome. APOE4 glia hold 3\u00d7 more lysosomal cholesterol, and TM6SF1 engages Ragulator cholesterol-dependently. But every gene in this module is transcriptionally <b>flat</b>, so the inhibitory bar is drawn on the pathway, not on our measurements.", "<b>LIPA carries a \u2020</b> because its blue comes from one ancestry stratum and reverses in the other: African-ancestry \u22120.61, European-ancestry <b>+0.16</b>, pooled \u22120.25 (between-stratum q 8.7e\u22128). \u201cLower in APOE4\u201d is not supportable for LIPA as a general claim.", "The lysosomal cholesterol machinery drawn here \u2014 NPC1, NPC2, TM6SF1, Ragulator, the Rag GTPases, mTORC1 \u2014 is transcriptionally <b>flat</b>: a lipid phenotype without a transcriptional signature."]),
    dict(t="Transcriptional consequences and targets", s="Less desmosterol leaves LXR/RXR on the LXR response element under-agonised, so the efflux programme falls.",
         box=[0, 429, 380.5, 265], side="right", glyphs=["chol"],
         notes=["<b>Therapeutic hypothesis 3</b> \u2014 <b>chemical reprogramming</b>, marked in the nucleus, is the only intervention on this figure aimed at cell state rather than at a single protein. Nothing in our data tests it: the label marks where such an intervention would act, not a result.", "<b>LXR agonism is pharmacologically responsive in APOE4 glia</b>, even though no agonist is drawn: GW3965 and T0901317 restore APOE4 cholesterol efflux to untreated-APOE3 levels. The rescue is incomplete, and systemic LXR agonism drives hepatic lipogenesis.", "<b>Direct LXR/RXR targets down in human spatial transcriptomics data:</b> PLTP <b>\u22120.51</b>, the APOE/APOC1/APOC2 cluster (\u22120.18, \u22120.75, \u22120.41), CD36 <b>\u22120.92</b>.", "APOD is drawn uncoloured: it does NOT move in this pooled contrast, but within European-ancestry donors it is <b>up +0.66</b>, the 99.4th percentile of all genes.", "ABCA1 and ABCA7 are <b>flat in the spatial transcript data</b> (FDR 0.13 and 0.70) but are decreased in isogenic APOE4 astrocytes."]),
    dict(t="The whole route", s="Synthesis to secretion to uptake to the lysosome, cholesterol back to the ER, and the response in the nucleus.",
         box=[0, -36, 1100, 766], side="right", glyphs=["apoe", "particle", "chol"]),

]

stops_js = ",\n".join(
    "  {t:%s, s:%s, box:[%s], side:%s, glyphs:%s%s}" % (
        json.dumps(s["t"]), json.dumps(s["s"]),
        ",".join(str(v) for v in s["box"]),
        json.dumps(s.get("side", "right")), json.dumps(s.get("glyphs", [])),
        ", notes:" + json.dumps(s["notes"]) if s.get("notes") else "")
    for s in STOPS
)

TOUR_CSS = """
<style>
html,body{margin:0;padding:0;height:100%;background:var(--page);color:var(--ink);
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
#stage{position:fixed;inset:0 0 34px 0;display:flex;align-items:stretch;gap:22px;padding:12px 16px}
#fig{flex:1 1 auto;min-width:0;display:flex;align-items:center;justify-content:center}
/* Lock the element to the master viewBox aspect so the rendered area EQUALS the
   viewBox. With width/height:100% the element took the window aspect and SVG's
   default xMidYMid meet letterboxed the drawing, putting blank page bands inside
   the frame (~205px each side at 16:9) - which is what stopped zoomed stops from
   reading as a clean rectangle. */
#schem{aspect-ratio:1100 / 766;width:auto;height:auto;max-width:100%;max-height:100%;
  min-width:0 !important;background:var(--page);
  border:1px solid var(--rule);border-radius:3px}
/* The caption is a SIDE PANEL, never an overlay - it must not cover the drawing.
   `side` on each stop puts it left or right of the figure; a consistent side is
   easier to follow in a talk, so all stops use one unless deliberately flipped. */
#card{flex:0 0 clamp(250px,26vw,400px);align-self:center;max-height:100%;overflow:auto;background:var(--surf);
  border:1px solid var(--rule);border-radius:10px;padding:20px 22px 22px;
  transition:opacity .2s}
body[data-side="left"] #stage{flex-direction:row-reverse}
#num{font:600 12px/1 ui-monospace,monospace;letter-spacing:.09em;
  color:var(--muted);text-transform:uppercase}
#ttl{font-weight:640;font-size:23px;line-height:1.22;margin:10px 0 10px;letter-spacing:-.012em}
#sub{font-size:16.5px;line-height:1.55;color:var(--ink2)}
/* Evidence key, shown only on the overview stop. Swatches read their colour from
   the same :root tokens the cartoon's gene labels use, so they cannot drift. */
#leg{margin-top:16px;padding-top:14px;border-top:1px solid var(--rule);display:none}
#leg.on{display:block}
#leg .r{display:flex;gap:10px;align-items:flex-start;font-size:15.5px;line-height:1.42;
  color:var(--ink2);margin-bottom:9px}
#leg .sw{width:14px;height:14px;border-radius:3px;flex:0 0 auto;margin-top:3px}
#leg .gl{flex:0 0 auto;width:36px;height:23px;margin-top:-1px}
#leg .k{font-weight:700;color:var(--ink);flex:0 0 auto;width:14px;text-align:center;
  font-size:15px;margin-top:0}
#leg .note{font-size:14px;line-height:1.42;color:var(--muted)}
#leg .nb{font-size:13.5px;line-height:1.45;color:var(--ink2);margin:0 0 8px;
  padding-left:11px;border-left:2px solid var(--rule)}
#leg .nb b{color:var(--ink);font-weight:640}
#leg .nb sub{font-size:.72em}
/* Narrow windows: stack the panel under the figure rather than squeezing it. */
@media (max-width:820px){
  #stage{flex-direction:column !important;align-items:center}
  #card{flex:0 0 auto;max-width:96%}
}
#bar{position:fixed;left:0;right:0;bottom:0;height:34px;display:flex;
  align-items:center;gap:7px;justify-content:center;background:var(--page);
  border-top:1px solid var(--rule);z-index:6}
.dot{width:8px;height:8px;border-radius:50%;background:var(--rule);cursor:pointer;
  border:0;padding:0;transition:background .2s,transform .2s}
.dot.on{background:var(--ink);transform:scale(1.32)}
/* inside the bottom bar, never over the drawing */
#hint{position:fixed;right:14px;bottom:10px;font:11px/1 ui-monospace,monospace;
  color:var(--muted);z-index:7}
body.clean #bar,body.clean #hint{display:none}
@media print{#bar,#hint{display:none}}
</style>
"""

TOUR_JS = """
<script>
const STOPS=[
%(stops)s
];
const VB=[%(vb)s];                       // master viewBox
const AR=VB[2]/VB[3];                    // master aspect ratio
const svg=document.getElementById("schem");
/* Colour rows are derived at runtime from the gene labels actually inside the
   current frame, so a stop's key can never disagree with what is on screen. */
const CAT_TEXT={gwas:["--c-gwas","AD GWAS locus (consensus Tier 1/2)"],
                ot:  ["--c-ot",  "Open Targets AD genetic association"],
                up:  ["--c-up",  "higher expression in APOE4 carriers"],
                dn:  ["--c-dn",  "lower expression in APOE4 carriers"]};
const CAT_SEQ=["gwas","ot","up","dn"];
const LEGEND_MARKS={cis:["\u2021","within 1 Mb of APOE, so the difference can follow the haplotype"],
                    dot:["\u25cf","one further category the gene also belongs to"]};
/* Glyph rows reuse the cartoon's own drawing functions, so the swatch is literally
   the same mark as the one in the figure. */
const GLYPHS={
  apoe:     ["APOE protein, a four-helix bundle", g=>apoeBundle(g,18,11.5,0,2.0)],
  chol:     ["cholesterol", g=>el("circle",{cx:18,cy:11.5,r:5.6,fill:css("--chol")},g)],
  particle: ["APOE lipoparticle, cholesterol inside", g=>particle(g,18,11.5,10.5)],
  abeta:    ["amyloid-\u03b2 aggregate", g=>fibAbeta(g,4,11.5,28)],
  tau:      ["tau aggregate", g=>fibTau(g,4,11.5,28)],
  bmp:      ["BMP, a lysosomal lipid that accumulates with age, in storage disorders and in drug-induced phospholipidosis", g=>bmpGlyph(g,18,11.5,0,1.5)],
  whorl:    ["whorl of undigested membrane", g=>whorl(g,18,11.5,9.5,2.2)]
};
function geneTokens(txt){            // split on any non-alphanumeric run: handles
  return txt.split(/[^A-Za-z0-9]+/)  // middots, slashes, spaces and the marks at once
            .filter(Boolean).map(t=>t.toUpperCase());
}
function rootBox(t){
  const b=t.getBBox(), m=svg.getScreenCTM().inverse().multiply(t.getScreenCTM());
  const P=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]]
    .map(([x,y])=>[m.a*x+m.c*y+m.e, m.b*x+m.d*y+m.f]);
  const xs=P.map(q=>q[0]), ys=P.map(q=>q[1]);
  return [Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)];
}
function catsInView(box){
  const [X,Y,W,H]=box;
  const cats=new Set(); let cis=false, multi=false;
  svg.querySelectorAll("text").forEach(t=>{
    const s=(t.textContent||"").trim(); if(!s) return;
    const [x0,y0,x1,y1]=rootBox(t);
    if(!(x0>=X-0.5 && x1<=X+W+0.5 && y0>=Y-0.5 && y1<=Y+H+0.5)) return;
    if(s.indexOf("\u2021")>=0) cis=true;
    geneTokens(s).forEach(gname=>{
      const rec=(D.genecat||{})[gname]; if(!rec) return;
      const c=rec.cats||[];
      if(c.length>1) multi=true;
      c.forEach(k=>cats.add(k));
    });
  });
  return {cats:CAT_SEQ.filter(k=>cats.has(k)), cis, multi};
}
const card=document.getElementById("card"),legE=document.getElementById("leg"),numE=document.getElementById("num"),
      ttlE=document.getElementById("ttl"),subE=document.getElementById("sub"),
      barE=document.getElementById("bar");
let i=0, anim=null;

/* Expand a loose box to the master aspect ratio so framing is predictable and
   SVG's preserveAspectRatio never letterboxes in a way we did not intend. */
function fit(b){
  let [x,y,w,h]=b;
  if(w/h > AR){ const nh=w/AR; y-=(nh-h)/2; h=nh; }
  else        { const nw=h*AR; x-=(nw-w)/2; w=nw; }
  /* Clamp inside the master viewBox so a frame never shows blank canvas past the
     drawing's edge - that is what made zoomed stops read as ragged rather than as a
     clean rectangle. The canvas is exactly AR, so w<=VB[2] implies h<=VB[3]. */
  if(w>=VB[2]) return VB.slice();
  x=Math.min(Math.max(x,VB[0]),VB[0]+VB[2]-w);
  y=Math.min(Math.max(y,VB[1]),VB[1]+VB[3]-h);
  return [x,y,w,h];
}
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const setVB=b=>svg.setAttribute("viewBox",b.map(v=>v.toFixed(2)).join(" "));

function go(n,instant){
  n=Math.max(0,Math.min(STOPS.length-1,n));
  const from=(svg.getAttribute("viewBox")||VB.join(" ")).split(/\\s+/).map(Number);
  const to=fit(STOPS[n].box);
  i=n; paint();
  if(anim) cancelAnimationFrame(anim);
  if(instant||from.some(isNaN)){ setVB(to); return; }
  const dur=900, t0=performance.now();
  (function step(now){
    const k=ease(Math.min(1,(now-t0)/dur));
    setVB(from.map((v,j)=>v+(to[j]-v)*k));
    if(k<1) anim=requestAnimationFrame(step);
  })(t0);
}
function paint(){
  const s=STOPS[i];
  document.body.dataset.side = s.side || "right";
  buildLegend(s);
  numE.textContent=`${i+1} / ${STOPS.length}`;
  ttlE.textContent=s.t; subE.textContent=s.s;
  [...barE.children].forEach((d,j)=>d.classList.toggle("on",j===i));
}
function buildLegend(s){
  const glyphs=s.glyphs||[];
  const {cats,cis,multi}=catsInView(fit(s.box));
  const show=(cats.length||glyphs.length);
  legE.classList.toggle("on", !!show);
  if(!show){ legE.innerHTML=""; return; }
  legE.innerHTML="";
  cats.forEach(k=>{
    const [v,txt]=CAT_TEXT[k];
    const r=document.createElement("div"); r.className="r";
    const sw=document.createElement("span"); sw.className="sw";
    sw.style.background="var("+v+")";
    const lb=document.createElement("span"); lb.textContent=txt;
    r.append(sw,lb); legE.appendChild(r);
  });
  glyphs.forEach(key=>{
    const entry=GLYPHS[key]; if(!entry) return;
    const [txt,draw]=entry;
    const r=document.createElement("div"); r.className="r";
    const sv=document.createElementNS(NS,"svg");
    sv.setAttribute("viewBox","0 0 36 23"); sv.setAttribute("class","gl");
    const g=el("g",{},sv); draw(g);
    const lb=document.createElement("span"); lb.textContent=txt;
    r.append(sv,lb); legE.appendChild(r);
  });
  (s.notes||[]).forEach(html=>{
    const d=document.createElement("div"); d.className="nb"; d.innerHTML=html;
    legE.appendChild(d);
  });
  [multi?"dot":null, cis?"cis":null].filter(Boolean).forEach(k=>{
    const [sym,txt]=LEGEND_MARKS[k];
    const r=document.createElement("div"); r.className="r";
    const kk=document.createElement("span"); kk.className="k"; kk.textContent=sym;
    const lb=document.createElement("span"); lb.className="note"; lb.textContent=txt;
    r.append(kk,lb); legE.appendChild(r);
  });
}
barE.innerHTML=STOPS.map((s,j)=>
  `<button class="dot" data-i="${j}" title="${s.t.replace(/"/g,"&quot;")}" aria-label="${s.t.replace(/"/g,"&quot;")}"></button>`).join("");
barE.addEventListener("click",e=>{const d=e.target.closest(".dot"); if(d) go(+d.dataset.i)});

addEventListener("keydown",e=>{
  if(["ArrowRight","ArrowDown"," ","PageDown","Enter","n"].includes(e.key)){go(i+1);e.preventDefault()}
  else if(["ArrowLeft","ArrowUp","PageUp","Backspace","p"].includes(e.key)){go(i-1);e.preventDefault()}
  else if(e.key==="Home"||e.key==="0"){go(0)}
  else if(e.key==="End"){go(STOPS.length-1)}
  else if(e.key==="c"){document.body.classList.toggle("clean")}
  else if(e.key==="t"){const r=document.documentElement;
    r.dataset.theme = r.dataset.theme==="dark" ? "light" : "dark"; drawA(); go(i,true)}
  else if(e.key==="f"){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
});
addEventListener("click",e=>{ if(!e.target.closest("#bar,#card")) go(i+1) });

drawA();
go(0,true);
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",()=>{drawA();go(i,true)});
</script>
"""

out = f"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>APOE Homeostasis Tour</title>
{style}
{TOUR_CSS}
<div id="stage">
  <div id="fig"><svg id="schem" viewBox="{vb}" role="img" aria-label="{aria}"></svg></div>
  <aside id="card"><div id="num"></div><div id="ttl"></div><div id="sub"></div><div id="leg"></div></aside>
</div>
<div id="bar"></div>
<div id="hint">click / → next · ← back · c chrome · t theme · f full</div>
<div id="tip" hidden></div>
<script>
{cartoon.replace("/*__DATA__*/null", dblob)}
</script>
{TOUR_JS % dict(stops=stops_js, vb=",".join(str(v) for v in VB))}
"""

# Emit the camera path so the MP4 renderer reads ONE definition, not a copy.
(HERE / "tour_stops.json").write_text(json.dumps(
    dict(viewBox=VB, stops=STOPS), indent=1))

OUT.write_text(out)
print(f"wrote {OUT.name} ({len(out)/1024:.0f} KB, {len(STOPS)} stops)")
print(f"  cartoon closure: {len(cartoon.splitlines())} lines, figdata keys {DKEYS}")
print(f"  viewBox: {vb}  aspect {VB[2]/VB[3]:.3f}")
print("  wrote tour_stops.json")
