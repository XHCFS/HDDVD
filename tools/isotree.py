#!/usr/bin/env python3
"""Unpack a sparse ISO from sparseiso.py into a folder tree.

The tree holds the same disc as the image, so the folder backend and the
ISO backend can be checked against each other. Only the real ranges listed
in <iso>.ranges are copied; the rest of every file stays a hole, so a
26 GB disc costs only what was fetched.

Usage: isotree.py <image.iso> <out-dir>
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from udfgrab import UDF, SECTOR  # noqa: E402
from sparseiso import load_ranges  # noqa: E402


class Local:
    def __init__(self, path):
        self.f = open(path, 'rb')

    def read(self, off, length):
        self.f.seek(off)
        return self.f.read(length)

    def sector(self, lsn, n=1):
        return self.read(lsn * SECTOR, n * SECTOR)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    iso, out = sys.argv[1], sys.argv[2]
    real = sorted((s, e) for s, e, _ in load_ranges(iso + '.ranges'))
    src = Local(iso)
    udf = UDF(src)
    for path, ext_ref, size, isdir in udf.walk():
        dst = out + path
        if isdir:
            os.makedirs(dst, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        extents, ref = ext_ref
        with open(dst, 'wb') as g:
            pos_in_file = 0
            for pos, ln in extents:
                start = udf.phys(pos, ref) * SECTOR
                for s, e in real:
                    lo, hi = max(s, start), min(e, start + ln)
                    if lo < hi:
                        g.seek(pos_in_file + lo - start)
                        g.write(src.read(lo, hi - lo))
                pos_in_file += ln
            g.truncate(size)
    print(f'{out}: unpacked')


if __name__ == '__main__':
    main()
