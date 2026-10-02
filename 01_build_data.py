#!/usr/bin/env python
"""Build figdata.json for the APOE endocytosis figure.

Pathway steps = downloaded QuickGO sets (00_fetch_go.py). Pathway-specificity uses the exact
estimand of mito/null_test.py: SE-decile-matched M-score (B=20000, same seed rule), then the
percentile of |M| among the 60 real GO reference pathways already scored in
mito/null_test_pathways.csv. A reference pathway is DROPPED from a step's comparator when more
than 25% of the step's genes are in it (a comparator must not contain the step's own effectors).
"""
import csv, collections, glob, hashlib, json, os
import numpy as np
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(H)
B,NDEC,SEED=20000,10,20260923          # identical to mito/null_test.py

def goset(*names):
    s=set()
    for n in names:
        with open(f"{H}/genesets/{n}.tsv") as f:
            next(f); s|={l.split("\t")[0].strip() for l in f if l.strip()}
    return s
STEPS=[("receptors","Lipoparticle receptors","GO:0030228",goset("lipoprotein_particle_receptor")),
       ("pit","Clathrin pit / internalisation","GO:0072583 + GO:0005905",goset("clathrin_dependent_endocytosis","clathrin_coated_pit")),
       ("early","Early endosome","GO:0005769",goset("early_endosome")),
       ("recycling","Recycling endosome","GO:0055037",goset("recycling_endosome")),
       ("late","Late endosome → lysosome","GO:0005770 + GO:0008333",goset("late_endosome","endosome_to_lysosome")),
       ("lysosome","Lysosome","GO:0005764",goset("lysosome"))]
UMBRELLA=[("endocytosis","Endocytosis (all)","GO:0006897",goset("endocytosis")),
          ("rme","Receptor-mediated endocytosis","GO:0006898",goset("receptor_mediated_endocytosis"))]
# Schematic labels only: every one must be in the downloaded step set it is drawn on.
NODE_GENES={"receptors":["LDLR","LRP1","VLDLR","LRP8","SORL1","SCARB1"],
            "pit":["CLTC","AP2M1","PICALM","DNM1","DNM2"],
            "early":["RAB5A","EEA1","APOE"],"recycling":["RAB11A","SORL1","DNM2"],
            "late":["RAB7A","BIN1","NPC1","NPC2"],"lysosome":["NPC1","NPC2","LIPA"]}
SECRETORY=[("er","Endoplasmic reticulum","GO:0005783",goset("endoplasmic_reticulum")),
           ("golgi","Golgi apparatus","GO:0005794",goset("golgi_apparatus")),
           ("exo","Secretory vesicle / exocytosis","GO:0006887",goset("exocytosis")),
           ("lysexo","Lysosome exocytosis","GO:1990927",goset("lysosome_exocytosis")),
           ("mcs","ER–lysosome contact site","GO:7770088",goset("er_endolysosome_contact")),
           # lysosomal mTORC1 machinery (drawn in the magnified lysosome-surface view)
           ("vatp","v-ATPase","GO:0016471",goset("v_atpase")),
           ("slc","SLC38A9","GO:1904263",goset("pos_reg_torc1")),
           ("ragulator","Ragulator (LAMTOR1–5)","GO:0071986",goset("ragulator")),
           ("rag","Rag GTPases","GO:1990131",goset("rag_gtpase")),
           ("flcn","FLCN–FNIP","GO:1904263",goset("pos_reg_torc1")),
           ("rheb","RHEB","GO:1904263",goset("pos_reg_torc1")),
           ("mtorc1","mTORC1","GO:0031931",goset("torc1_complex")),
           ("tsc","TSC complex","GO:0033596",goset("tsc_complex"))]
NODE_GENES.update({"er":["HSPA5","CANX","SEC61A1"],"golgi":["GOLGA2","GORASP1","COPA"],
                   "exo":["SNAP23","STX4","VAMP3","RAB27A"],"lysexo":["ARL8B","SYT7","SYT11"],"mcs":["STARD3","VAPA","OSBPL1A"],
                   "vatp":["ATP6V1A","ATP6V0D1","ATP6V0A1"],"slc":["SLC38A9"],"ragulator":["LAMTOR1","LAMTOR2","LAMTOR3"],
                   "rag":["RRAGA","RRAGB","RRAGC","RRAGD"],"flcn":["FLCN","FNIP1"],"rheb":["RHEB"],"mtorc1":["MTOR","RPTOR","MLST8"],"tsc":["TSC1","TSC2"]})
