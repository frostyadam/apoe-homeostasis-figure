import json, os, subprocess
CORE=os.path.expanduser('~/.claude/plugins/cache/skillful-alhazen/alhazen-core/0.1.0')
S='/home/afrost/.claude/external-skills/alhazen-skill-deep-research/skills/scientific-literature/scientific_literature.py'
INV='scinv-6808f3d27a90'
def run(*a):
    p=subprocess.run(['uv','run','--project',CORE,'--with','requests','python',S,*a],capture_output=True,text=True,
                     env={**os.environ,'TYPEDB_DATABASE':'alh_deep_research'},timeout=300)
    o=p.stdout; return json.loads(o[o.index('{'):])
inv=run('show-investigation','--id',INV)
it=max(p.get('iteration') or 0 for p in inv['phases'] if p.get('phase')=='analysis')+1
C=json.load(open('/home/afrost/apoe-research/endocytosis/kb_claims.json'))
content=f"""## Analysis iteration {it} (2026-09-24): APOE endocytosis, the lysosomal cholesterol-mTORC1 route, and where the investigation stands

**Artifact.** APOE Endocytosis Atlas: https://claude.ai/artifact/KCN5GQaEECrJk8Xap4AdNh. Panel A is a data-free cell cartoon of APOE secretion (ER, Golgi, exocytosis, ABCA1 lipidation) and uptake (HSPG, LDLR/LRP1-family receptors, clathrin pit, early endosome with continuous recycling tubule, late endosome, lysosome). It also shows endo-lysosomal exocytosis (GO:1990927), ER tubules tethered to the lysosome for NPC1-directed cholesterol egress (GO:7770088), and a magnified lysosome surface: v-ATPase, SLC38A9, TM6SF1, Ragulator, Rag GTPases, FLCN-FNIP, RHEB and mTORC1. Panels B-D carry the data. Build: ~/apoe-research/endocytosis/.

**Papers added to the collection this iteration (13):** Hong et al. 2026 PNAS, TM6SF1 (scilit-paper-87c7bcae1cdc); Castellano 2017 (7d4531e7a0ef); Lim 2019 (2debbf7f6b3d); Wilhelm 2017 (802b7097766a); Rocha 2009 (dbfca83a2410); Sancak 2010 (7e6f1978ebd4); Zoncu 2011 (d892dc4defd3); Tsun 2013 (957cbea39c3c); Reddy 2001 (cb8a178e6a5c); Wahrle 2004 (08583491041f); Infante 2008 (4b2f6cbb999e); Pu 2015 (a2dc8a376e7e); and the APOE2 serum signature 2025 (250d968ed0cb), which had a bundle but was not in the collection. The TM6SF1 preprint (10.64898/2026.04.01.715928) was superseded by the PNAS version, so the preprint was not ingested separately. All 13 are abstract-level only: no bundles and no full-text curation.

**New claims:** {', '.join(C)}.

### Current understanding (supersedes nothing; integrates iterations 1-{it-1})
1. **The dominant APOE4-vs-APOE2 signal in LC is immune/microglial and reflects abundance, not state.** It is cis-free and African-ancestry-specific (AA -0.905 vs EA -0.115 on the 8 identity genes). Genotype and ancestry are collinear (epsilon4 about 59% African vs epsilon2 about 33%), so the pooled headline cannot be attributed to genotype alone.
2. **The lipid-pathway claim is withdrawn** once the APOE cis window is excluded. GPIHBP1, CD36, PLTP and DHCR24 survive only as single-gene trans findings.
3. **mTORC1 elevation is retracted** (no 5'-TOP stabilisation), and mTORC1 inhibition, the ISR and TFEB are excluded as drivers of the ribosome/OXPHOS axis.
4. **New this iteration: the endocytic route is not unusual** (steps at the 25th-49th percentile vs real pathways; only lysosome in ERC Visium stands out, at the 85th). **The lysosomal cholesterol-to-mTORC1 apparatus, TM6SF1 included, is transcriptionally flat.** Items 3 and 4 agree. Transcripts are the wrong readout for a recruitment-controlled switch, so the open question is activity, not abundance.
5. **Mechanistic bridge from the literature:** isoform-dependent particle uptake → LIPA → NPC2/NPC1 → three cholesterol sensors (SLC38A9-NPC1, OSBP at ER contacts, TM6SF1-LAMTOR1) → Ragulator-Rag → mTORC1 and TFEB. Together with R136S reversing microglial cholesterol flux, this predicts lower lysosomal cholesterol, lower mTORC1 and more nuclear TFEB for protective isoforms. That is a cell-biology test, not a transcriptomic one.

### Next moves
- Per-donor Xenium cluster proportions (abundance vs state), stratified by ancestry from the start.
- Isoform-matched iPSC microglia/astrocytes: lysosomal cholesterol, pS6K/p4E-BP1, TFEB localisation, TM6SF1-LAMTOR1 co-IP.
- Treat the ERC Visium lysosome signal as a lead only: check it against the ERC snRNA cell types before building on it.
"""
r=run('record-phase','--investigation',INV,'--phase','analysis','--iteration',str(it),'--content',content)
print("iteration",it,"action:",r.get('action'),"success:",r.get('success'))
