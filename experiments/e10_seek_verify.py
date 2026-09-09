"""e10: End-to-end seek. Proves sheet 07 EVOBU walk math on a live MAP+EVO.

Claim: sum(EVOBU_SZ) == EVO pack count; reserved bits zero; a mid-clip seek by
accumulated EVOBU_SZ lands on an MPEG-2 pack start (00 00 01 BA).
Player must follow: seek by accumulating EVOBU_SZ (bits 0-12, 13-bit) * 2048.
"""
import sys, os, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
_ROOT = os.path.join(os.path.dirname(__file__), '..')
from udfgrab import Remote, UDF
u16=lambda b,o: struct.unpack_from('>H',b,o)[0]; u32=lambda b,o: struct.unpack_from('>I',b,o)[0]
if len(sys.argv) >= 4:
    disc, mapname, evoname = sys.argv[1], sys.argv[2], sys.argv[3]
else:
    disc, mapname, evoname = 'DOWNFALL', 'EVOB002.MAP', 'EVOB002.EVO'
url=open(os.path.join(_ROOT, f'corpus/{disc}/_listing.txt')).readline().strip().lstrip('# ')
u=UDF(Remote(url))
mp=ev=None
for p,e,s,d in u.walk():
    if d: continue
    if p.endswith('/'+mapname): mp=(e,s)
    elif p.endswith('/'+evoname): ev=(e,s)
(mext,_),msz = mp; (eext,_),esz = ev
mapb=b''.join(u.r.read((u.part_start+pos)*2048, ln) for pos,ln in mext)[:msz]
print(f"# {disc}  {mapname} ({msz}B)  {evoname} ({esz:,}B = {esz//2048:,} packs)")
tmapi_ns=u16(mapb,55); tmap_ty=u16(mapb,20)
print(f"  TMAP_TY={tmap_ty:#06x} TMAPI_Ns={tmapi_ns}")
sa=u32(mapb,384); evobin=u16(mapb,388); nent=u16(mapb,390)
print(f"  TMAPI_SRP: SA={sa} VTS_EVOBIN={evobin} EVOBU_ENT_Ns={nent}")
# walk EVOBU_ENT
tot_sz=tot_tm=0
for i in range(nent):
    w=u32(mapb, sa+i*4)
    sz=w & 0x1FFF; tm=(w>>13)&0xFF; ref=(w>>21)&0x7FF   # 13-bit SZ (sheet 07; e08 finds SZ>2047)
    # no reserved bits between fields: 13(SZ)+8(TM)+11(1STREF)=32 exactly
    tot_sz+=sz; tot_tm+=tm
print(f"  walked {nent} EVOBU_ENT (13-bit SZ): sum EVOBU_SZ={tot_sz:,} packs  sum PB_TM={tot_tm:,} fields")
print(f"  EVO packs={esz//2048:,}   match={'YES' if tot_sz==esz//2048 else 'off by '+str(esz//2048-tot_sz)}")
# seek test: jump to entry N/2, read that pack, expect MPEG-2 pack header
mid=nent//2; off=sum((u32(mapb,sa+i*4)&0x1FFF) for i in range(mid))
# EVO offset in packs -> sector; account for extents
target=off
seg=[];cum=0
for pos,ln in eext:
    n=ln//2048; seg.append((cum,n,pos)); cum+=n
for st,n,pos in seg:
    if st<=target<st+n:
        raw=u.r.read((u.part_start+pos+(target-st))*2048,4)
        ok = raw == b'\x00\x00\x01\xba'
        print(f"  seek to EVOBU {mid}: pack {target} -> {raw.hex(' ')} -> {'pack start OK' if ok else 'MISALIGNED'}")
        assert tot_sz == esz//2048, "EVOBU_SZ sum != EVO packs"
        assert ok, "seek did not land on a pack boundary"
        print("E10 PASS")
        break
