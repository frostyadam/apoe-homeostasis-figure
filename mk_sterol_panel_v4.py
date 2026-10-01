#!/usr/bin/env python
"""Sterol / LXR sub-panel v4 for the APOE Homeostasis figure.

v3 promoted Arm A (DHCR24 replicated) and withdrew Arm B (CYP46A1 contradicted).
v4 adds what the TCW et al. 2022 main figures supply, now obtained:
  - the ER sterol-depletion paradox is MEASURED, not inferred (GC-MS free cholesterol)
  - the hypothesis has been tested pharmacologically: LXR agonists rescue APOE4 efflux
  - the disposal route differs by cell type (astrocytes store FC; oligodendroglia esterify)
  - the decisive Arm A test may already exist unreported in TCW's GC-MS runs
"""
W, H = 1000, 596
o = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, cls="", fs=12, anchor="start", weight=None, fill=None):
    a = f' class="{cls}"' if cls else ""
    b = f' font-weight="{weight}"' if weight else ""
    f = f' fill="{fill}"' if fill else ""
    o.append(f'<text x="{x}" y="{y}" font-size="{fs}" text-anchor="{anchor}"{a}{b}{f}>{esc(s)}</text>')


def box(x, y, w, h, fill="var(--surf)", stroke="--rule", sw=1, rx=4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
             f'stroke="var({stroke})" stroke-width="{sw}"{d}/>')


def arrow(x1, y1, x2, y2, col="--ink2", sw=1.8):
    o.append(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="var({col})" stroke-width="{sw}" '
             f'fill="none" marker-end="url(#ah4)"/>')


