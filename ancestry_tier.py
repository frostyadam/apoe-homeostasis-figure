"""Per-gene ancestry concordance for the figure's evidence ramp.

Derived, not hard-coded: reads the two WITHIN-ancestry contrasts from ST12 and asks
whether a gene's pooled direction holds in BOTH strata. Heterogeneity is tested with
GLS using the measured between-domain error correlations (errcorr.json), because the
five LC domains are correlated and independent pooling is anti-conservative.
Writes ancestry_tier.json for 01_build_data.py to consume.
"""
import json, math, statistics as st
import numpy as np, openpyxl
from scipy import stats

R0 = "/home/afrost/apoe-research"
DOMS = ['ACHE_SERT_LC_WM', 'ACHE_SERT_Npep', 'Astro', 'LC', 'Oligo_Astro']
EC = json.load(open(f"{R0}/shared-spatial/errcorr.json"))
R = np.array([[EC.get(f"{a}|{b}", EC.get(f"{b}|{a}", 1.0 if a == b else 0.0))
               for b in DOMS] for a in DOMS], float)

wb = openpyxl.load_workbook(f"{R0}/shared-spatial/ST12-DEtables.xlsx", read_only=True, data_only=True)
def grab(sheet):
    ws = wb[sheet]; it = ws.iter_rows(values_only=True); h = [str(x) for x in next(it)]
    gi, di, li, ti, fi = (h.index(x) for x in ['Gene Symbol', 'Domain', 'logFC', 't statistic', 'FDR'])
    out = {}
    for r in it:
        if r[li] is None or not r[ti]: continue
        out.setdefault(r[gi], {})[r[di]] = (r[li], abs(r[li] / r[ti]), r[fi])
    return out
EA = grab('APOE win Ancestry (EA E4-EA E2)')
AA = grab('APOE w.in Ancestry (AA E4-AA E2')
wb.close()

one = np.ones(len(DOMS))
out = {}
for g in sorted(set(EA) & set(AA)):
    if not all(d in EA[g] and d in AA[g] for d in DOMS): continue
    em = st.mean([EA[g][d][0] for d in DOMS]); am = st.mean([AA[g][d][0] for d in DOMS])
    esig = sum(EA[g][d][2] < 0.05 for d in DOMS); asig = sum(AA[g][d][2] < 0.05 for d in DOMS)
    d = np.array([EA[g][x][0] - AA[g][x][0] for x in DOMS])
    se = np.array([EA[g][x][1] for x in DOMS]); sa = np.array([AA[g][x][1] for x in DOMS])
    C = np.outer(se, se) * R + np.outer(sa, sa) * R
    Ci = np.linalg.inv(C); den = one @ Ci @ one
    est = (one @ Ci @ d) / den
    p = 2 * stats.norm.sf(abs(est / math.sqrt(1 / den)))
    # concordant = same sign in both strata, nominally significant in BOTH, and no
    # significant between-stratum heterogeneity
    conc = bool(em * am > 0 and esig and asig and p >= 0.05)
    out[g] = dict(ea=round(em, 3), aa=round(am, 3), ea_sig=esig, aa_sig=asig,
                  p_het=float(f"{p:.3g}"), concordant=conc)
json.dump(out, open("ancestry_tier.json", "w"), indent=0)
print(f"{len(out)} genes scored; concordant in both ancestries: "
      f"{sum(v['concordant'] for v in out.values())}")
