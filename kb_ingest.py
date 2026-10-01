"""Ingest the papers behind the APOE endocytosis cartoon into scinv-6808f3d27a90's collection, then verify."""
import json, os, subprocess
CORE=os.path.expanduser('~/.claude/plugins/cache/skillful-alhazen/alhazen-core/0.1.0')
S='/home/afrost/.claude/external-skills/alhazen-skill-deep-research/skills/scientific-literature/scientific_literature.py'
COLL='collection-164e53a90461'
def run(*a):
    p=subprocess.run(['uv','run','--project',CORE,'--with','requests','python',S,*a],capture_output=True,text=True,
                     env={**os.environ,'TYPEDB_DATABASE':'alh_deep_research'},timeout=300)
    o=p.stdout
    try: return json.loads(o[o.index('{'):])
    except Exception: return {"_raw":o[-300:],"_err":p.stderr[-300:]}
PAPERS=[("TM6SF1 2026 PNAS","10.1073/pnas.2622424123"),("Castellano 2017","10.1126/science.aag1417"),
 ("Lim 2019","10.1038/s41556-019-0391-5"),("Wilhelm 2017","10.15252/embj.201695917"),("Rocha 2009","10.1083/jcb.200811005"),
 ("Sancak 2010","10.1016/j.cell.2010.02.024"),("Zoncu 2011","10.1126/science.1207056"),("Tsun 2013","10.1016/j.molcel.2013.09.016"),
 ("Reddy 2001","10.1016/s0092-8674(01)00421-4"),("Wahrle 2004","10.1074/jbc.m407963200"),("Infante 2008","10.1073/pnas.0807328105"),
 ("Pu 2015","10.1016/j.devcel.2015.02.011"),("E2 signature 2025","10.1002/advs.202509764")]
out=[]
for lab,doi in PAPERS:
    r=run('ingest','--doi',doi,'--collection',COLL)
    pid=r.get('paper_id') or r.get('id')
    v=run('show','--id',pid) if pid else {}
    title=(v.get('title') or v.get('name') or (v.get('paper') or {}).get('title') or '') if isinstance(v,dict) else ''
    print(f"{lab:18s} {doi:34s} -> {pid}  status={r.get('status')}  verified_title={str(title)[:70]!r}")
    out.append(dict(label=lab,doi=doi,ingest=r,paper_id=pid,verified_title=title))
json.dump(out,open('/home/afrost/apoe-research/endocytosis/kb_ingest_result.json','w'),indent=1)