EXTRA_GENES=["ABCA1"]   # drawn as a membrane glyph; values shown in its tooltip only
# Genes drawn only because a therapeutic hypothesis names them, with no evidence of their own.
# TET2 is the DNA demethylase shown as a transcriptional output of the chemical-reprogramming
# hypothesis. It carries NONE of this figure's categories: not an AD GWAS consensus locus, not
# in the LC expression universe at all (so it can never take red or blue), and its Mendelian
# evidence is entirely haematological/immunological (immunodeficiency 75 3.285, myelodysplastic
# syndrome 1.382, clonal haematopoiesis 0.559) with no nervous-system disease, so the mendel
# category correctly excludes it. It renders in ink.
HYPOTHESIS_LABELS={"TET2"}
# Glutamate transporters, drawn on the plasma membrane and in the early endosome (requested
# 2026-10-01) and merged into one "EAAT1/2" label. EAAT1 = SLC1A3, EAAT2 = SLC1A2. They are NOT
# in any downloaded GO set here, so they are drawn as their own glyphs rather than added to a
# step's node list; no GO claim is made for them. Both carry two categories: lower in APOE4
# (SLC1A3 -0.523 FDR 5.7e-13, SLC1A2 -0.363 FDR 1.6e-05 -- SLC1A3's is the strongest effect
# anywhere in this figure) and Mendelian CNS disease (SLC1A3 4.117 episodic ataxia type 6,
# SLC1A2 4.394 developmental and epileptic encephalopathy 41).
# Retromer, drawn on the recycling endosome (requested 2026-10-01). VPS35 is the subunit that
# carries the human genetics: VPS35 D620N causes autosomal-dominant Parkinson disease (PARK17),
# Open Targets Mendelian nervous-system score 3.506 on late-onset PD. VPS26A, VPS26B and VPS29
# score 0.000, and none of the four moves in our LC contrast (all FDR > 0.55), so only VPS35
# takes a colour. They are not in any downloaded GO set here, so the complex is drawn as its own
# glyph and no GO membership is claimed.
RETROMER=["VPS35","VPS26A","VPS29"]
EAAT_MERGE="EAAT1/2"
EAAT_MEMBERS=["SLC1A3","SLC1A2"]
# Named exceptions: label-only genes shown on a step whose GO set does not contain them.
# BIN1 (amphiphysin 2, a BAR-domain protein at clathrin-coated pits) is annotated to
# endocytosis GO:0006897 but not to the clathrin-specific terms that define the pit step.
# BIN1 is also drawn on the early and recycling endosome (requested 2026-10-01). Same situation:
# of the downloaded sets it is in endocytosis GO:0006897 and endosome_to_lysosome (which is why
# it already carries the late endosome), but NOT in early_endosome GO:0005769 or
# recycling_endosome GO:0055037, so both are declared exceptions and the figcaption says so.
LABEL_EXCEPTIONS={"pit":{"BIN1":"endocytosis"},"early":{"BIN1":"endocytosis"},"recycling":{"BIN1":"endocytosis"}}
NODE_GENES["pit"]=NODE_GENES["pit"]+["BIN1"]
NODE_GENES["early"]=NODE_GENES["early"]+["BIN1"]
NODE_GENES["recycling"]=NODE_GENES["recycling"]+["BIN1"]
# User-requested label-only additions (drawn as their own receptors, listed under the receptor heading)
USER_LABELS={"receptors":["SORT1","CD36","GPIHBP1"]}
# User-requested removals from the cartoon (2026-09-24). DNM1 is APOE4-DE (pool5 +0.12, FDR 0.031) but was
# removed at the user's request: the fold-change is small and its neurodegeneration link is not relevant here.
# AP2M1, DNM1 and DNM2 were removed here for simplicity; all three carry Mendelian CNS
# disease (DNM2 4.162 CMT dominant intermediate B, DNM1 2.306 Lennox-Gastaut, AP2M1 1.216
# epileptic encephalopathy) and were restored 2026-10-01. EEA1, SYT11 and HSPA5 score 0.000,
# so they stay out.
USER_REMOVE={"EEA1","SYT11","HSPA5"}   # HSPA5: DE but down, so not an ER-stress signature
NODE_GENES["recycling"]=[g for g in NODE_GENES["recycling"] if g!="SORL1"]   # SORL1 is listed under the receptors
SD={k:s for k,_,_,s in STEPS+UMBRELLA+SECRETORY}
for k,gl in NODE_GENES.items():
    miss=[g for g in gl if g not in SD[k] and not (g in LABEL_EXCEPTIONS.get(k,{}) and g in SD[LABEL_EXCEPTIONS[k][g]])]
    assert not miss, f"schematic genes not in GO set {k}: {miss}"

