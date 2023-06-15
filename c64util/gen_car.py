#!/bin/env python

import argparse
import sys

from schema.car import (
    CarArchiveType,
    CarCompressionType,
    CarHeader,
)


def main(paths, path_prefix, archive_type, compression_type, note, recursive=False):
    header = CarHeader(archive_type=archive_type, note=note)
    header.serialize(sys.stdout.buffer)


if __name__ == "__main__":
    archive_types = [ t.name.lower() for t in CarArchiveType ]
    archive_default = CarArchiveType.GENERAL.name.lower()
    compression_types = [ t.name.lower() for t in CarCompressionType ]
    compression_default = CarCompressionType.NONE.name.lower()

    parser = argparse.ArgumentParser(description='generate a .car archive file.')
    parser.add_argument('paths', help='paths to files and/or directories', nargs='*')
    parser.add_argument('-r', '--recursive', help='write directories and their contents recursively', action='store_true')
    parser.add_argument('-p', '--prefix', help='path prefix for the root of the archive', default='/')
    parser.add_argument('-t', '--type', help='archive type (default general)', choices=archive_types, default=archive_default)
    parser.add_argument('-c', '--compression', help='compression type (default none)', choices=compression_types, default=compression_default)
    parser.add_argument('-n', '--note', help='a note which will be added to the archive metadata', default='')

    args = parser.parse_args()
    archive_type = CarArchiveType[args.type.upper()]
    compression_type = CarCompressionType[args.compression.upper()]

    main(args.paths, args.prefix, archive_type, compression_type, args.note, recursive=args.recursive)