def blunt(x1, y1, x2, y2, col="--c-dn", sw=2.2):
    o.append(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="var({col})" stroke-width="{sw}" fill="none"/>')
    o.append(f'<path d="M {x2} {y1-10} L {x2} {y1+10}" stroke="var({col})" stroke-width="3"/>')


def tick(x, y, col="--c-up"):
    o.append(f'<path d="M {x} {y} l 3.5 4 l 6 -9" stroke="var({col})" stroke-width="2.4" fill="none" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')


def cross(x, y, col="--ink2"):
    o.append(f'<path d="M {x} {y-4} l 8 8 M {x+8} {y-4} l -8 8" stroke="var({col})" stroke-width="2.2" '
             f'fill="none" stroke-linecap="round"/>')


AL = ("Sterol and LXR evidence. Band 1: DHCR24 is higher in APOE4 in five independent datasets. Band 2: the "
      "consequence is now measured rather than inferred — isogenic APOE4 astrocytes hold 20 percent more total "
      "cholesterol, entirely as free cholesterol with cholesteryl ester unchanged, and three times more lysosomal "
      "cholesterol, so the endoplasmic reticulum reads sterol-depleted while the lysosome is loaded, which predicts "
      "weaker LXR agonism. Band 3: the hypothesis tested pharmacologically — LXR agonists restore APOE4 cholesterol "
      "efflux to APOE3 levels whereas 25-hydroxycholesterol does not. Band 4: the disposal route differs by cell "
      "type, astrocytes storing free cholesterol and oligodendroglia esterifying it. Band 5: the opposing "
      "24S-hydroxycholesterol arm is withdrawn because CYP46A1 is down in human oligodendroglia.")
o.append(f'<svg id="sterolnr" viewBox="0 0 {W} {H}" style="min-width:760px" role="img" aria-label="{esc(AL)}">')
o.append('<defs><marker id="ah4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
         'orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9 z" fill="var(--ink2)"/></marker></defs>')

# ---------------- BAND 1 : the replicated observation ----------------
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
for i, (lab, lf, sig, ctl, solid) in enumerate(ROWS):
    y = 60 + i * 19
    t(12, y + 4, lab, cls="mono", fs=10.5, fill=None if solid else "var(--ink2)")
    o.append(f'<rect x="300" y="{y-5}" width="{max(2.0, lf*210):.1f}" height="10" rx="1.5" fill="var(--c-up)"/>')
    if not solid:
        o.append(f'<rect x="300" y="{y-5}" width="{max(2.0, lf*210):.1f}" height="10" rx="1.5" '
                 f'fill="var(--surf)" opacity="0.45"/>')
    t(470, y + 4, f"+{lf:.3f}", cls="mono", fs=10.5, anchor="end", weight=500, fill="var(--c-up)")
    t(486, y + 4, sig, cls="mono", fs=10, fill="var(--ink2)")
    t(660, y + 4, ctl, cls="mono", fs=10, fill="var(--ink2)")
t(12, 164, "DHCR24 = 24-dehydrocholesterol reductase: converts desmosterol → cholesterol. Also seladin-1, "
           "reduced in vulnerable neurons in AD.", cls="mono muted", fs=9.5)

# ---------------- BAND 2 : now measured, not inferred ----------------
t(0, 194, "NOW MEASURED, NOT INFERRED — APOE4 glia hoard FREE cholesterol in lysosomes while the ER reads "
          "\"depleted\"", cls="mono muted", fs=11, weight=600)
box(0, 204, 1000, 124)
# left: the GC-MS numbers
box(10, 214, 274, 104, fill="var(--band)")
t(22, 232, "isogenic APOE4 vs APOE3 astrocytes", cls="mono", fs=10, weight=600)
t(22, 245, "GC-MS · n = 6, 4 experiments", cls="mono muted", fs=9)
t(22, 266, "total cholesterol", cls="mono", fs=10.5)
t(274, 266, "+20%", cls="mono", fs=11, anchor="end", weight=600, fill="var(--c-up)")
t(22, 283, "…entirely FREE cholesterol", cls="mono", fs=10, fill="var(--ink2)")
t(22, 300, "cholesteryl ester", cls="mono", fs=10.5)
t(274, 300, "unchanged", cls="mono", fs=10.5, anchor="end", fill="var(--ink2)")
t(22, 313, "lysosomal cholesterol 3× (p<0.001, filipin)", cls="mono", fs=9.5, weight=600, fill="var(--c-up)")
# middle: the chain
o.append('<circle cx="318" cy="252" r="8" fill="var(--chol)"/>')
t(318, 274, "desmosterol", cls="mono", fs=9.5, anchor="middle", weight=600)
arrow(334, 252, 372, 252)
t(353, 245, "DHCR24 ↑", cls="mono", fs=9, anchor="middle", fill="var(--c-up)")
o.append('<circle cx="396" cy="252" r="8" fill="none" stroke="var(--c-dn)" stroke-width="1.6" stroke-dasharray="2.5 2.5"/>')
o.append('<circle cx="396" cy="252" r="3" fill="var(--chol)" opacity="0.3"/>')
t(396, 274, "↓ predicted", cls="mono", fs=9.5, anchor="middle", weight=600, fill="var(--c-dn)")
blunt(414, 252, 452, 252)
t(433, 243, "LESS", cls="mono", fs=9, anchor="middle", weight=600, fill="var(--c-dn)")
box(462, 224, 132, 60, fill="var(--neutral)", stroke="--ink", sw=1.6, rx=6)
t(528, 248, "LXR / RXR", fs=14, anchor="middle", weight=600)
t(528, 266, "hypo-agonised", cls="mono", fs=9.5, anchor="middle", weight=600, fill="var(--c-dn)")
t(528, 300, "efflux ↓ · our PLTP −0.505", cls="mono", fs=9.5, anchor="middle", fill="var(--ink2)")
t(528, 313, "ABCA1, ABCA7, APOE protein ↓ (TCW)", cls="mono", fs=9, anchor="middle", fill="var(--ink2)")
# right: the authors' own reading
box(606, 214, 384, 104, fill="var(--band)")
t(618, 232, "the authors' own mechanism", cls="mono muted", fs=9.5, weight=600)
for i, line in enumerate(["\"lysosomal sequestration of free cholesterol away",
                          "from ER that misinforms APOE4 cells to respond",
                          "as if intracellular cholesterol levels are low,",
                          "leading to upregulated de novo synthesis\""]):
    t(618, 252 + i * 15, line, fs=10.5, fill="var(--ink)")
t(618, 313, "TCW et al. 2022 · independently reached from the sterol side", cls="mono muted", fs=9)

# ---------------- BAND 3 : tested pharmacologically ----------------
t(0, 350, "THE HYPOTHESIS TESTED PHARMACOLOGICALLY", cls="mono muted", fs=11, weight=600)
box(0, 360, 490, 112)
tick(14, 382)
t(34, 386, "LXR agonists GW3965 · T0901317", cls="mono", fs=10.5, weight=600)
t(34, 400, "restore APOE4 efflux to untreated APOE3 level", cls="mono", fs=10, fill="var(--c-up)")
cross(14, 416)
t(34, 420, "25-hydroxycholesterol", cls="mono", fs=10.5, weight=600)
t(34, 434, "no rescue of efflux (it suppresses SREBF2 instead)", cls="mono", fs=10, fill="var(--ink2)")
t(14, 450, "Incomplete: the APOE4-vs-APOE3 baseline gap persists under treatment; in microglia the", cls="mono muted", fs=9)
t(14, 462, "agonists raise APOE in APOE3 but NOT in APOE4 — the response is cell-type specific.", cls="mono muted", fs=9)

# ---------------- BAND 4 : disposal route by cell type ----------------
t(510, 350, "THE DISPOSAL ROUTE DIFFERS BY CELL TYPE", cls="mono muted", fs=11, weight=600)
box(510, 360, 490, 112, fill="var(--band)")
t(522, 380, "astrocytes", cls="mono", fs=11, weight=600)
t(988, 380, "store it FREE · CE unchanged", cls="mono", fs=10.5, anchor="end", fill="var(--c-up)")
t(522, 402, "oligodendroglia", cls="mono", fs=11, weight=600)
t(988, 402, "esterify it · 35/35 CE ↑ ≈9×", cls="mono", fs=10.5, anchor="end", fill="var(--c-up)")
t(522, 424, "both compartments", cls="mono", fs=11, weight=600)
t(988, 424, "BMP ↑ in 3 cohorts", cls="mono", fs=10.5, anchor="end", fill="var(--c-up)")
t(522, 446, "LIPA (lysosomal CE hydrolase)", cls="mono", fs=10.5)
t(988, 446, "−0.249 pooled · AA −0.61 / EA +0.16", cls="mono", fs=10.5, anchor="end", weight=600, fill="var(--c-dn)")
t(522, 462, "so cholesteryl ester is NOT a universal APOE4 readout", cls="mono muted", fs=9)

# ---------------- BAND 5 : withdrawn arm ----------------
t(0, 496, "WITHDRAWN IN REVISION — the opposing 24S-OHC arm", cls="mono muted", fs=11, weight=600)
box(0, 506, 1000, 46, dash="4 3")
t(12, 525, "CYP46A1", cls="mono", fs=11, weight=600)
t(96, 525, "our LC pool +0.180 (FDR 0.037)  ·  isogenic iPSC oligodendroglia −0.707 (q 1.7e-04, OPPOSITE)  ·  "
           "post-mortem null (p 0.44)", cls="mono", fs=10, fill="var(--ink2)")
t(12, 542, "Cell-type rescue FAILS — our ERC oligodendrocytes lean +0.310, opposite sign in the same cell type. "
           "24S-OHC is unmeasured in all 5 datasets.", cls="mono muted", fs=9.5)

# ---------------- footer ----------------
box(0, 560, 1000, 32, fill="var(--band)")
t(14, 574, "Still unmeasured:", cls="mono", fs=10, weight=600)
t(126, 574, "desmosterol, lathosterol, 24S-/25-/27-OHC — 0 of 5 APOE datasets. The sterol labels above remain "
            "inferred from enzyme transcripts.", cls="mono", fs=10, fill="var(--ink2)")
t(14, 587, "Decisive test, possibly already run:", cls="mono", fs=10, weight=600)
t(238, 587, "TCW's GC-MS protocol (Müller 2019) resolves 23 distal sterol intermediates, desmosterol among them — "
            "only FC/TC/CE were reported.", cls="mono", fs=10, fill="var(--ink2)")
o.append("</svg>")
open("sterol_nr_panel_v4.svg", "w").write("".join(o))
print(f"wrote sterol_nr_panel_v4.svg  {len(''.join(o))} chars")
