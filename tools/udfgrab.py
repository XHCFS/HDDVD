#!/usr/bin/env python3
"""Walk the UDF filesystem of a remote ISO over HTTP range requests and pull
small files (IFO/BUP/MAP/VTI/XPL/XML/DAT) without downloading the whole image.

Usage: udfgrab.py <iso-url> <outdir> [--list] [--max-bytes N] [--ext .IFO,.BUP]
"""
import sys, os, struct, urllib.request, argparse

SECTOR = 2048

class Remote:
    """Random access to a remote file via HTTP Range, with sector caching."""
    def __init__(self, url, chunk=64 * 1024, sparse=None):
        self.url, self.chunk, self.cache = url, chunk, {}
        self.bytes_fetched = 0
        self.sparse = open(sparse, 'wb+') if sparse else None
        self.size = None

    def _get(self, start, length):
        req = urllib.request.Request(self.url, headers={
            'Range': f'bytes={start}-{start+length-1}', 'User-Agent': 'Mozilla/5.0'})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    d = r.read()
                    if self.size is None:
                        cr = r.headers.get('Content-Range', '')
                        if '/' in cr:
                            self.size = int(cr.rsplit('/', 1)[1])
                self.bytes_fetched += len(d)
                if self.sparse is not None:
                    self.sparse.seek(start)
                    self.sparse.write(d)
                return d
            except Exception:
                if attempt == 3:
                    raise
        return b''

    def read(self, off, length):
        out = bytearray()
        while length > 0:
            ci = off // self.chunk
            if ci not in self.cache:
                self.cache[ci] = self._get(ci * self.chunk, self.chunk)
                if len(self.cache) > 512:
                    self.cache.pop(next(iter(self.cache)))
            blk = self.cache[ci]
            o = off - ci * self.chunk
            take = blk[o:o + length]
            if not take:
                break
            out += take
            off += len(take)
            length -= len(take)
        return bytes(out)

    def sector(self, lsn, n=1):
        return self.read(lsn * SECTOR, n * SECTOR)


def tag_id(b, off=0):
    return struct.unpack_from('<H', b, off)[0] if len(b) >= off + 2 else 0


def long_ad(b, off):
    """Return (length, logical block number, partition reference number)."""
    ln = struct.unpack_from('<I', b, off)[0]
    lbn = struct.unpack_from('<I', b, off + 4)[0]
    ref = struct.unpack_from('<H', b, off + 8)[0]
    return ln & 0x3FFFFFFF, lbn, ref


