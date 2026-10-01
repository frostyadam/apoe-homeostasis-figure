"""Open Targets: association of each figure gene with neurodegenerative disease (MONDO_0005559, indirect)."""
import json, urllib.request
API="https://api.platform.opentargets.org/api/v4/graphql"
def q(query,var):
    r=urllib.request.Request(API,data=json.dumps({"query":query,"variables":var}).encode(),headers={"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=120))
G="""APOE LDLR LRP1 VLDLR LRP8 SORL1 SCARB1 CLTC AP2M1 PICALM DNM1 DNM2 BIN1 RAB5A EEA1 RAB11A RAB7A NPC1 NPC2 LIPA
HSPA5 CANX SEC61A1 GOLGA2 GORASP1 COPA SNAP23 STX4 VAMP3 RAB27A ARL8B SYT7 SYT11 STARD3 VAPA OSBPL1A
ATP6V1A ATP6V0D1 ATP6V0A1 SLC38A9 LAMTOR1 LAMTOR2 LAMTOR3 RRAGA RRAGB RRAGC RRAGD FLCN FNIP1 RHEB MTOR RPTOR MLST8
TM6SF1 ABCA1 ABCA7 CD36 GPIHBP1 TSC1 TSC2""".split()
ids={}
for g in G:
    r=q('query($s:String!){search(queryString:$s,entityNames:["target"],page:{index:0,size:3}){hits{id name entity object{... on Target{approvedSymbol}}}}}',{"s":g})
    for h in r["data"]["search"]["hits"]:
        if h["object"] and h["object"].get("approvedSymbol")==g: ids[g]=h["id"]; break
miss=[g for g in G if g not in ids]; print("unmapped:",miss)
r=q('''query($b:[String!]){disease(efoId:"MONDO_0005559"){name associatedTargets(Bs:$b,page:{index:0,size:100}){count rows{target{approvedSymbol} score datatypeScores{id score}}}}}''',{"b":list(ids.values())})
rows={x["target"]["approvedSymbol"]:x for x in r["data"]["disease"]["associatedTargets"]["rows"]}
out={}
print(f"{'gene':9s} {'overall':>7s} {'genetic':>7s} {'literature':>10s} {'animal':>7s} other")
for g in G:
    x=rows.get(g); dt={d["id"]:d["score"] for d in (x["datatypeScores"] if x else [])}
    out[g]=dict(overall=x["score"] if x else 0,**dt)
    other={k:round(v,2) for k,v in dt.items() if k not in("genetic_association","literature","animal_model")}
    print(f"{g:9s} {out[g]['overall']:7.3f} {dt.get('genetic_association',0):7.3f} {dt.get('literature',0):10.3f} {dt.get('animal_model',0):7.3f} {other}")
json.dump(dict(ids=ids,assoc=out),open("/home/afrost/apoe-research/endocytosis/ot_neurodegen.json","w"),indent=1)