for k,gl in USER_LABELS.items(): NODE_GENES[k]=NODE_GENES[k]+gl
# Dynamin consolidation (requested 2026-10-01). DNM1 and DNM2 are shown ONCE, as a single
# "DNM1/2" label in the clathrin pit where both are annotated, instead of two labels there plus
# a third DNM2 at the recycling endosome. That removes a row from the pit (it had wrapped to
# three) and a name from the recycling run, which was 153 units wide and reached to within 9
# units of the "buds" arrowhead. The merged label's categories are the UNION of the two genes'
# (DNM1 mendel+up, DNM2 mendel -> mendel+up) and its mendel score the maximum, so no evidence is
# lost; the per-gene detail lives in the step's hover box.
# Done after the GO assertion above because "DNM1/2" is a display name, not a gene symbol.
DNM_MERGE="DNM1/2"
NODE_GENES["pit"]=[g for g in NODE_GENES["pit"] if g not in ("DNM1","DNM2")]+[DNM_MERGE]
NODE_GENES["recycling"]=[g for g in NODE_GENES["recycling"] if g!="DNM2"]
# ---- DE sources (same loaders as mito/null_test.py, plus FDR) ----
SRC=[("LC_Visium",f"{R}/shared-spatial/st12_allgeno.tsv","tsv"),
     ("ERC_Visium",f"{R}/erc/S9_SRT_domainDE/SuppTable_09.csv","csv"),
     ("ERC_snBroad",f"{R}/erc/S11_snRNA_broadDE/SuppTable_11.csv","csv"),
     ("ERC_snFine",f"{R}/erc/S13_snRNA_fineDE/SuppTable_13.csv","csv")]
cell=collections.defaultdict(dict)       # (ds,dom) -> gene -> (lf, se, t, fdr)
for ds,path,kind in SRC:
    with open(path) as f:
        if kind=="tsv":
            r=csv.reader(f,delimiter="\t"); next(r)
            for row in r:
                if row[0]!="ALLE4_ALLE2": continue
                try: lf,fdr,t=float(row[3]),float(row[4]),float(row[5])
                except ValueError: continue
                if t==0: continue
                cell[(ds,row[1])][row[2]]=(lf,abs(lf/t),t,fdr)
        else:
            for row in csv.DictReader(f):
                v=[row[k] for k in ("carrier_logFC","carrier_t","carrier_adj.P.Val")]
                if any(x in ("NA","") for x in v): continue
                try: lf,t,fdr=map(float,v)
                except ValueError: continue
                if t==0: continue
                cell[(ds,row["cluster"])][row["gene_name"]]=(lf,abs(lf/t),t,fdr)
