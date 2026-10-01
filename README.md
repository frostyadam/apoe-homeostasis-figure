# APOE Homeostasis Figure

A publication-quality, interactive figure of APOE-dependent lipoparticle handling in the
brain — synthesis and secretion, HSPG capture, receptor-mediated endocytosis, the
endosome-to-lysosome route, and sterol processing in the ER — with the APOE4-vs-APOE2
transcriptomic evidence mapped onto each step, plus three therapeutic hypotheses.

Two pages are published as private Claude Artifacts:

| Page | File | Artifact |
|---|---|---|
| Static atlas | `apoe_endocytosis_atlas.html` | https://claude.ai/artifact/KCN5GQaEECrJk8Xap4AdNh |
| Guided 9-stop tour (animated) | `apoe_tour.html` | https://claude.ai/artifact/WZRhc1Hqtd8cE92wYPWPQc |

Both are self-contained single files — the data is embedded, so they open from `file://`
with no server and no network.

## Build pipeline

```
00_fetch_go.py        QuickGO -> genesets/*.tsv        (network; re-run only to refresh GO)
ancestry_tier.py      ST12 within-ancestry sheets -> ancestry_tier.json
01_build_data.py      DE tables + genesets -> figdata.json
02_build_page.py      page_template.html + figdata.json -> apoe_endocytosis_atlas.html
03_build_tour.py      -> apoe_tour.html  (9 stops, camera path in tour_stops.json)
04_render_tour_mp4.py -> apoe_tour.mp4   (STALE: see Known issues)
```

`page_template.html` is the real source of the figure. The two HTML outputs are generated and
committed so the repo always carries a viewable, shareable copy.

Normal edit loop — change the template, then:

```bash
python 02_build_page.py && python 03_build_tour.py
```

Interpreter used for this project: `~/.claude/venvs/apoe-spatial/bin/python`.

## What this repo does and does not contain

**Committed:** the drawing source, the build scripts, the GO gene-set TSVs, the derived
`figdata.json` and `ancestry_tier.json`, and the two generated HTML pages. That is enough to
**rebuild the figure** and to view it.

**Not committed — upstream data lives one directory up**, in the parent `apoe-research/`
project: `reanalysis/results/tidy_de.csv`, `shared-spatial/st12_allgeno.tsv`,
`shared-spatial/errcorr.json`, `shared-spatial/pool5.json`, `erc/S9|S11|S13/*`,
`mito/null_test_pathways.csv`, `adgenetics/consensus_loci.tsv`, `curation/*.json`.

So: `02_build_page.py` and `03_build_tour.py` work from a fresh clone; `01_build_data.py` and
`ancestry_tier.py` do **not** — they need the parent project. Clone this inside
`apoe-research/` if you intend to re-derive the data.

## How to read the colour code

- **plum** — AD GWAS locus
- **teal** — Open Targets AD association
- **red / blue** — higher / lower in APOE4 than APOE2 carriers, pooled LC contrast, FDR < 0.05
- **grey** — on the pathway, no evidence category
- a trailing `●` means the gene carries a further category; `‡` marks a gene inside the
  ±1 Mb APOE cis window; `†` marks significant between-stratum heterogeneity

Every claim in the figure is in a tooltip with its citation. `MEMO.md` holds the panel-C
pathway percentiles and the headline numbers.

## Caveats carried by the figure itself

No APOE3/APOE3 arm — every contrast is APOE4 versus APOE2 carriers, and genotype is
confounded with ancestry. Of the fifteen directional genes, only APOC1 and CD36 hold in both
ancestry strata; **APOE's own effect is European-ancestry-specific** (between-stratum
p = 1.4e-07), so a pooled statement here is largely a statement about the EA donors
(`ancestry_tier.json` has the per-gene detail). Microglial signal in this dataset is density,
not state.

## Known issues

- `04_render_tour_mp4.py` still renders the retired overlay-caption layout, not the current
  side-panel design. The MP4 is gitignored and the last export (2026-09-26) is out of date.
