"""Apply the catalogue's elemental review package to a separate copy of Ravager's OBJEX.GFF."""
import argparse
import os
from pathlib import Path
import shutil
import struct
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import sl_figures as gff


# Object number, shipped picture, review picture. The duplicate fire templates are used in game.
TIERS = (
    (422, 2538, 2538), (426, 2405, 2405),
    (424, 1881, 1881), (428, 1881, 3954),
    (420, 2540, 2540), (423, 2540, 2540), (409, 2557, 2557), (427, 2557, 2557),
    (425, 915, 915), (429, 915, 3955),
)
BANKS = {'BMP ': 'base', 'CBMP': 'combat', 'SCMD': 'script'}


def build(source, package):
    figures = {target for _, _, target in TIERS}
    changes = {}
    with ZipFile(package) as art:
        for figure in figures:
            for kind, name in BANKS.items():
                changes[kind, figure] = art.read(f'{figure}/{name}.chunk')

    allowed = {actor: {old, new} for actor, old, new in TIERS}
    # A modded base may already use one of these pictures for an unrelated actor.
    for (kind, actor), record in source.items():
        if kind == 'OJFF':
            picture, = struct.unpack_from('<H', record, 12)
            if picture in figures and picture not in allowed.get(actor, ()):
                raise ValueError(f'figure {picture} is in use by unexpected object {actor}')

    for actor, old, new in TIERS:
        record = bytearray(source['OJFF', actor])
        current, = struct.unpack_from('<H', record, 12)
        if current not in (old, new):
            raise ValueError(f'object {actor} already uses another figure ({current})')
        if old != new:
            keys = [(kind, new) for kind in BANKS]
            if current == old and any(key in source for key in keys):
                raise ValueError(f'new figure number {new} already contains resources')
            if current == new and any(key not in source for key in keys):
                raise ValueError(f'object {actor} points to an incomplete figure {new}')
            struct.pack_into('<H', record, 12, new)
            changes['OJFF', actor] = bytes(record)

    return {key: value for key, value in changes.items() if source.get(key) != value}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--package', type=Path, default=Path(__file__).with_name('elemental-tiers.zip'))
    args = parser.parse_args()
    if args.output.resolve() == args.base.resolve():
        parser.error('choose a separate output path')
    input_chunks = gff.load(args.base)[1]
    changes = build(input_chunks, args.package)
    with TemporaryDirectory(dir=args.output.parent) as temp:
        staged = Path(temp) / 'OBJEX.GFF'
        if changes:
            gff.write_ranged(args.base, changes, staged)
        else:
            shutil.copyfile(args.base, staged)
        check = gff.load(staged)[1]
        if build(check, args.package):
            raise ValueError('output archive did not retain the elemental split')
        os.replace(staged, args.output)


if __name__ == '__main__':
    main()
