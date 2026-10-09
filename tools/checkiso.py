#!/usr/bin/env python3
"""Compare udfcheck output for a sparse ISO with the corpus.

Every path and size must match corpus/<DISC>/_listing.txt, and every file the
corpus saved must hash the same as read through libudfread.

Usage: udfcheck X.iso | checkiso.py <corpus-dir> <DISC>
"""
import os, sys


def fnv64(data):
    h = 0xcbf29ce484222325
    for b in data:
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return f'{h:016x}'


def main():
    corpus, disc = sys.argv[1], sys.argv[2]
    listing = {}
    with open(os.path.join(corpus, disc, '_listing.txt'), encoding='utf-8') as f:
        for line in f:
            if line.startswith('FILE '):
                _, size, path = line.rstrip('\n').split(None, 2)
                listing[path] = int(size)
    seen, bad, compared = set(), 0, 0
    for line in sys.stdin:
        if not line.startswith('FILE '):
            if line.startswith(('ERROR', 'HOLE')):
                print(line.rstrip()); bad += 1
            continue
        _, size, h, path = line.rstrip('\n').split(None, 3)
        seen.add(path)
        if listing.get(path) != int(size):
            print(f'size {path}: iso {size} listing {listing.get(path)}'); bad += 1
        saved = os.path.join(corpus, disc, path.lstrip('/').replace('/', '__'))
        if h != '-' and os.path.isfile(saved):
            with open(saved, 'rb') as g:
                if fnv64(g.read()) != h:
                    print(f'bytes differ {path}'); bad += 1
            compared += 1
    for path in sorted(set(listing) - seen):
        print(f'missing from iso {path}'); bad += 1
    print(f'{disc}: {len(seen)} files, {compared} compared with corpus, {bad} problems')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