- The figcaption still narrates the mTORC1 cascade in prose after that label was removed.
- An evidence-weight colour gradient was attempted and reverted on 2026-09-30: `catCol` feeds
  shape `fill`, not only label text, so changing the no-category fallback from grey to ink
  turned every uncategorised gene glyph near-black. A retry must leave the fallback grey and
  restyle only genes that already have a category.

## Published versions

| | version | what it is |
|---|---|---|
| Atlas | **v93** | `apoe_endocytosis_atlas.html` |
| Tour | **v60** | `apoe_tour.html`, 9 stops |

Republishing the same file path keeps the URL, so the artifact version number is the figure's
real version history; git records the source that produced each one.

### Changelog

**v80 / v47 — 2026-10-01**

- Moved the "Recycling endosome" label to 3 o'clock of its own structure. Anchored `end` at
  (612,270) it extended leftward and landed at x545-612 / y254-292, directly above the
  "Lysosome exocytosis" label at x541-615 — two stacked labels, neither beside the thing it
  named. Now anchored `start` at (680,215): 16.5 units clear of the endosome's outer edge,
  block centre 3.7 units above the circle centre.

**v93 / v60 — 2026-10-01**

- The three v-ATPase subunit genes are removed from under the `ER–lysosome contact site` label.
  The evidence moves onto the **pump glyph itself**: filled with the colour of ATP6V0A1, its
  strongest-evidence subunit — up in APOE4, so red leads — with a sienna dot for its Mendelian
  CNS disease (epileptic encephalopathy 104, 3.141). ATP6V1A contributes mendel only (2.969)
  and ATP6V0D1 carries nothing, so neither needed its own label.
- Retromer: the coat glyph is removed from inside the tubule, and the `retromer / VPS35` text
  moves to anchor-end (866, 290/302), spanning x811-868 over the tubule **body** rather than
  its tip at (780,321). Best free slot in a sweep of x800-960 / y290-345, at 13.5 units.

**v92 / v59 — 2026-10-01**

- Retromer moved from the recycling endosome **onto the recycling tubule** emanating from the
  early endosome, which is where it acts — retromer with its SNX-BAR partners tubulates the
  endosome and that tubule *is* the retrieval carrier. Coat beads measure 1.7–2.7 units from
  the tubule centreline, inside its 5.5 half-width.
- Its tooltip now carries a 40-gene comparative sweep, `ot_recycling_genetics.json`. **Nine
  genes outscore VPS35** (3.506): SNX14 4.879 (SCAR20), RAB39B 4.347, WASHC5 4.133 (SPG8),
  VPS13A 4.061, LRRK2 4.001, VPS13D 3.957, RAB7A 3.818, RAB11B 3.707, CCDC22 3.646. And the
  retromer **core** is genetically silent: VPS26A, VPS26B, VPS29 and the SNX-BARs all 0.000.

**v91 / v58 — 2026-10-01**

- `buds` arrow now **points at** the recycling endosome. Its end tangent was ~40° off the line
  to the centre, so it read as sweeping past; the control point is moved onto the ray from the
  centre through the end point, giving a tangent error of **2.3°**. The `buds` label moved clear
  of the new curve (gap 8.7, was colliding). End gap to the membrane still 12.5.
- **Retromer** added on the cytosolic face of the recycling endosome, as three subunit beads in
  an arc, coloured by **VPS35** — D620N causes autosomal-dominant Parkinson disease (PARK17),
  Mendelian nervous-system score 3.506. VPS26A, VPS26B and VPS29 score 0.000 and take no
  colour; none of the four moves in our data (all FDR > 0.55), so the sienna is external
  genetics only. Sienna is the right bin precisely because it is neurodegenerative genetics
  broadly rather than PD-specific — it already holds ataxia, epilepsy and CMT genes.
- Lipoparticle receptors on **two rows** by request, via a `FORCE` layout that overrides the
  width packer: `LDLR · VLDLR · SCARB1 · CD36` then `LRP1 · SORT1 · SORL1 · GPIHBP1`.

**v90 / v57 — 2026-10-01**

