#!/bin/env python

import argparse
import datetime
import sys

from schema.app import ApplicationMetadata


def main(name, version, year, author):
    metadata = ApplicationMetadata(name=name, version=version, year=year, author=author)
    metadata.serialize(sys.stdout.buffer)


if __name__ == "__main__":
    current_year = datetime.datetime.now().year

    parser = argparse.ArgumentParser(description='generate an about.t file.')
    parser.add_argument('name', help='the application name')
    parser.add_argument('version', help='the application version')
    parser.add_argument('-y', '--year', help='the publication year', type=int, default=current_year)
    parser.add_argument('-a', '--author', help="the author's name", default='')

    args = parser.parse_args()
    main(args.name, args.version, args.year, args.author)
