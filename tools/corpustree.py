#!/usr/bin/env python3
"""Rebuild disc folder trees from the corpus for folder-backend tests.

corpus/<DISC>/ stores the small files of each disc under flattened names
(HVDVD_TS__FEATURE.MAP) plus _listing.txt with every directory and file of
the disc and its size. This recreates the original layout:

    <out>/<DISC>/ADV_OBJ/DISCID.DAT
    <out>/<DISC>/HVDVD_TS/FEATURE.MAP
    ...

Saved files are hard links into the corpus (copies when linking fails).
Files the corpus did not save (EVOs, large ACAs, most of ANY!) become sparse
placeholders of the listed size: their names and sizes are right, their
bytes are zeros. <out>/<DISC>/../<DISC>.placeholders lists them.

Usage: corpustree.py <corpus-dir> <out-dir> [DISC ...]
"""
import os, shutil, sys


def build(corpus, out, disc):
    src = os.path.join(corpus, disc)
    root = os.path.join(out, disc)
    placeholders = []
    with open(os.path.join(src, '_listing.txt'), encoding='utf-8') as f:
        lines = f.read().splitlines()
    for line in lines:
        if line.startswith('DIR '):
            path = line.split(None, 1)[1]
            os.makedirs(root + path, exist_ok=True)
        elif line.startswith('FILE '):
            _, size, path = line.split(None, 2)
            size = int(size)
            dst = root + path
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.lexists(dst):
                os.remove(dst)
            saved = os.path.join(src, path.lstrip('/').replace('/', '__'))
            if os.path.isfile(saved) and os.path.getsize(saved) == size:
                try:
                    os.link(saved, dst)
                except OSError:
                    shutil.copyfile(saved, dst)
            else:
                with open(dst, 'wb') as g:
                    g.truncate(size)
                placeholders.append(path)
    with open(root + '.placeholders', 'w', encoding='utf-8') as f:
        f.write(''.join(p + '\n' for p in placeholders))
    return len(placeholders)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    corpus, out = sys.argv[1], sys.argv[2]
    discs = sys.argv[3:] or sorted(
        d for d in os.listdir(corpus)
        if os.path.isfile(os.path.join(corpus, d, '_listing.txt')))
    for d in discs:
        n = build(corpus, out, d)
        print(f'{d}: {n} placeholders')


if __name__ == '__main__':
    main()
