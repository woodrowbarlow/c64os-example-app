# C64 OS Utilities

This is a collection of utilities, written in python, for working with filetypes that are used in C64 OS.

In the long term, my plan is to separate this into a separate repo and publish it as a Python package that you can install with `pip`. I'd just like to get some basic features working and tested first.

## Schemas

This is a collection of classes for parsing and generating various filetypes. Each schema class provides a `serialize` and `deserialize` function:

* `serialize`: convert the current class into a binary data and write it into the provided buffer.
* `deserialize`: from a buffer full of binary data, parse that data into a Python class instance (so that individual fields can be inspected and modified).

This can be used to load data from a file or save data to a file.

For instance, to generate a `.car` archive from scratch:

    archive = CarArchive('out/main.o', 'out/menu.m')
    with open('out/application.car', 'wb') as f:
        archive.serialize(f)

Or to parse an application metadata file:

    with open('out/about.t', 'rb') as f:
        metadata = ApplicationMetadata.deserialize(f)
    print(f'{metadata.name} v{metadata.version}')
    print(f'Copyright {metadata.year}, {metadata.author}')
