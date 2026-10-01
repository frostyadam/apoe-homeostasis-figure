"""Theoretical isoelectric point of mature APOE isoforms (Bjellqvist pKa set, as in ExPASy/Biopython)."""
import urllib.request
seq="".join(urllib.request.urlopen("https://rest.uniprot.org/uniprotkb/P02649.fasta").read().decode().splitlines()[1:])
POS={'K':10.0,'R':12.0,'H':5.98}; NEG={'D':4.05,'E':4.45,'C':9.0,'Y':10.0}
NT={'A':7.59,'M':7.0,'S':6.93,'P':8.36,'T':6.82,'V':7.44,'E':7.7}; CT={'D':4.55,'E':4.75}
def charge(s,pH):
    pos={**{k:s.count(k) for k in POS},'N':1}; pk={**POS,'N':NT.get(s[0],7.5)}
    neg={**{k:s.count(k) for k in NEG},'C_':1}; nk={**NEG,'C_':CT.get(s[-1],3.55)}
    return sum(n/(1+10**(pH-pk[k])) for k,n in pos.items())-sum(n/(1+10**(nk[k]-pH)) for k,n in neg.items())
def pI(s):
    lo,hi=0.0,14.0
    for _ in range(60):
        m=(lo+hi)/2; lo,hi=(m,hi) if charge(s,m)>0 else (lo,m)
    return (lo+hi)/2
assert seq[129]=="C" and seq[175]=="R", "canonical P02649 is expected to be APOE3 (C130, R176)"
e3=seq[18:]; e4=seq[:129]+"R"+seq[130:]; e4=e4[18:]; e2=(seq[:175]+"C"+seq[176:])[18:]
for nm,s in (("APOE2",e2),("APOE3",e3),("APOE4",e4)):
    print(f"{nm}  pI {pI(s):.2f}   net charge at pH 6.3: {charge(s,6.3):+.2f}   at pH 7.4: {charge(s,7.4):+.2f}   length {len(s)}")