- Endosomal EAAT barrel scaled to **0.64 = 9/14**, the endosome membrane stroke over the
  plasma-membrane stroke, so it traverses the thinner bilayer by the same proportion
  (12.8 tall on a 9-unit band; ratio 1.42 against 1.43 at the cell surface).
- **Recycling endosome dilated r19 → r25** to clear the green/purple clash. At r19 the lumen was
  only 29 units across, so the teal recY (x633.5-646.5, y221-240) and the plum sortilin head
  (x640.7-646, y206.3-226) overlapped over x640.7-646 / y221-226. The two glyphs also moved to
  opposed bearings (120° and −30°). Teal-to-plum gap is now **9.6** units.
- Both arrows targeting that endosome were re-trimmed for the larger outer edge (29.5), so the
  `buds` end and the `receptor returns` start are back to exactly **12.5**.

**v89 / v56 — 2026-10-01**

- EAAT1/2 moved from x300 to the **far right of the plasma membrane at x1030**, directly under
  the `Uptake` title (y74-108, x1002-1088), with the label at y151-167 in the cytoplasm below.
- The barrel now **fully traverses** the bilayer. `eaatGlyph()` is 14 wide × 20 tall rather than
  18 × 18, so against the 14-unit membrane stroke centred on y130 it spans y120-140 — the band
  is y123-137, giving 3 units of overhang on each face. Verified by measurement.

**v88 / v55 — 2026-10-01**

- **Category precedence reordered**: direction colours now outrank `mendel`, so a gene carrying
  both leads with what this dataset measured. The order lives in `01_build_data.py` (geneSpans
  paints `cats[0]`); the template's `CAT_ORDER` turned out to be referenced nowhere else.
  ACAT2, MVK, ATP6V0A1 and DNM1/2 flip from sienna+red to red+sienna.
- **EAAT1/2 (SLC1A3/SLC1A2)** added to the plasma membrane and the early endosome as a
  transporter barrel, merged into one label like DNM1/2. Blue with a sienna dot: SLC1A3 −0.523
  FDR 5.7e-13 (the strongest effect in the figure) and SLC1A2 −0.363 FDR 1.6e-05, plus
  Mendelian CNS disease (episodic ataxia type 6; epileptic encephalopathy 41). Neither is in
  any downloaded GO set, so they are drawn as their own glyphs and no GO claim is made.
- **Sortilin glyph** factored into `sortGlyph()` and added to the early and recycling endosome,
  on the basis of the two papers below.
- Corpus: Asaro 2021 (J Cell Sci 134:jcs258894) and Greda 2025 (Nat Metab 7:2346), both with
  full text — PMC XML plus the user-supplied PDFs extracted with poppler (102k and 407k chars).

**v87 / v54 — 2026-10-01**

- Removed the italic `exocytosis` arrow label above the cell-type ranking; the arrow alone
  carries the step and the secretory-vesicle label beside it already says exocytosis.
- Ranking trimmed to **four** rows — hepatocytes (1), Müller glia (2), macrophages (6),
  astrocytes (9) — with the **full top twenty** now in the hover box, generated from
  `apoe_celltype_ncpm.tsv` at build time rather than typed by hand.
- **Caught a blank-figure bug before publishing.** The tooltip edit left a stray `)`, so the
  whole script failed to parse and `#schem` rendered with *zero* elements. The build steps all
  exited 0 and the tour still reported "9 stops"; the only visible signal was the tour dropping
  117 → 96 KB. Builds are now syntax-checked with `node --check` on the extracted script.

**v86 / v53 — 2026-10-01**

- **DNM1 and DNM2 consolidated** into a single `DNM1/2` label in the clathrin pit, with the
  union of their categories (mendel + up) and the max Mendelian score, so no evidence is lost.
  The hover box spells out the members. The third dynamin label at the recycling endosome is
  dropped, so the family is named once.
- **Recycling endosome decluttered**: its run went from `RAB11A · DNM2 · BIN1` (153 units) to
  `RAB11A · BIN1` (102), and the `buds` arrow was re-aimed to approach the endosome lower-left
  at (652,256). Gap from the arrowhead to the RAB11A run: **9.0 -> 16.2**, with the 12.5-unit
  membrane clearance preserved (12.6).
