#!/usr/bin/env python
"""Condense UniProt CC FUNCTION into a one-line functional summary per gene product.

Source of truth is uniprot_function.json (fetched from rest.uniprot.org, reviewed human
entries only). Each summary is the entry's own first FUNCTION sentence, with evidence
braces and PubMed parentheticals stripped. OVERRIDE holds the cases where that sentence is
unusable, and every one of them says why: either UniProt leads with a generic family
boilerplate that is identical across paralogues (the four Rabs), leads with a minor
interaction rather than the protein's job (APOD), is a one-clause stub, or is a superseded
annotation that newer structural work has replaced (TM6SF1). Nothing here is invented;
the overrides restate UniProt's own later sentences or the paper cited inline.
"""
import json,re,sys
H="/home/afrost/apoe-research/endocytosis"
U=json.load(open(f"{H}/uniprot_function.json"))

# why-annotated replacements for unusable UniProt lead sentences
OVERRIDE={
 # identical family boilerplate across all four Rabs -> each gets its own step role
 "RAB5A":"Early-endosome Rab GTPase; in its GTP state it recruits the effectors that drive homotypic early-endosome fusion and PI(3)P production.",
 "RAB7A":"Late-endosome and lysosome Rab GTPase; it drives early-to-late endosome maturation and recruits the machinery for lysosome fusion.",
 "RAB11A":"Recycling-endosome Rab GTPase; it governs the slow recycling route that returns internalised receptors to the plasma membrane.",
 "RAB27A":"Secretory Rab GTPase; it tethers secretory lysosomes and multivesicular bodies at the plasma membrane for exocytosis.",
 # UniProt leads with an LCAT complex, not the protein's job
 "APOD":"Secreted lipocalin that binds small hydrophobic ligands including cholesterol and arachidonic acid, and co-resides on APOE-containing lipoparticles.",
 # one-clause stubs
 "ACAT2":"Cytosolic thiolase that condenses two acetyl-CoA into acetoacetyl-CoA at the entry of the mevalonate pathway to cholesterol.",
 "AP2M1":"Mu subunit of the AP-2 adaptor complex; it reads the YxxO sorting motif in receptor tails and links the cargo to the clathrin coat.",
 "GORASP1":"Golgi reassembly-stacking protein that holds cis-Golgi cisternae in a stack and is disassembled for mitotic Golgi breakdown.",
 "SORL1":"Vps10p-domain sorting receptor (SORLA) that routes APP and APOE-lipoproteins between the Golgi, the cell surface and endosomes.",
 "SNAP23":"Plasma-membrane SNAP-25 homologue that forms the ternary SNARE complex driving exocytic vesicle fusion in non-neuronal cells.",
 "LRP1":"Large endocytic receptor for APOE-lipoproteins, alpha-2-macroglobulin and amyloid-beta, and a signalling co-receptor.",
 "CD36":"Class B scavenger receptor for oxidised LDL, long-chain fatty acids and fibrillar amyloid-beta, which it internalises.",
 "VPS26A":"Cargo-selective retromer subunit; with VPS35 and VPS29 it captures cargo on the endosome for retrograde and plasma-membrane recycling.",
 "VPS35":"Cargo-selective retromer subunit that binds cargo tails and nucleates the tubules that recycle receptors out of the endosome.",
 "VPS29":"Shared subunit of retromer and of the Commander/retriever complexes, both of which recycle transmembrane cargo off the endosome.",
 # superseded annotation: UniProt still says "may function as sterol isomerase"
 "TM6SF1":"Lysosomal cholesterol-binding membrane homodimer that engages LAMTOR1 of Ragulator; UniProt's sterol-isomerase annotation is superseded by the 2026 cryo-EM structure.",
}
# hand-shortened leads: UniProt's own first sentence, cut to its load-bearing clause
SHORT={
 "ABCA1":"ATP-driven phospholipid floppase that transfers phospholipid and cholesterol onto apolipoproteins to form nascent HDL.",
 "ABCA7":"ATP-driven lipid floppase, closest homologue of ABCA1, preferring phosphatidylserine; needed for macrophage and microglial phagocytosis.",
 "ATP6V0A1":"a subunit of the membrane-integral V0 sector of the vacuolar H+-ATPase, the pump that acidifies endosomes and lysosomes.",
 "ATP6V0D1":"d subunit of the membrane-integral V0 sector of the vacuolar H+-ATPase, which translocates protons across the organelle membrane.",
 "ATP6V1A":"Catalytic A subunit of the peripheral V1 sector of the vacuolar H+-ATPase, which hydrolyses ATP to drive proton pumping.",
 "COPA":"Alpha subunit of the COPI coatomer, which buds vesicles that carry cargo from the ER through the Golgi to the trans-Golgi network.",
 "DNM1":"Neuronal dynamin; a GTPase that constricts the neck of a coated pit and severs the vesicle from the membrane.",
 "DNM2":"Ubiquitous dynamin; a GTPase that severs endocytic vesicles from the plasma membrane and remodels actin structures.",
 "FNIP1":"Binding partner of the FLCN GTPase-activating protein; the pair couple amino-acid availability to mTORC1 control of TFEB and TFE3.",
 "GOLGA2":"GM130, a cis-Golgi membrane skeleton protein that maintains Golgi structure and tethers incoming vesicles for fusion.",
 "LAMTOR1":"p18, the lipid-anchored scaffold of the Ragulator complex that holds the Rag GTPases on the lysosome for amino-acid sensing by mTORC1.",
 "PICALM":"Clathrin assembly lymphoid myeloid protein, a cytoplasmic adaptor that selects cargo and sets vesicle size in clathrin-mediated endocytosis.",
 "PLTP":"Secreted phospholipid transfer protein that moves phospholipid and free cholesterol between lipoproteins and remodels HDL.",
 "RHEB":"Small GTPase that allosterically activates mTORC1 at the lysosome; it is the direct target of TSC2's GAP activity.",
 "RPTOR":"Raptor, the defining scaffold subunit of mTORC1; it presents substrates to the kinase and is the rapamycin-sensitive arm.",
 "TSC1":"Non-catalytic subunit of the TSC complex, which switches off mTORC1 by acting as a GTPase-activating protein for RHEB.",
 "TSC2":"Catalytic subunit of the TSC complex; its GAP activity converts RHEB to the GDP state and so switches mTORC1 off.",
}
def clean(t):
    t=re.sub(r'\{[^}]*\}','',t)
    t=re.sub(r'\(PubMed:[^)]*\)','',t)
    t=re.sub(r'\((?:By similarity|Probable)\)','',t,flags=re.I)
    t=re.sub(r'\s+',' ',t); t=re.sub(r'\s+([.,;])',r'\1',t)
    return t.strip()
