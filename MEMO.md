# APOE endocytosis — memo (2026-09-24)

Artifact: https://claude.ai/artifact/KCN5GQaEECrJk8Xap4AdNh ("APOE Endocytosis Atlas")
Build: `00_fetch_go.py` (QuickGO) → `01_build_data.py` (figdata.json) → `02_build_page.py` (HTML)

## Verdict
No endocytic step is changed more than a typical real pathway in E4 vs E2 carriers.
Estimand = mito/null_test.py M-score (SE-decile matched, B=20000), percentile of |M| among
60 real GO pathways per cell; refs holding >25% of a step's genes removed from its comparator;
cis window (±1 Mb APOE: APOE, APOC2) removed from step sets; ERC Oligo.3 excluded. 50 cells.

| step (GO) | median pct, all cells | LC Visium | ERC Visium | ERC snRNA | ERC sn fine |
|---|---|---|---|---|---|
| receptors (GO:0030228) | 28.6 | 32.7 | 46.9 | 12.2 | 24.5 |
| clathrin pit (GO:0072583+0005905) | 32.7 | 40.0 | 20.0 | 23.6 | 34.5 |
| early endosome (GO:0005769) | 31.2 | 15.8 | 43.0 | 36.8 | 32.5 |
| recycling endosome (GO:0055037) | 28.5 | 36.2 | 47.4 | 27.6 | 25.9 |
| late endosome→lysosome (GO:0005770+0008333) | 36.6 | 16.1 | 59.0 | 37.5 | 33.9 |
| lysosome (GO:0005764) | 41.4 | 17.2 | **85.3** | 39.7 | 38.8 |
| endocytosis umbrella (GO:0006897) | 49.1 | 16.1 | 34.8 | 58.9 | 50.0 |
| receptor-mediated (GO:0006898) | 25.5 | 22.8 | 41.2 | 31.6 | 20.2 |

Only local exception: lysosome in ERC Visium (85th). Receptors individually flat in LC
(LDLR FDR ≥0.48, LRP1 ≥0.07, SORL1 ≥0.60); values cross-checked against lipid_panel.json.

## Caveats
No E3/E3 arm; genotype collinear with ancestry (ε4 ~59% African vs ε2 ~33%); ERC carrier
contrast underpowered (0.1–0.3% FDR<0.05). "E4 endosomal trapping" callout dropped — nothing
in the curated corpus supports it.

## v2 (2026-09-24): secretory arm added to the cartoon
Same estimand, fresh QuickGO sets. Median |M| percentile, all cells:
ER (GO:0005783) 56.8 (ERC Visium 89.8) · Golgi (GO:0005794) 63.8 · exocytosis (GO:0006887) 67.6.
Somewhat above the uptake steps but inside the real-pathway range. APOE (cis) excluded from ER/Golgi.

## v6 + knowledge base (2026-09-24)
Cartoon: continuous ER/recycling lumens, bilayers everywhere, ER–lysosome contacts (GO:7770088),
lysosomal exocytosis (GO:1990927), magnified lysosome surface with mTORC1 machinery and TM6SF1
(Hong…Hobbs, Li, PNAS 2026, 10.1073/pnas.2622424123).
Alhazen scinv-6808f3d27a90: +13 papers (96→109; ids in kb_ingest_result.json), claims
scsynth-13906c8273e2 (endocytosis typical), scsynth-f16d9935cb3c (cholesterol–mTORC1 apparatus incl.
TM6SF1 flat: 0/24 genes FDR<0.05 in LC), scsynth-5c9ec2c17304 (literature bridge, conf 0.6),
analysis phase iteration 14 (current-understanding synthesis).
