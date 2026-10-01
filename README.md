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
| Atlas | **v82** | `apoe_endocytosis_atlas.html` |
| Tour | **v49** | `apoe_tour.html`, 9 stops |

Republishing the same file path keeps the URL, so the artifact version number is the figure's
real version history; git records the source that produced each one.

### Changelog

**v80 / v47 — 2026-10-01**

- Moved the "Recycling endosome" label to 3 o'clock of its own structure. Anchored `end` at
  (612,270) it extended leftward and landed at x545-612 / y254-292, directly above the
  "Lysosome exocytosis" label at x541-615 — two stacked labels, neither beside the thing it
  named. Now anchored `start` at (680,215): 16.5 units clear of the endosome's outer edge,
  block centre 3.7 units above the circle centre.

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
