#!/usr/bin/env python
"""Sterol / LXR sub-panel v3 for the Endocytosis Atlas panel A.

v2 framed two opposing arms (desmosterol vs 24S-OHC) and left LXR tone unresolved.
v3 is restructured after the Blanchard 2022 supplements:
  - Arm A is PROMOTED: DHCR24 up is replicated in 5 datasets, 3 platforms, 2 species.
  - Arm B is WITHDRAWN: CYP46A1 up is contradicted in isogenic human oligodendroglia
    (-0.707, q 1.7e-4) and null post-mortem; the cell-type rescue fails (our ERC Oli leans +).
  - The consequence is drawn: less LXR agonism -> less efflux -> CE and BMP storage.
Static SVG in its own coordinate space; uses the template's CSS tokens.
"""
W, H = 1000, 500
o = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, cls="", fs=12, anchor="start", weight=None, fill=None, style=None):
    a = f' class="{cls}"' if cls else ""
    b = f' font-weight="{weight}"' if weight else ""
    f = f' fill="{fill}"' if fill else ""
    st = f' style="{style}"' if style else ""
    o.append(f'<text x="{x}" y="{y}" font-size="{fs}" text-anchor="{anchor}"{a}{b}{f}{st}>{esc(s)}</text>')


def box(x, y, w, h, fill="var(--surf)", stroke="--rule", sw=1, rx=4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
             f'stroke="var({stroke})" stroke-width="{sw}"{d}/>')


def bar(x, y, w, h, col):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.5" fill="var({col})"/>')


def arrow(x1, y1, x2, y2, col="--ink2", sw=1.8):
    o.append(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="var({col})" stroke-width="{sw}" '
             f'fill="none" marker-end="url(#ah3)"/>')


