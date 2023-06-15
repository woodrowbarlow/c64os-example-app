#!/bin/env python

import argparse
import collections
import json
import sys

from schema.app import ApplicationMenu


def main(config):
    menu = ApplicationMenu(menu=config)
    menu.serialize(sys.stdout.buffer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate a menu.m file.')
    parser.add_argument('config', help='path to a menu.json file')

    args = parser.parse_args()
    decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
    with open(args.config, 'r') as f:
        config = decoder.decode(f.read())
    main(config)
