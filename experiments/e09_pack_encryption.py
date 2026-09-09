"""e09: Is any EVO pack actually AACS-encrypted in this corpus?

Claim under test (spec/advanced/09_aacs.md 9.6): an encrypted 2048-byte pack has
bytes 0-127 clear with PES_scrambling_control at pack byte 20, and bytes 128-2047
AES-CBC. If PES_scrambling_control is 0 on every sampled pack of every disc, then
no encrypted pack is observable here and CPI/KEY_VF cannot be exercised.

Player must follow: check pack byte 20 bits 5-4 before attempting decryption.
"""
import sys, os, json, struct, math, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
_ROOT = os.path.join(os.path.dirname(__file__), '..')
from udfgrab import Remote, UDF

CACHE = '/tmp/e09_cache.json'
SAMPLES = [
    ('12_MONKEYS', True),
    ('16_BLOCKS', True),
    ('40YR_OLD_VIRGIN', True),
    ('AEON_FLUX', True),
    ('ANCHORMAN', True),
    ('AVIATOR_FRA', True),
    ('BALLS_OF_FURY', True),
    ('BATMAN_BEGINS', True),
    ('1408_DC', False),
    ('ARMY_OF_DARKNESS', False),
    ('ARMY_OF_SHADOWS', False),
]

def entropy(b):
    c = collections.Counter(b); n = len(b)
    return -sum(v/n*math.log2(v/n) for v in c.values())

def biggest_evo(disc):
    import re
    p = os.path.join(_ROOT, f'corpus/{disc}/_listing.txt')
    if not os.path.exists(p): return None
    evos = [(int(m.group(1)), m.group(2)) for m in
            re.finditer(r'FILE\s+(\d+)\s+/HVDVD_TS/(\S+\.EVO)$', open(p, errors='replace').read(), re.M)]
    return max(evos)[1] if evos else None

def probe(disc, evoname, frac=0.5, npack=64):
    url = open(os.path.join(_ROOT, f'corpus/{disc}/_listing.txt')).readline().strip().lstrip('# ')
    u = UDF(Remote(url))
    tgt = None
    for p, e, s, d in u.walk():
        if not d and p.endswith('/' + evoname): tgt = e; break
    if not tgt: return None
    ext, _ = tgt
    segs = []; cum = 0
    for pos, ln in ext:
        n = ln // 2048; segs.append((cum, n, pos)); cum += n
    idx = int(cum * frac)
    blk = b''
    for st, n, pos in segs:
        if st <= idx < st + n:
            blk = u.r.read((u.part_start + pos + (idx - st)) * 2048, npack * 2048); break
    sc = collections.Counter(); ents = []; packs = 0
    for k in range(npack):
        r = blk[k*2048:(k+1)*2048]
        if len(r) < 2048 or r[:4] != b'\x00\x00\x01\xba': continue
        packs += 1
        sc[(r[20] >> 4) & 3] += 1
        ents.append(entropy(r[128:]))
    return {'packs': packs, 'scrambling': dict(sc),
            'tail_entropy': round(sum(ents)/len(ents), 3) if ents else None}

def main():
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    rows = []
    for disc, is_aacs in SAMPLES:
        if not os.path.exists(os.path.join(_ROOT, f'corpus/{disc}/_listing.txt')): continue
        evo = biggest_evo(disc)
        if not evo: continue
        key = f'{disc}/{evo}'
        if key not in cache:
            try: cache[key] = probe(disc, evo)
            except Exception as ex: cache[key] = {'error': str(ex)[:60]}
            json.dump(cache, open(CACHE, 'w'))
        rows.append((disc, is_aacs, evo, cache[key]))
    print(f"{'disc':<18}{'AACS':<6}{'packs':<7}{'scrambling':<22}{'tail entropy'}")
    any_scrambled = False
    for disc, is_aacs, evo, r in rows:
        if not r or 'error' in r:
            print(f"  {disc:<16}{'y' if is_aacs else 'n':<6}ERROR {r}"); continue
        s = r['scrambling']
        if any(int(k) != 0 for k in s): any_scrambled = True
        print(f"  {disc:<16}{'y' if is_aacs else 'n':<6}{r['packs']:<7}{str(s):<22}{r['tail_entropy']}")
    print()
    print(f"ANY PACK WITH PES_scrambling_control != 0 : {any_scrambled}")
    ok_rows = [r for _, _, _, r in rows if r and "error" not in r]
    packs = sum(r["packs"] for r in ok_rows)
    print(f"sampled packs={packs} discs={len(ok_rows)}")
    assert rows, "no discs probed"
    assert ok_rows, "no successful pack samples"
    assert not any_scrambled, "PES_scrambling_control != 00b on a sampled pack"
    assert packs >= 384, packs
    print("E09 PASS")

if __name__ == '__main__':
    main()
