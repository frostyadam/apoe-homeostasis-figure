#!/usr/bin/env python
"""Download endocytic-pathway GO definitions from QuickGO (human, Swiss-Prot, all descendants).
Never hand-curate a panel: each gene's admission rule is 'annotated to this term or a descendant'."""
import os, urllib.request, urllib.parse
TERMS={"endocytosis":"GO:0006897","receptor_mediated_endocytosis":"GO:0006898",
       "clathrin_dependent_endocytosis":"GO:0072583","clathrin_coated_pit":"GO:0005905",
       "early_endosome":"GO:0005769","late_endosome":"GO:0005770",
       "recycling_endosome":"GO:0055037","endosome_to_lysosome":"GO:0008333",
       "lysosome":"GO:0005764","lipoprotein_particle_receptor":"GO:0030228",
       "endoplasmic_reticulum":"GO:0005783","golgi_apparatus":"GO:0005794","exocytosis":"GO:0006887",
       "lysosome_exocytosis":"GO:1990927",
       "er_lysosome_contact":"GO:7770052","er_endolysosome_contact":"GO:7770088",
       "torc1_complex":"GO:0031931","ragulator":"GO:0071986","rag_gtpase":"GO:1990131",
       "pos_reg_torc1":"GO:1904263","v_atpase":"GO:0016471",
       "tsc_complex":"GO:0033596"}
BASE="https://www.ebi.ac.uk/QuickGO/services/annotation/downloadSearch?"
here=os.path.dirname(os.path.abspath(__file__))
import sys
ONLY=set(sys.argv[1:])
for nm,go in TERMS.items():
    if ONLY and nm not in ONLY: continue
    q=urllib.parse.urlencode(dict(goId=go,goUsage="descendants",goUsageRelationships="is_a,part_of,occurs_in",
        taxonId="9606",taxonUsage="exact",geneProductType="protein",geneProductSubset="Swiss-Prot",
        selectedFields="symbol,goId",downloadLimit="500000"))
    req=urllib.request.Request(BASE+q,headers={"Accept":"text/tsv"})
    txt=urllib.request.urlopen(req,timeout=180).read().decode()
    out=os.path.join(here,"genesets",f"{nm}.tsv"); open(out,"w").write(txt)
    genes={l.split("\t")[0] for l in txt.splitlines()[1:] if l.strip()}
    print(f"{nm:34s}{go}  {len(genes):5d} genes")
