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
