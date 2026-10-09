#!/usr/bin/env python3
"""Build a sparse local copy of a remote HD DVD ISO for library tests.

The copy has the full logical size of the disc. Only these parts hold real
bytes, everything else is a hole that reads back as zeros:
  - the first and last MiB of the disc (volume recognition sequence, both
    anchors, the descriptor sequences),
  - every UDF structure the walk touches (metadata partition, file entries,
    directories),
  - every file except .EVO files, rounded up to whole sectors,
  - .EVO files up to --evo-bytes from their start (whole file when smaller).

A <out>.ranges file lists the real byte ranges ("start end path", end
exclusive, path "-" for filesystem structures) so a test knows which reads
return disc data.

Usage: sparseiso.py <iso-url> <out.iso> [--evo-bytes N]
       sparseiso.py --resume <iso-url> <out.iso> [--evo-bytes N]   (fetch only what is missing)
"""
import argparse, os, sys, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from udfgrab import Remote, UDF, SECTOR  # noqa: E402

PIECE = 4 * 1024 * 1024
EDGE = 1024 * 1024
WORKERS = 6


class LoggedRemote(Remote):
    """Remote that remembers every byte range it fetched and why."""
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.label = '-'
        self.ranges = []
        self.lock = threading.Lock()

    def _get(self, start, length):
        d = super()._get(start, length)
        with self.lock:
            self.ranges.append((start, start + len(d), self.label))
        return d

    def piece(self, start, length, label):
        """Fetch one range straight into the image; safe from many threads."""
        req = urllib.request.Request(self.url, headers={
            'Range': f'bytes={start}-{start+length-1}', 'User-Agent': 'Mozilla/5.0'})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    d = r.read()
                if len(d) != length:
                    raise IOError(f'short read {len(d)}/{length} at {start}')
                break
            except Exception:
                if attempt == 3:
                    raise
        os.pwrite(self.sparse.fileno(), d, start)
        with self.lock:
            self.bytes_fetched += len(d)
            self.ranges.append((start, start + len(d), label))


def merge(ranges):
    out = []
    for s, e, p in sorted(ranges):
        if out and s <= out[-1][1] and out[-1][2] == p:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e, p])
    return out


def edges(size):
    return [(0, EDGE, '-'), (size - EDGE, EDGE, '-')]


def load_ranges(path):
    with open(path) as f:
        rows = [l.split(' ', 2) for l in f.read().splitlines()
                if l and not l.startswith('#')]
    return [(int(x), int(y), p) for x, y, p in rows]


def covered(have, start, end):
    """True when [start, end) lies inside the union of the `have` ranges."""
    for s, e, _ in sorted(have):
        if s > start:
            return False
        if e > start:
            start = e
            if start >= end:
                return True
    return start >= end


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--resume', action='store_true',
                    help='keep an existing image and fetch only what it lacks')
    ap.add_argument('url'); ap.add_argument('out')
    ap.add_argument('--evo-bytes', type=int, default=32 * 1024 * 1024,
                    help='bytes to copy from the start of each .EVO (0 = none)')
    a = ap.parse_args()

    have = []
    if a.resume:
        have = load_ranges(a.out + '.ranges')
        rem = LoggedRemote(a.url)
        rem.sparse = open(a.out, 'r+b')
    else:
        rem = LoggedRemote(a.url, sparse=a.out)
    udf = UDF(rem)
    entries = list(udf.walk())

    rem.sparse.flush()
    jobs = []
    for path, ext_ref, size, isdir in entries:
        if isdir:
            continue
        want = size
        if path.upper().endswith('.EVO'):
            want = min(size, a.evo_bytes)
        extents, ref = ext_ref
        left = want
        for pos, ln in extents:
            if left <= 0:
                break
            start = udf.phys(pos, ref) * SECTOR
            take = -(-min(ln, left) // SECTOR) * SECTOR
            for done in range(0, take, PIECE):
                jobs.append((start + done, min(PIECE, take - done), path))
            left -= take
        print(f'{want:>12} of {size:>12} {path}', flush=True)

    jobs += edges(rem.size)
    jobs = [j for j in jobs if not covered(have, j[0], j[0] + j[1])]
    with ThreadPoolExecutor(WORKERS) as pool:
        for n, _ in enumerate(pool.map(lambda j: rem.piece(*j), jobs), 1):
            if n % 10 == 0 or n == len(jobs):
                print(f'# {n}/{len(jobs)} pieces, {rem.bytes_fetched/1e6:.1f} MB', flush=True)

    rem.sparse.truncate(rem.size)
    rem.sparse.close()
    with open(a.out + '.ranges', 'w') as f:
        f.write(f'# {a.url}\n# size {rem.size}\n')
        for s, e, p in merge(have + rem.ranges):
            f.write(f'{s} {min(e, rem.size)} {p}\n')
    print(f'# {a.out}: logical {rem.size/1e9:.2f} GB, fetched {rem.bytes_fetched/1e6:.1f} MB')


if __name__ == '__main__':
    main()