- **APOE by cell type** added under the CYTOPLASM label: six rows with ranks, from HPA
  single-cell consensus nCPM across 154 cell types (`apoe_celltype_ncpm.tsv` committed).
  Hepatocytes 9962 (1st), Müller glia 6740 (2nd), macrophages 1733 (6th), astrocytes 1020
  (9th), Kupffer cells 859 (14th), pericytes 721 (18th). Ranks are printed so the omitted
  entries are visible rather than hidden.

**v85 / v52 — 2026-10-01**

- Chemical reprogramming now names two transcriptional outputs below the response element:
  **ABCA1** (plum + teal and sienna dots — AD GWAS locus, Open Targets AD, Mendelian CNS) and
  **TET2** (ink). Placed at root y694/709, the only free band in the nucleus by a clearance
  sweep (27.3 units clear).
- TET2 carries **no** evidence category and that is deliberate: not an AD GWAS locus, absent
  from the LC expression universe so it can never take red or blue, and its Mendelian evidence
  is wholly haematological/immunological (immunodeficiency 75, MDS, clonal haematopoiesis), so
  the neoplasm/nervous-system filter excludes it. It is catalogued with
  `why="therapeutic hypothesis readout"` via a new `HYPOTHESIS_LABELS` set, and the tooltip and
  figcaption both state that its ink colour means a named prediction, not a result.

**v84 / v51 — 2026-10-01**

- TSC1/TSC2 labels raised to sit just under the complex glyph: gap to the circles 20 -> 4.1
  units, clearance +3.6 and +15.2. The band *above* the circles is only ~26 root units, which
  fits one line but not two, so below-and-close is as near as a two-line label can get.
- **BIN1** added to the early and recycling endosome, via the build's existing
  `LABEL_EXCEPTIONS` mechanism. BIN1 is in endocytosis GO:0006897 and endosome-to-lysosome
  but **not** in early endosome GO:0005769 or recycling endosome GO:0055037, and
  `01_build_data.py` asserts every schematic gene is in its step's GO set — so the placement
  has to be declared, exactly as BIN1 at the clathrin pit already was. The figcaption now
  states the exception. BIN1 renders at four compartments.

**v83 / v50 — 2026-10-01**

- The **tour** legend was missing the sienna row (the atlas legend had it since v81). Added, plus
  the two marks it never listed: `†` ancestry heterogeneity and `§` AD-literature link.
- Fixed a real TSC1/TSC2 collision in the mTORC1 inset. Anchored `end` at local x1085 the label
  ran leftward across its own glyph (the two `--tsc` circles at 1052/1069,660) and across the
  inhibitory bars at x1003-1041. As one 78-unit string a clearance sweep of that corner found
  only two positions where it fits at all, both at 2.3 units. Split onto two lines (~40 units)
  and placed below the complex, it clears everything by 19.3 and 21.4. Above was blocked by the
  inset's own top boundary.

**v82 / v49 — 2026-10-01**

- Restored **AP2M1, DNM1, DNM2**, removed earlier for simplicity. All three carry Mendelian
  CNS disease: DNM2 4.162 (CMT dominant intermediate B, the 4th strongest in the figure),
  DNM1 2.306 (Lennox-Gastaut), AP2M1 1.216 (epileptic encephalopathy). EEA1, SYT11 and HSPA5
  stay removed — they score 0.000.
- Gave the mTORC1 inset real gene symbols so three genes that qualified but were invisible can
  carry the code: `ATP6V1A · ATP6V0D1 · ATP6V0A1` under the v-ATPase glyph, and `MTOR` above
  the pill. MTOR goes outside the pill because the pill's subunit line is white-on-fill, where
  a category colour would be illegible. Sienna labels: 9 -> 16.
- New `geneRun()` helper: a run of symbols each coloured by its own category. `nm()`'s compound
  rule cannot do this — it paints a whole label from one leading category, which would wrongly
  colour non-qualifying subunits.
