#!/bin/env python

import argparse
import cbmcodecs2
import collections
import json
import sys


def write_menu(menu, buffer, codec):
    for key, val in menu.items():
        if isinstance(val, dict):
            count = len(val)
            size = chr(ord('a')+count-1)
            buffer.write(f'{key};{size}'.encode(codec) + b'\x0d')
            write_menu(val, buffer, codec)
        else:
            buffer.write(f'{key}:{val}'.encode(codec) + b'\x0d')


def main(config):
    lc_codec='petscii-c64en-lc'
    write_menu(config, sys.stdout.buffer, lc_codec)
    sys.stdout.buffer.write(b'\x0d')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a menu.m file.')
    parser.add_argument('config', help='path to a menu.json file')

    args = parser.parse_args()
    with open(args.config, 'r') as f:
        config = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(f.read())
    main(config)