class UDF:
    def __init__(self, rem):
        self.r = rem
        self.part_start = None
        self.fsd = None
        self.meta_fe_lbn = None      # metadata File Entry, LBN in physical partition
        self.meta_extents = None     # resolved extents of the metadata file
        self._mount()
        self._load_metadata_partition()

    def _mount(self):
        avdp = self.r.sector(256)
        if tag_id(avdp) != 2:
            raise RuntimeError('no AVDP at sector 256')
        vds_len, vds_loc = struct.unpack_from('<II', avdp, 16)
        n = max(1, vds_len // SECTOR)
        blk = self.r.sector(vds_loc, min(n, 32))
        fsd_ad = None
        for i in range(0, len(blk), SECTOR):
            t = tag_id(blk, i)
            if t == 5 and self.part_start is None:          # Partition Descriptor
                self.part_start = struct.unpack_from('<I', blk, i + 188)[0]
            elif t == 6 and fsd_ad is None:                 # Logical Volume Descriptor
                fsd_ad = long_ad(blk, i + 248)
                n_maps = struct.unpack_from('<I', blk, i + 268)[0]
                mo = i + 440
                for _ in range(n_maps):
                    mtype, mlen = blk[mo], blk[mo + 1]
                    if mtype == 2 and b'Metadata Partition' in blk[mo + 4:mo + 36]:
                        # UDF 2.50 metadata partition map: file entry LBN at +40
                        self.meta_fe_lbn = struct.unpack_from('<I', blk, mo + 40)[0]
                    mo += mlen
            elif t == 8:                                    # Terminating Descriptor
                break
        if self.part_start is None or fsd_ad is None:
            raise RuntimeError('PD/LVD not found')
        self.fsd, self.fsd_ref = fsd_ad[1], fsd_ad[2]

    def _load_metadata_partition(self):
        """Resolve the UDF 2.50 metadata file so partition-ref 1 can be mapped."""
        if self.meta_fe_lbn is None:
            return
        e = self._entry_at(self.part_start + self.meta_fe_lbn)
        if e:
            self.meta_extents = e[1]

    def phys(self, lbn, ref=0):
        """Map a logical block in partition `ref` to a physical sector."""
        if ref == 0 or not self.meta_extents:
            return self.part_start + lbn
        # partition ref 1 = metadata partition: index into the metadata file's extents
        remain = lbn
        for pos, ln in self.meta_extents:
            blocks = (ln + SECTOR - 1) // SECTOR
            if remain < blocks:
                return self.part_start + pos + remain
            remain -= blocks
        raise RuntimeError(f'metadata lbn {lbn} beyond metadata file')

    def _entry(self, lbn, ref=0):
        return self._entry_at(self.phys(lbn, ref))

    def _entry_at(self, sector):
        """Return (filetype, [(offset,length)] extents, info_len, inline_bytes)."""
        b = self.r.sector(sector, 1)
        t = tag_id(b)
        if t == 261:
            base, l_ea_off, l_ad_off, info_off = 176, 168, 172, 56
        elif t == 266:
            base, l_ea_off, l_ad_off, info_off = 216, 208, 212, 56
        else:
            return None
        icb_flags = struct.unpack_from('<H', b, 16 + 18)[0]
        ftype = b[16 + 11]
        info_len = struct.unpack_from('<Q', b, info_off)[0]
        l_ea = struct.unpack_from('<I', b, l_ea_off)[0]
        l_ad = struct.unpack_from('<I', b, l_ad_off)[0]
        ad_off = base + l_ea
        adtype = icb_flags & 7
        extents = []
        if adtype == 3:                                     # inline data
            return ftype, [], info_len, b[ad_off:ad_off + l_ad]
        step = 8 if adtype == 0 else (16 if adtype == 1 else 20)
        for o in range(ad_off, ad_off + l_ad, step):
            if o + step > len(b):
                break
            ln = struct.unpack_from('<I', b, o)[0]
            kind, ln = ln >> 30, ln & 0x3FFFFFFF
            pos = struct.unpack_from('<I', b, o + 4)[0]
            if ln == 0:
                continue
            if kind == 0:
                extents.append((pos, ln))
        return ftype, extents, info_len, None

    def readdir(self, lbn, ref=0):
        e = self._entry(lbn, ref)
        if not e:
            return []
        ftype, extents, info_len, inline = e
        # Allocation descriptors inside an ICB refer to the partition holding that ICB.
        data = inline if inline is not None else b''.join(
            self.r.read(self.phys(pos, ref) * SECTOR, ln) for pos, ln in extents)
        out, o = [], 0
        while o + 38 <= len(data):
            if tag_id(data, o) != 257:
                break
            l_fi = data[o + 19]
            chars = data[o + 18]
            _, icb, icb_ref = long_ad(data, o + 20)
            l_iu = struct.unpack_from('<H', data, o + 36)[0]
            fi = data[o + 38 + l_iu: o + 38 + l_iu + l_fi]
            name = ''
            if l_fi:
                name = fi[1:].decode('utf-16-be' if fi[0] == 16 else 'latin-1', 'replace')
            total = 38 + l_iu + l_fi
            o += total + ((4 - total % 4) % 4)
            if chars & 0x08:            # parent entry
                continue
            out.append((name, icb, icb_ref, bool(chars & 0x02)))
        return out

    def root(self):
        b = self.r.sector(self.phys(self.fsd, self.fsd_ref))
        if tag_id(b) != 256:
            raise RuntimeError('no FSD')
        ln, lbn, ref = long_ad(b, 400)
        return lbn, ref

    def walk(self, lbn=None, ref=0, path='', depth=0):
        if lbn is None:
            lbn, ref = self.root()
        if depth > 8:
            return
        for name, icb, icb_ref, isdir in self.readdir(lbn, ref):
            p = f'{path}/{name}'
            if isdir:
                yield p, None, None, True
                yield from self.walk(icb, icb_ref, p, depth + 1)
            else:
                e = self._entry(icb, icb_ref)
                if e:
                    # UDF 2.50: the metadata partition holds FEs, directory data and
                    # EAs only -- regular file data always lives in the physical
                    # partition, so its descriptors are physical regardless of the
                    # partition the ICB itself was read from.
                    yield p, (e[1], 0), e[2], False

    def find(self, path):
        """Resolve `/HVDVD_TS/foo.EVO` without walking `ANY!`. Returns ((extents, ref), size) or None."""
        parts = [p for p in path.strip("/").split("/") if p]
        lbn, ref = self.root()
        for i, name in enumerate(parts):
            hit = None
            for n, icb, icb_ref, isdir in self.readdir(lbn, ref):
                if n == name:
                    hit = (icb, icb_ref, isdir)
                    break
            if hit is None:
                return None
            icb, icb_ref, isdir = hit
            if i + 1 == len(parts):
                if isdir:
                    return None
                e = self._entry(icb, icb_ref)
                if not e:
                    return None
                return (e[1], 0), e[2]
            if not isdir:
                return None
            lbn, ref = icb, icb_ref
        return None

    def fetch(self, extents_ref, size):
        extents, ref = extents_ref
        out = bytearray()
        for pos, ln in extents:
            out += self.r.read(self.phys(pos, ref) * SECTOR, ln)
        return bytes(out[:size])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url'); ap.add_argument('outdir')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--max-bytes', type=int, default=8 * 1024 * 1024)
    ap.add_argument('--ext', default='.IFO,.BUP,.MAP,.VTI,.XPL,.XML,.DAT')
    ap.add_argument('--sparse-out', default=None,
                    help='write fetched sectors into a sparse local ISO for udfclient validation')
    a = ap.parse_args()
    exts = tuple(x.strip().upper() for x in a.ext.split(',') if x.strip())

    rem = Remote(a.url, sparse=a.sparse_out)
    u = UDF(rem)
    entries = list(u.walk())
    files = [(p, e, s) for p, e, s, d in entries if not d]
    print(f'# {a.url}')
    print(f'# partition_start={u.part_start} meta_fe={u.meta_fe_lbn} files={len(files)}')
    for p, e, s, d in entries:
        print(f'{"DIR " if d else "FILE"} {s if s is not None else "":>12} {p}')
    if a.list:
        print(f'# fetched {rem.bytes_fetched/1e6:.1f} MB of metadata')
        return
    os.makedirs(a.outdir, exist_ok=True)
    got = 0
    for p, e, s in files:
        if not p.upper().endswith(exts) or s > a.max_bytes:
            continue
        dst = os.path.join(a.outdir, p.lstrip('/').replace('/', '__'))
        if os.path.exists(dst) and os.path.getsize(dst) == s:
            continue
        with open(dst, 'wb') as f:
            f.write(u.fetch(e, s))
        got += 1
        print(f'  saved {s:>10} {p}')
    print(f'# saved {got} files; fetched {rem.bytes_fetched/1e6:.1f} MB total')
    if rem.sparse is not None and rem.size:
        rem.sparse.truncate(rem.size)
        rem.sparse.close()
        print(f'# sparse image {a.sparse_out} logical size {rem.size}')


if __name__ == '__main__':
    main()