- `lab()` now packs gene rows **width-aware into as many rows as needed**. The old rule split
  into exactly two at the midpoint and estimated 6.1 px/char, under-counting the ‡†§● marks;
  the restored pit genes then pushed both rows past the 1100 viewBox edge and were silently
  clipped. Measured rate is 7.4 px/char.
- Re-verified: nothing clipped, zero text overlaps, drawA clean.

**v81 / v48 — 2026-10-01**

- New category: **Mendelian CNS disease**, sienna `#84330b` (dark `#c78005`). 18 genes.
  Membership is derived, not curated: Open Targets clinical-genetics evidence summed per
  disease for *every* labelled gene, nervous-system only, neoplasms dropped, threshold 0.5
  (set by NPC1 0.699 and NPC2 0.608). Genes whose monogenic disease *is* Alzheimer's (APOE,
  ABCA7, SORL1) are excluded so the category adds information the AD colours do not.
- `§` on TSC1/TSC2: a literature link to AD that Open Targets does not index. Drawn as a mark,
  not a sixth colour, because every candidate hue clearing the five category colours collides
  with a glyph colour (protan ΔE 6.1 and 5.3 vs cholesterol gold, 3.2 vs BMP magenta).
- Genes with no category are now **ink**, not grey: grey sat only ΔE 2.8 from the Open Targets
  teal under protanopia. Scoped to label text; `catCol` stays grey so shape fills are untouched.
- The mTORC1 inset joins the colour code. `nm()` colours a compound label only when every gene
  it names resolves and they agree on a leading category, so TSC1/TSC2 goes sienna while
  FLCN–FNIP, RagA/B and v-ATPase stay default.
- Palette re-validated all-pairs, both modes: **ALL CHECKS PASS**. Light worst CVD ΔE 10.3,
  normal-vision floor 16.4; dark normal-vision floor 15.7.

**v79 / v46 — 2026-10-01**

- Removed the duplicate antibody. Therapeutic hypothesis 1 was drawn twice; the approaching copy
  at (483,49) and its two-line label are gone, and the engaged drawing keeps it. The deleted
  tooltip's unique content (steric intent, the LDLR K_d series with ref [10], the blood-brain
  barrier liability) was merged into the survivor rather than dropped.
- Raised the "Golgi apparatus" label to y341, level with the left end of the top cisterna, and
  moved the ER-to-Golgi arrow onto the outer flank of the ER exit-site tubule it belongs to. The
  label move is what freed the band the arrow now occupies.
- Shortened the APOE mRNA from a 12-degree to an 8-degree arc (70.6 -> 47.1 units).
- Gave every direction arrow the same clearance as the scission arrow: **12.5 units** from a
  structure's outer edge (stroke centreline plus half the stroke width). Twelve of sixteen arrows
  were trimmed by exact de Casteljau subdivision, five of which had an endpoint *inside* a
  membrane. The ER-to-Golgi arrow is the one exception, at 8.9, because its corridor is only
  ~21 units wide.
- Recentred the exocytic lysosome to (505,340), on the midpoint of its own route.
- Replaced the LXR/RXR agonist glyph with **chemical reprogramming** in the nucleus, and removed
  the sterol structure diagrams.

**Reverted, deliberately:** an evidence-weight colour gradient. See Known issues — `catCol` feeds
shape `fill`, so changing the no-category fallback from grey to ink blackened every uncategorised
gene glyph. The ancestry tiering built for it survives in `ancestry_tier.json` and is recorded as
Alhazen claim `scsynth-1bbdb48be256`.

## Sharing and reuse

This repo is **public**. The two Artifact links above are *private* pages, so they will not
open for most readers — clone the repo and open `apoe_endocytosis_atlas.html` or
`apoe_tour.html` directly in a browser instead. Both are self-contained, with no server and no
network needed.

No licence file is present, so by default all rights are reserved and the code is not
redistributable. Add a licence if reuse is intended.

The analysis here is derived from published datasets (see the pipeline above), but the
within-ancestry re-analysis in `ancestry_tier.json` and the pathway percentiles in `MEMO.md`
are not themselves published. Treat the numbers as a preprint-stage result and cite the
upstream papers for the primary data.