def blunt(x1, y1, x2, y2, col="--c-dn", sw=2.2):
    o.append(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="var({col})" stroke-width="{sw}" fill="none"/>')
    o.append(f'<path d="M {x2} {y1-10} L {x2} {y1+10}" stroke="var({col})" stroke-width="3"/>')


AL = ("Sterol-enzyme evidence restructured. Top: DHCR24 is higher in APOE4 in five independent datasets across "
      "three platforms and two species, including isogenic human iPSC oligodendroglia. Middle: DHCR24 consumes "
      "desmosterol, an endogenous LXR agonist, so the replicated rise predicts less desmosterol and weaker "
      "LXR/RXR agonism; the DHCR24-desmosterol-LXR-alpha axis is genetically proven in liver. Right: the predicted "
      "consequence is less cholesterol efflux and more storage, which matches 35 of 35 cholesteryl-ester species "
      "raised about nine-fold in APOE4 oligodendroglia, BMP raised in three cohorts, and LIPA lower. Bottom: the "
      "opposing 24S-hydroxycholesterol arm is withdrawn because CYP46A1 is down in isogenic human oligodendroglia "
      "and null post-mortem. No sterol or oxysterol is measured in any of these datasets.")
o.append(f'<svg id="sterolnr" viewBox="0 0 {W} {H}" style="min-width:760px" role="img" aria-label="{esc(AL)}">')
o.append('<defs><marker id="ah3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         'orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9 z" fill="var(--ink2)"/></marker></defs>')

# ---------------- ROW A : the replicated observation ----------------
t(0, 14, "THE REPLICATED OBSERVATION — DHCR24 higher in APOE4, five datasets, three platforms, two species",
  cls="mono muted", fs=11, weight=600)
box(0, 24, 1000, 146)
t(12, 42, "dataset", cls="mono muted", fs=9.5)
t(470, 42, "log₂FC", cls="mono muted", fs=9.5, anchor="end")
t(486, 42, "significance", cls="mono muted", fs=9.5)
t(660, 42, "what it controls for", cls="mono muted", fs=9.5)

ROWS = [
    ("our LC Visium · 5-domain pool", 0.276, "FDR 5.7×10⁻⁷", "spot-level, E4 vs E2 carriers", True),
    ("our ERC snRNA · oligodendrocytes", 0.201, "n.s. (underpowered)", "cell-type resolved, same direction", False),
    ("isogenic iPSC oligodendroglia", 0.614, "q 1.7×10⁻⁴", "genotype is the ONLY variable", True),
    ("post-mortem oligodendrocytes · Nebula", 0.551, "padj 0.024", "human tissue, per-nucleus", True),
    ("post-mortem oligodendrocytes · Wilcoxon", 0.118, "top-ranked, up in AD + non-AD", "~10⁵ nuclei, both strata", True),
]
SC = 210.0  # px per log2 unit
for i, (lab, lf, sig, ctl, solid) in enumerate(ROWS):
    y = 60 + i * 19
    t(12, y + 4, lab, cls="mono", fs=10.5, fill=None if solid else "var(--ink2)")
    bar(300, y - 5, max(2.0, lf * SC), 10, "--c-up")
    if not solid:
        o.append(f'<rect x="300" y="{y-5}" width="{max(2.0, lf*SC):.1f}" height="10" rx="1.5" '
                 f'fill="var(--surf)" opacity="0.45"/>')
    t(470, y + 4, f"+{lf:.3f}", cls="mono", fs=10.5, anchor="end", weight=500, fill="var(--c-up)")
    t(486, y + 4, sig, cls="mono", fs=10, fill="var(--ink2)")
    t(660, y + 4, ctl, cls="mono", fs=10, fill="var(--ink2)")
t(12, 164, "DHCR24 = 24-dehydrocholesterol reductase: converts desmosterol → cholesterol. "
            "Also seladin-1, reduced in vulnerable neurons in AD.", cls="mono muted", fs=9.5)

# ---------------- ROW B : mechanism chain ----------------
t(0, 192, "THE PREDICTION IT LICENSES — less agonist reaching LXR/RXR", cls="mono muted", fs=11, weight=600)
box(0, 202, 596, 124)
o.append('<circle cx="40" cy="242" r="9" fill="var(--chol)"/>')
t(40, 268, "desmosterol", cls="mono", fs=10, anchor="middle", weight=600)
t(40, 280, "LXR agonist", cls="mono muted", fs=8.5, anchor="middle")
arrow(64, 242, 112, 242)
t(88, 234, "consumed", cls="mono", fs=9, anchor="middle", fill="var(--ink2)")
t(88, 256, "faster", cls="mono", fs=9, anchor="middle", fill="var(--ink2)")
o.append('<circle cx="140" cy="242" r="9" fill="none" stroke="var(--c-dn)" stroke-width="1.6" stroke-dasharray="2.5 2.5"/>')
o.append('<circle cx="140" cy="242" r="3.4" fill="var(--chol)" opacity="0.3"/>')
t(140, 268, "desmosterol ↓", cls="mono", fs=10, anchor="middle", weight=600, fill="var(--c-dn)")
t(140, 280, "predicted", cls="mono muted", fs=8.5, anchor="middle")
blunt(164, 242, 226, 242)
t(195, 230, "LESS agonism", cls="mono", fs=9.5, anchor="middle", weight=600, fill="var(--c-dn)")
box(240, 212, 156, 92, fill="var(--neutral)", stroke="--ink", sw=1.6, rx=6)
t(318, 242, "LXR / RXR", fs=15, anchor="middle", weight=600)
t(318, 260, "NR1H2 / NR1H3", cls="mono", fs=9.5, anchor="middle", fill="var(--ink2)")
t(318, 280, "hypothesised:", cls="mono", fs=9, anchor="middle", fill="var(--ink2)")
t(318, 293, "HYPO-agonised", cls="mono", fs=10, anchor="middle", weight=600, fill="var(--c-dn)")
arrow(400, 242, 438, 242)
t(446, 234, "efflux ↓", cls="mono", fs=11, weight=600, fill="var(--c-dn)")
t(446, 250, "PLTP −0.505", cls="mono", fs=9.5, fill="var(--ink2)")
t(446, 264, "isogenic glia, IPA:", cls="mono", fs=9.5, fill="var(--ink2)")
t(446, 277, "efflux z −2.38", cls="mono", fs=9.5, fill="var(--ink2)")
t(446, 290, "accum. z +2.77", cls="mono", fs=9.5, fill="var(--ink2)")
t(12, 340, "Axis proven causally, in liver: DHCR24 inhibition raises desmosterol; every effect abolished in LXRα-null mice (EMBO Mol Med 2023).", cls="mono muted", fs=9.5)
t(12, 353, "ABCA1 n.s. (−0.221, FDR 0.13); ABCG1, ABCG4, MYLIP not measured; APOE/APOC1/APOC2 down but cis ‡.", cls="mono muted", fs=9.5)

# ---------------- ROW C : the storage phenotype ----------------
t(612, 192, "WHAT IS ACTUALLY MEASURED DOWNSTREAM — storage", cls="mono muted", fs=11, weight=600)
box(612, 202, 388, 124, fill="var(--band)")
t(624, 224, "cholesteryl ester", cls="mono", fs=11.5, weight=600, fill="var(--c-up)")
t(988, 224, "35 / 35 species ↑", cls="mono", fs=11.5, anchor="end", weight=600, fill="var(--c-up)")
t(624, 239, "isogenic APOE4/4 oligodendroglia, no tau · +3.17 log₂ (≈9×)", cls="mono", fs=9.5, fill="var(--ink2)")
t(624, 264, "BMP (lysosomal)", cls="mono", fs=11.5, weight=600, fill="var(--c-up)")
t(988, 264, "↑ in 3 cohorts", cls="mono", fs=11.5, anchor="end", weight=600, fill="var(--c-up)")
t(624, 279, "APOE4 EC dose p=0.007 · APOE4 forebrain · mTORC1 cortex", cls="mono", fs=9.5, fill="var(--ink2)")
t(624, 304, "LIPA", cls="mono", fs=11.5, weight=600, fill="var(--c-dn)")
t(988, 304, "−0.249 (FDR 0.003)", cls="mono", fs=11.5, anchor="end", weight=600, fill="var(--c-dn)")
t(624, 319, "lysosomal CE hydrolase — the direction that PERMITS storage", cls="mono", fs=9.5, fill="var(--ink2)")
arrow(556, 300, 606, 280)

# ---------------- ROW D : withdrawn arm ----------------
t(0, 372, "WITHDRAWN IN THIS REVISION — the opposing 24S-OHC arm", cls="mono muted", fs=11, weight=600)
box(0, 382, 1000, 78, dash="4 3")
t(12, 402, "CYP46A1", cls="mono", fs=11.5, weight=600)
t(12, 418, "read as: up → more 24S-OHC", cls="mono", fs=9.5, fill="var(--ink2)")
t(12, 431, "→ MORE agonism", cls="mono", fs=9.5, fill="var(--ink2)")
t(250, 402, "our LC pool", cls="mono", fs=10, fill="var(--ink2)")
t(468, 402, "+0.180", cls="mono", fs=10.5, anchor="end", weight=500, fill="var(--c-up)")
t(478, 402, "FDR 0.037", cls="mono", fs=9.5, fill="var(--ink2)")
t(250, 419, "isogenic iPSC oligodendroglia", cls="mono", fs=10, fill="var(--ink2)")
t(468, 419, "−0.707", cls="mono", fs=10.5, anchor="end", weight=600, fill="var(--c-dn)")
t(478, 419, "q 1.7e-04 — OPPOSITE", cls="mono", fs=9.5, weight=600, fill="var(--c-dn)")
t(250, 436, "post-mortem oligodendrocytes", cls="mono", fs=10, fill="var(--ink2)")
t(468, 436, "+0.095", cls="mono", fs=10.5, anchor="end", fill="var(--ink2)")
t(478, 436, "p 0.44 — null", cls="mono", fs=9.5, fill="var(--ink2)")
t(660, 402, "Cell-type rescue FAILS: our ERC oligodendrocytes", cls="mono", fs=9.5, fill="var(--ink2)")
t(660, 415, "lean +0.310 — opposite sign, same cell type.", cls="mono", fs=9.5, fill="var(--ink2)")
t(660, 428, "24S-OHC is unmeasured in all 5 datasets, so Arm B is", cls="mono", fs=9.5, fill="var(--ink2)")
t(660, 441, "not drawn as a counterweight.", cls="mono", fs=9.5, fill="var(--ink2)")

# ---------------- footer ----------------
box(0, 468, 1000, 30, fill="var(--band)")
t(14, 480, "Not measured:", cls="mono", fs=10, weight=600)
t(104, 480, "desmosterol, lathosterol, 24S-/25-/27-OHC, free cholesterol — 0 of 5 datasets. Every sterol label is inferred from enzyme transcripts.", cls="mono", fs=10, fill="var(--ink2)")
t(14, 493, "Decisive test:", cls="mono", fs=10, weight=600)
t(104, 493, "desmosterol : cholesterol ratio by sterol LC-MS in isogenic APOE4 vs APOE3 oligodendroglia, with an LXR reporter and CE.", cls="mono", fs=10, fill="var(--ink2)")
o.append("</svg>")
open("sterol_nr_panel_v3.svg", "w").write("".join(o))
print(f"wrote sterol_nr_panel_v3.svg  {len(''.join(o))} chars")