# ---- cis window: same rule and coordinate source as cistrans/cistrans.py (ERC table, +/-1 Mb of APOE) ----
pos={}
with open(f"{R}/erc/S9_SRT_domainDE/SuppTable_09.csv") as f:
    for row in csv.DictReader(f):
        g=row["gene_name"]
        if g in pos: continue
        try: pos[g]=(row["seqnames"],(int(row["start"])+int(row["end"]))//2)
        except (ValueError,KeyError): pass
APOE_MID=(44905791+44909393)//2
CIS={g for g,(c,m) in pos.items() if c=="chr19" and abs(m-APOE_MID)<=1_000_000}
assert {"APOE","APOC1","TOMM40"}<=CIS
STEPS=[(k,l,go,s-CIS) for k,l,go,s in STEPS]; UMBRELLA=[(k,l,go,s-CIS) for k,l,go,s in UMBRELLA]
SECRETORY=[(k,l,go,s-CIS) for k,l,go,s in SECRETORY]
CIS_IN_STEPS=sorted(CIS&set().union(*SD.values()))
print("cis genes removed from step scores:",CIS_IN_STEPS)

cells=[c for c in sorted(cell) if len(cell[c])>=4000 and c[1]!="Oligo.3"]   # Oligo.3 = handling artefact

# ---- reference pathways (already scored) ----
REFG={}
for p in sorted(glob.glob(f"{R}/mito/genesets/ref/*.tsv")):
    with open(p) as f:
        next(f); REFG["ref: "+os.path.basename(p)[:-4]]={l.split("\t")[0].strip() for l in f if l.strip()}
REFM=collections.defaultdict(dict)
for r in csv.DictReader(open(f"{R}/mito/null_test_pathways.csv")):
    if r["pathway"].startswith("ref:"): REFM[(r["dataset"],r["domain"])][r["pathway"]]=float(r["mscore"])
excluded={}
for k,_,_,s in STEPS+UMBRELLA+SECRETORY:
    excluded[k]=sorted(p for p,g in REFG.items() if len(s&g)/len(s)>0.25)

def mscore(gd,name,gs):
    genes=np.array(sorted(gd)); lfv=np.array([gd[g][0] for g in genes]); sev=np.array([gd[g][1] for g in genes])
    e=np.quantile(sev,np.linspace(0,1,NDEC+1)); e[-1]+=1e-12
    dec=np.clip(np.searchsorted(e,sev,side="right")-1,0,NDEC-1)
    pools=[np.where(dec==d)[0] for d in range(NDEC)]; gpos={g:i for i,g in enumerate(genes)}
    gl=sorted(g for g in gs if g in gpos)
    if len(gl)<8: return None
    rng=np.random.default_rng([SEED,int(hashlib.sha256(name.encode()).hexdigest()[:8],16)])
    h=collections.Counter(dec[gpos[g]] for g in gl); acc=np.zeros(B)
    for d in sorted(h):
        p=pools[d]
        if len(p): acc+=lfv[p[rng.integers(0,len(p),size=(B,h[d]))]].sum(axis=1)
    nd=acc/len(gl); obs=float(np.mean([gd[g][0] for g in gl])); mu,sd=float(nd.mean()),float(nd.std(ddof=1))
    return dict(n=len(gl),mean=obs,m=(obs-mu)/sd if sd else 0.0)

scores=[]
for c in cells:
    ref=REFM.get(c,{})
    for k,lab,go,s in STEPS+UMBRELLA+SECRETORY:
        r=mscore(cell[c],"endo: "+k,s)
        if r is None: continue
        rv=np.array([abs(v) for p,v in ref.items() if p not in excluded[k]])
        pct=float(100*np.mean(rv<abs(r["m"]))) if len(rv)>=30 else None
        scores.append(dict(ds=c[0],dom=c[1],step=k,n=r["n"],mean=round(r["mean"],4),
                           m=round(r["m"],3),pct=None if pct is None else round(pct,1),nref=int(len(rv))))

# ---- heatmap genes: step genes with FDR<0.05 in >=1 shown column, plus all schematic genes ----
HEATCOLS=[c for c in cells if c[0]!="ERC_snFine"]
named={g for k,gl in NODE_GENES.items() if k in dict((x[0],1) for x in STEPS) for g in gl}
stepgenes=set().union(*[SD[k] for k,_,_,_ in STEPS])
keep=[g for g in sorted(stepgenes) if g in named or any(g in cell[c] and cell[c][g][3]<0.05 for c in HEATCOLS)]
def primary(g): return next(k for k,_,_,_ in STEPS if g in SD[k])
genes=[]
for g in keep:
    vals={f"{c[0]}|{c[1]}":[round(cell[c][g][0],3),round(cell[c][g][2],2),float(f"{cell[c][g][3]:.3g}")]
          for c in HEATCOLS if g in cell[c]}
    genes.append(dict(g=g,step=primary(g),steps=[k for k,_,_,_ in STEPS if g in SD[k]],named=g in named,cis=g in CIS,v=vals))

# ---- receptor forest: LC (all / EA / AA with CI) from tidy_de; ERC from limma t ----
REC=["LDLR","LRP1","VLDLR","LRP8","SORL1","SCARB1"]
forest=[]
with open(f"{R}/reanalysis/results/tidy_de.csv") as f:
    for r in csv.DictReader(f):
        if r["gene"] in REC and r["contrast"] in ("ALLE4_ALLE2","EA","AA"):
            forest.append(dict(g=r["gene"],ds="LC_Visium",dom=r["domain"],stratum={"ALLE4_ALLE2":"all"}.get(r["contrast"],r["contrast"]),
                lf=round(float(r["logFC"]),3),lo=round(float(r["ci_lo"]),3),hi=round(float(r["ci_hi"]),3),fdr=float(f"{float(r['FDR']):.3g}")))
for c in HEATCOLS:
    if c[0]=="LC_Visium": continue
    for g in REC:
        if g in cell[c]:
            lf,se,t,fdr=cell[c][g]
            forest.append(dict(g=g,ds=c[0],dom=c[1],stratum="all",lf=round(lf,3),lo=round(lf-1.96*se,3),hi=round(lf+1.96*se,3),fdr=float(f"{fdr:.3g}")))

sec_named=sorted({g for k,_,_,_ in SECRETORY for g in NODE_GENES[k]}|set(EXTRA_GENES))
extra={g:{f"{c[0]}|{c[1]}":[round(cell[c][g][0],3),round(cell[c][g][2],2),float(f"{cell[c][g][3]:.3g}")] for c in HEATCOLS if g in cell[c]} for g in sec_named}
# ---- gene evidence categories for the cartoon's labels (colour code) ----
# gwas: AD consensus loci (Nature Genetics 2026 consensus meta-analysis), Tier1 or Tier2, matched on locus token
gw={}
for r in csv.DictReader(open(f"{R}/adgenetics/consensus_loci.tsv"),delimiter="\t"):
    for tok in r["locus"].replace(" ","").split("/"): gw.setdefault(tok,r["tier"])
# ot: Open Targets AD (MONDO_0004975) genetic_association scores recorded in curation/synthesis_q13_otgenetics.json
OT_AD={"APOE":0.857,"TREM2":0.858,"SORL1":0.731,"ABCA7":0.649,"ABCA1":0.747,"CLU":0.662,"APOC1":0.611,"APOC2":0.416,"LDLR":0.451}
# de: pooled five-domain LC E4-vs-E2 contrast, the sister sessions' primary estimand (shared-spatial/pool5.json), FDR<0.05
pool5=json.load(open(f"{R}/shared-spatial/pool5.json"))
# neurodegeneration genetics: Open Targets MONDO_0005559 (neurodegenerative disease, indirect), genetic evidence >= 0.1
otnd=json.load(open(f"{H}/ot_neurodegen.json"))["assoc"]
# mendel: Mendelian CNS disease. Open Targets clinical-genetics datasources (Orphanet, ClinGen,
# Genomics England, ClinVar/EVA, UniProt, Gene2Phenotype) summed per disease, restricted to
# nervous-system/psychiatric therapeutic areas, neoplasms dropped. Queried for EVERY labelled
# gene, not a hand-picked shortlist. Threshold 0.5 is set by the two genes that motivated the
# category: NPC1 0.699 and NPC2 0.608.
# AD-DRIVEN QUALIFIERS ARE EXCLUDED: APOE, ABCA7 and SORL1 clear the bar only because their
# Mendelian disease IS Alzheimer's, and the point of this category is the genes carrying severe
# monogenic CNS disease that is NOT obviously APOE4/AD. They keep their gwas/ot colours.
otmd=json.load(open(f"{H}/ot_mendelian_all.json"))
def _mendel(g):
    v=otmd.get(g) or {}
    if (v.get("max") or 0)<0.5: return False
    top=((v.get("top") or [{}])[0].get("disease") or "").lower()
    return not any(k in top for k in ("alzheimer","dementia"))
MENDEL={g for g in otmd if _mendel(g)}
# TSC1/TSC2 carry a literature link to AD that Open Targets does not index at all (it returns no
# Alzheimer/dementia association for either): Adriaanse 2023 Neuropathol Appl Neurobiol 49:e12904,
# "TSC1 contributes to selective neuronal vulnerability in Alzheimer's disease", plus the TSC
# tauopathy series (Liu 2022, Hwang 2023) and plasma p-tau217 in TSC (Baumel 2026 preprint).
# Marked with a dagger-class symbol rather than a colour -- see the note at CAT_ORDER.
ADLIT={"TSC1","TSC2"}
# evidence ramp: a coloured gene is STRONG only on a CONJUNCTION - its pooled direction
# holds in BOTH ancestry strata (derived in ancestry_tier.py, not hard-coded) AND at least
# one independent external source is cited in this figure. "Weak" therefore honestly means
# ONE line of evidence, which is true of a gene we have not curated: our data is its only
# source. That avoids a pale step that silently means "nobody looked".
anc=json.load(open(f"{H}/ancestry_tier.json"))
# external source, with the reason, from this figure's own sources block:
#   APOE/APOC1/APOC2/PLTP/CD36 - mapped LXR response elements, ref [12]
#   LRP1 - one protein-level study, ref [12];  CLU - AD GWAS Tier 1 + Open Targets 0.662
#   DHCR24 - five independent datasets, three platforms, two species (sterol sub-panel)
# NOT included and why: LIPA (ref [12] records NO credible evidence), ACAT2/MVK (SREBP2
# pathway membership is not an independent DE replication), GPIHBP1/DNM1/ATP6V0A1/HSPA5
# (nothing external cited anywhere in the figure).
EXTERNAL={"APOE","APOC1","APOC2","PLTP","CD36","LRP1","DHCR24","CLU"}
KEEP_PATHWAY={"NPC1","NPC2"}|{g for k in ("vatp","slc","ragulator","rag","flcn","rheb","mtorc1","tsc") for g in NODE_GENES[k]}|{"TM6SF1"}
labelled=sorted({g for gl in NODE_GENES.values() for g in gl}|{"ABCA1","ABCA7","CD36","GPIHBP1","TM6SF1","SORT1","DHCR24","MVK","APOC1","APOC2","CLU","PLTP","ACAT2"}|HYPOTHESIS_LABELS|{"DNM1","DNM2"}|set(EAAT_MEMBERS)|set(RETROMER))   # merged-label members stay catalogued
# one-line functional summary per gene product, built by 00_build_func.py from UniProt
# CC FUNCTION (reviewed human entries). Every KEPT label must have one -- asserted below.
FUNC=json.load(open(f"{H}/gene_function.json"))

genecat={}
for g in labelled:
    de=g in pool5 and pool5[g]["fdr"]<0.05
    # APOC1/APOC2 Open Targets evidence is the APOE credible set assigned to neighbours, so it is not credited
    ot=g in OT_AD and g not in {"APOC1","APOC2"}
    # ORDER IS LOAD-BEARING: geneSpans paints a gene with cats[0], so this tuple -- not the
    # template's CAT_ORDER, which turns out to be referenced nowhere else -- decides which colour
    # leads. Reordered 2026-10-01 so the direction measured in THIS dataset outranks borrowed
    # Mendelian disease context.
    cats=[c for c,ok in (("gwas",g in gw),("ot",ot),
                         ("up",de and pool5[g]["lf"]>0),("dn",de and pool5[g]["lf"]<0),
                         ("mendel",g in MENDEL)) if ok]
    a=otnd.get(g,{}); ndgen=max(a.get("genetic_association",0),a.get("genetic_literature",0))
    why=("" if g in USER_REMOVE else "evidence" if cats else "neurodegeneration genetics" if ndgen>=0.1 else "mTORC1 / NPC pathway" if g in KEEP_PATHWAY else "therapeutic hypothesis readout" if g in HYPOTHESIS_LABELS else "")
    av=anc.get(g,{})
    strong=bool(({"up","dn"} & set(cats)) and av.get("concordant") and g in EXTERNAL)
    genecat[g]=dict(cats=cats,keep=bool(why),why=why,func=(FUNC.get(g) or {}).get("f"),uniprot=(FUNC.get(g) or {}).get("acc"),cis=g in CIS,gwas_tier=gw.get(g),ot_ad=OT_AD.get(g),
                    mendel=(otmd.get(g) or {}).get("max") or 0, mendel_dz=((otmd.get(g) or {}).get("top") or [{}])[0].get("disease"),
                    adlit=g in ADLIT,
                    ev=("strong" if strong else "weak"),anc=av or None,
                    de=pool5[g] if g in pool5 else None,nd_genetic=round(ndgen,3))
# the merged dynamin label: union of DNM1 and DNM2 so the colour code loses nothing
_d1,_d2=genecat["DNM1"],genecat["DNM2"]
_un=[c for c in ("gwas","ot","up","dn","mendel") if c in set(_d1["cats"])|set(_d2["cats"])]
genecat[DNM_MERGE]=dict(func=FUNC["DNM1/2"]["f"],uniprot=None,cats=_un,keep=True,why="evidence",cis=_d1["cis"] or _d2["cis"],
    gwas_tier=_d1["gwas_tier"] or _d2["gwas_tier"], ot_ad=_d1["ot_ad"] or _d2["ot_ad"],
    mendel=max(_d1.get("mendel") or 0,_d2.get("mendel") or 0),
    mendel_dz=(_d1 if (_d1.get("mendel") or 0)>=(_d2.get("mendel") or 0) else _d2).get("mendel_dz"),
    adlit=False, ev="weak", anc=None, de=None, nd_genetic=max(_d1["nd_genetic"],_d2["nd_genetic"]),
    members=["DNM1","DNM2"])
print("DNM1/2 merged cats:",_un,"mendel",genecat[DNM_MERGE]["mendel"])
# the merged glutamate-transporter label: union of SLC1A3 and SLC1A2
_e1,_e2=genecat["SLC1A3"],genecat["SLC1A2"]
_eu=[c for c in ("gwas","ot","up","dn","mendel") if c in set(_e1["cats"])|set(_e2["cats"])]
genecat[EAAT_MERGE]=dict(func=FUNC["EAAT1/2"]["f"],uniprot=None,cats=_eu,keep=True,why="evidence",cis=False,gwas_tier=None,ot_ad=None,
    mendel=max(_e1.get("mendel") or 0,_e2.get("mendel") or 0),
    mendel_dz=(_e1 if (_e1.get("mendel") or 0)>=(_e2.get("mendel") or 0) else _e2).get("mendel_dz"),
    adlit=False, ev="weak", anc=None,
    de=(_e1["de"] if (_e1.get("de") or {}).get("fdr",1)<=(_e2.get("de") or {}).get("fdr",1) else _e2["de"]),
    nd_genetic=max(_e1["nd_genetic"],_e2["nd_genetic"]), members=EAAT_MEMBERS)
print("EAAT1/2 merged cats:",_eu,"mendel",genecat[EAAT_MERGE]["mendel"])
nofunc=sorted(g for g,v in genecat.items() if v["keep"] and not v.get("func"))
assert not nofunc, f"kept gene label with no functional summary: {nofunc} -- add it to 00_build_func.py OVERRIDE"
print(f"functional summaries: {sum(1 for v in genecat.values() if v.get('func'))}/{len(genecat)} genecat entries; every kept label covered")
print("removed labels:",sorted(g for g,v in genecat.items() if not v["keep"]))
print("coloured:",{c:sorted(g for g,v in genecat.items() if c in v["cats"]) for c in ("gwas","ot","up","dn")})
out=dict(genecat=genecat,extra=extra,steps=[dict(k=k,label=l,go=go,n=len(s),nodes=NODE_GENES.get(k,[]),excluded_refs=excluded[k],
         group="secretory" if k in dict((x[0],1) for x in SECRETORY) else "endocytic") for k,l,go,s in STEPS+UMBRELLA+SECRETORY],
         cis_removed=CIS_IN_STEPS,cells=[dict(ds=c[0],dom=c[1],heat=c in HEATCOLS) for c in cells],scores=scores,genes=genes,forest=forest)
json.dump(out,open(f"{H}/figdata.json","w"),separators=(",",":"))
print(f"{len(cells)} cells, {len(scores)} step x cell scores, {len(genes)} heatmap genes, {len(forest)} forest rows")
for k,_,_,s in STEPS+UMBRELLA+SECRETORY: print(f"  {k:10s} n={len(s):4d}  excluded refs: {excluded[k]}")
print("\nmedian |M| percentile by step (and by dataset):")
for k,_,_,_ in STEPS+UMBRELLA+SECRETORY:
    ss=[x for x in scores if x["step"]==k and x["pct"] is not None]
    line=f"  {k:10s} all {np.median([x['pct'] for x in ss]):5.1f} (k={len(ss)})"
    for ds in ("LC_Visium","ERC_Visium","ERC_snBroad","ERC_snFine"):
        v=[x["pct"] for x in ss if x["ds"]==ds]; line+=f"  {ds} {np.median(v):5.1f}" if v else ""
    line+=f"  |M|>=2: {sum(abs(x['m'])>=2 for x in ss)}/{len(ss)}  signed median M {np.median([x['m'] for x in ss]):+.2f}"
    print(line)
