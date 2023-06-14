#!/bin/env python

import argparse
import cbmcodecs2
import datetime
import sys


def main(name, version, author):
    lc_codec='petscii-c64en-lc'
    lines = [
        name.encode(lc_codec),
        b'\x20' + version.encode(lc_codec),
        str(datetime.date.today().year).encode(lc_codec),
        author.encode(lc_codec)
    ]
    for line in lines:
        sys.stdout.buffer.write(line + b'\x0d')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate an about.t file.')
    parser.add_argument('name', help='the application name')
    parser.add_argument('version', help='the application version')
    parser.add_argument('author', help="the author's name")

    args = parser.parse_args()
    main(args.name, args.version, args.author)