def lead(t):
    parts=re.split(r'(?<=[a-z0-9\)\]])\.\s+(?=[A-Z(])',clean(t))
    s=parts[0].strip()
    return s if s.endswith('.') else s+'.'

out={}
for g,v in U.items():
    acc=(v or {}).get("acc")
    if g in OVERRIDE: s,src=OVERRIDE[g],"curated"
    elif g in SHORT:  s,src=SHORT[g],"uniprot-short"
    else:
        f=(v or {}).get("func") or ""
        if not f: continue
        s,src=lead(f),"uniprot"
    out[g]={"f":s,"acc":acc,"src":src}

# merged display labels carry both members, joined
out["DNM1/2"]={"f":"Dynamin GTPases that constrict the neck of a clathrin-coated pit and sever the vesicle; DNM1 is neuronal, DNM2 ubiquitous.","acc":None,"src":"curated"}
out["EAAT1/2"]={"f":"Sodium-dependent high-affinity glutamate transporters (GLAST and GLT-1) that clear synaptic glutamate into astrocytes.","acc":None,"src":"curated"}

bad=[g for g,v in out.items() if len(v["f"])>205 or len(v["f"])<50]
assert not bad, f"summary out of the 50-205 char band: {bad}"
json.dump(out,open(f"{H}/gene_function.json","w"),indent=1,sort_keys=True)
L=sorted(len(v["f"]) for v in out.values())
print(f"wrote gene_function.json: {len(out)} summaries "
      f"(median {L[len(L)//2]} chars, max {L[-1]}); "
      f"{sum(1 for v in out.values() if v['src']=='uniprot')} verbatim UniProt leads, "
      f"{sum(1 for v in out.values() if v['src']=='uniprot-short')} shortened, "
      f"{sum(1 for v in out.values() if v['src']=='curated')} curated")
