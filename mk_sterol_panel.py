#!/usr/bin/env python
"""Build the desmosterol / LXR-RXR sub-panel (A2) for the Endocytosis Atlas panel A.
Static SVG in its own coordinate space, so it cannot collide with the hand-composed cartoon.
Uses the template's own CSS tokens."""
W,H=1000,372
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
o=[]
o.append(f'<svg id="sterolnr" viewBox="0 0 {W} {H}" style="min-width:760px" role="img" aria-label="Predicted metabolite consequences of the raised sterol-synthesis enzymes. DHCR24 consumes desmosterol, an endogenous LXR agonist, so raised DHCR24 predicts less LXR agonism; CYP46A1 up and CYP7B1 down predict more 24-hydroxycholesterol and so more agonism. The two arms oppose. The measured LXR target genes PLTP, ABCA1 and APOE are all lower in APOE4 carriers, which favours the desmosterol arm.">')
def box(x,y,w,h,fill,stroke="--rule",sw=1,rx=4):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="var({stroke})" stroke-width="{sw}"/>')
def t(x,y,s,cls="",fs=13,anchor="start",weight=None,fill=None):
    a=f' class="{cls}"' if cls else ""
    b=f' font-weight="{weight}"' if weight else ""
    f=f' fill="{fill}"' if fill else ""
    o.append(f'<text x="{x}" y="{y}" font-size="{fs}" text-anchor="{anchor}"{a}{b}{f}>{esc(s)}</text>')
def arrow(x1,y1,x2,y2,col="--ink2",sw=1.6,dash=None,head=True):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    m=' marker-end="url(#ah2)"' if head else ""
    o.append(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="var({col})" stroke-width="{sw}" fill="none"{d}{m}/>')
def blunt(x1,y1,x2,y2,col="--c-dn"):
    o.append(f'<path d="M {x1} {y1} L {x2} {y2}" stroke="var({col})" stroke-width="2.2" fill="none"/>')
    o.append(f'<path d="M {x2} {y1-11} L {x2} {y1+11}" stroke="var({col})" stroke-width="3"/>')
o.append('<defs><marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
         '<path d="M 0 1 L 9 5 L 0 9 z" fill="var(--ink2)"/></marker></defs>')
t(0,16,"PREDICTED METABOLITE CONSEQUENCE — the enzymes are measured, the sterols are NOT",cls="mono muted",fs=11.5,weight=600)

# ---------- ARM A : desmosterol ----------
box(0,34,300,104,"var(--surf)")
t(12,54,"Arm A · desmosterol",cls="mono",fs=11.5,weight=600,fill="var(--c-dn)")
o.append('<circle cx="26" cy="80" r="7" fill="var(--chol)"/>')
t(40,84,"desmosterol",fs=13,weight=600)
t(40,101,"an endogenous LXR agonist",cls="ink2",fs=11.5)
t(12,126,"DHCR24  +0.276   FDR 5.7e-07",cls="mono",fs=11.5,fill="var(--c-up)")
arrow(150,78,196,78)
t(206,74,"consumed",cls="ink2",fs=11.5)
t(206,90,"faster",cls="ink2",fs=11.5)
t(318,70,"desmosterol",fs=13,weight=600,fill="var(--c-dn)")
t(318,88,"↓ predicted",cls="mono",fs=12,fill="var(--c-dn)")
t(318,106,"DHCR7 flat (−0.02, FDR 0.89),",cls="ink2",fs=10.5)
t(318,120,"so the Bloch branch specifically",cls="ink2",fs=10.5)
blunt(452,78,536,78)
t(494,62,"LESS agonism",cls="mono",fs=11,anchor="middle",fill="var(--c-dn)",weight=600)

# ---------- LXR/RXR node ----------
box(556,52,150,120,"var(--neutral)","--ink",1.6,6)
t(631,84,"LXR / RXR",fs=16,anchor="middle",weight=600)
t(631,104,"NR1H2/NR1H3",cls="mono ink2",fs=10.5,anchor="middle")
t(631,124,"nuclear receptor",cls="ink2",fs=11,anchor="middle")
t(631,140,"heterodimer",cls="ink2",fs=11,anchor="middle")
t(631,162,"net tone: unresolved",cls="mono",fs=10.5,anchor="middle",fill="var(--muted)")

# ---------- ARM B : 24S-OHC ----------
box(0,190,300,104,"var(--surf)")
t(12,210,"Arm B · 24S-hydroxycholesterol",cls="mono",fs=11.5,weight=600,fill="var(--c-up)")
t(12,238,"CYP46A1  +0.180   FDR 0.037",cls="mono",fs=11.5,fill="var(--c-up)")
t(12,258,"CYP7B1   −0.288   FDR 0.0042",cls="mono",fs=11.5,fill="var(--c-dn)")
t(12,280,"more made, less catabolised",cls="ink2",fs=11)
t(318,226,"24S-OHC",fs=13,weight=600,fill="var(--c-up)")
t(318,244,"↑ predicted",cls="mono",fs=12,fill="var(--c-up)")
t(318,262,"a potent LXR agonist",cls="ink2",fs=10.5)
arrow(452,232,536,180,"--c-up",2.2)
t(500,258,"MORE agonism",cls="mono",fs=11,anchor="middle",fill="var(--c-up)",weight=600)

# ---------- measured output ----------
box(740,52,260,168,"var(--surf)")
t(752,72,"MEASURED LXR targets, LC pool",cls="mono muted",fs=11,weight=600)
arrow(710,112,736,112)
rows=[("PLTP","−0.505","9.7e-05",True),("ABCA1","−0.221","0.13",False),
      ("APOE ‡","−0.181","0.0039",True)]
y=96
for g,lf,fdr,sig in rows:
    t(752,y+14,g,cls="mono",fs=12.5,weight=600 if sig else None)
    t(872,y+14,lf,cls="mono",fs=12.5,anchor="end",fill="var(--c-dn)")
    t(988,y+14,fdr,cls="mono ink2",fs=11,anchor="end")
    y+=26
t(752,186,"ABCG1, ABCG4, MYLIP — not measured",cls="ink2",fs=10.5)
t(752,204,"all measured targets are DOWN",cls="mono",fs=11,weight=600,fill="var(--c-dn)")

# ---------- verdict strip ----------
box(0,304,1000,62,"var(--band)","--rule")
t(14,322,"Reading:",cls="mono",fs=11.5,weight=600)
t(74,322,"the two arms oppose, so transcripts cannot give a net direction — but every measured LXR target is lower in APOE4, which favours Arm A.",cls="ink2",fs=12)
t(14,340,"Decisive test:",cls="mono",fs=11.5,weight=600)
t(102,340,"sterol LC-MS for the desmosterol:cholesterol ratio and 24S-OHC.",cls="ink2",fs=12)
t(102,358,"The two species are predicted to move in OPPOSITE directions, so the ratio discriminates between the arms.",cls="ink2",fs=12)
o.append('</svg>')
svg="".join(o)
open("sterol_nr_panel.svg","w").write(svg)
print(f"wrote sterol_nr_panel.svg ({len(svg):,} bytes)")
