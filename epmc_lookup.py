import json, sys, urllib.parse, urllib.request
Q=[("TM6SF1","TITLE:\"TM6SF1\" AND (TITLE:mTORC1 OR TITLE:structure)"),
   ("Castellano2017","TITLE:\"Lysosomal cholesterol activates mTORC1\""),
   ("Lim2019","TITLE:\"ER-lysosome contacts enable cholesterol sensing by mTORC1\""),
   ("Wilhelm2017","TITLE:\"STARD3 mediates endoplasmic reticulum-to-endosome cholesterol transport\""),
   ("Rocha2009","TITLE:\"Cholesterol sensor ORP1L contacts the ER protein VAP\""),
   ("Sancak2010","TITLE:\"Ragulator-Rag complex targets mTORC1 to the lysosomal surface\""),
   ("Zoncu2011","TITLE:\"mTORC1 senses lysosomal amino acids through an inside-out mechanism\""),
   ("Tsun2013","TITLE:\"folliculin tumor suppressor is a GAP for the RagC/D GTPases\""),
   ("Reddy2001","TITLE:\"Plasma membrane repair is mediated by Ca(2+)-regulated exocytosis of lysosomes\" OR TITLE:\"Plasma membrane repair is mediated by Ca2+-regulated exocytosis of lysosomes\""),
   ("Wahrle2004","TITLE:\"ABCA1 is required for normal central nervous system ApoE levels\""),
   ("Infante2008","TITLE:\"NPC2 facilitates bidirectional transfer of cholesterol between NPC1 and lipid bilayers\""),
   ("Pu2015","TITLE:\"BORC, a multisubunit complex that regulates lysosome positioning\""),
   ("Chen2025","TITLE:\"R136S binds to Tau\""),
   ("E2sig2025","TITLE:\"Robust Serum Proteomic Signature of the E2 Allele\"")]
for k,q in Q:
    u="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=q,format="json",resultType="core",pageSize=3))
    r=json.load(urllib.request.urlopen(u,timeout=60))["resultList"]["result"]
    for x in r[:2]:
        print(f"{k:14s}| {x.get('doi','-'):38s}| {x.get('pmid','-'):9s}| {x.get('pubYear')}| {x.get('source')}| {x.get('title','')[:95]}")
    if not r: print(f"{k:14s}| NO HIT")
