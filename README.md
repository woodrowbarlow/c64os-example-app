# C64 OS Example App

This is (work in progress) project template set up to cross-assemble for the
C64 from Linux, specifically for making C64 OS applications.

C64 OS is a graphical general-purpose operating system for the Commodore 64,
created by Greg Nacu and released in 2022. C64 OS is commercial software, and
C64 OS applications cannot run without a copy of C64 OS. The operating system
is available for purchase at:

https://c64os.com/c64os/

## Disclaimer

Greg Nacu, the developer of C64 OS, is a firm believer in developing natively
(as opposed to cross-assembling).

See the section "Programming natively vs cross assembling" for more info:

https://c64os.com/c64os/programmersguide/devenvironment

Greg raises good points... but at the end of the day I want to use git. So
that's why I've set this up.

## Download

Via SSH:

    git clone --recurse-submodules git@github.com:woodrowbarlow/c64os-example-app.git

Via HTTPS:

    git clone --recurse-submodules https://github.com/woodrowbarlow/c64os-example-app.git

As an archive:

    wget https://github.com/woodrowbarlow/c64os-example-app/archive/refs/heads/main.zip -O c64os-example-app.zip

## Dependencies

**Python**

Python is used to translate between some file formats and encodings.

You need Python 3.10 or newer.

https://www.python.org/

You'll also need to install a Python package called Poetry:

    python -m pip install poetry

Finally, use Poetry to install the rest of the Python dependencies:

    python -m poetry install

Those dependencies get installed in a virtual environment, to avoid polluting
your system environment. The Makefile takes care of activating that environment
when necessary.

**Make**

You'll need to be able to execute `Makefile`s. I use GNU Make but any
POSIX-compliant `Makefile` runner should do.

We also depend on a few standard UNIX tools.

**Cross-Assembler**

The cross-assembler is TMPx. This translates the source into 6502 binaries.

https://style64.org/release/tmpx-v1.1.0-style

You do not need to download this. The Makefile will automatically download it
on first run.

**Emulator**

The emulator is used for testing and for generating a `.d64` disk image
containing the final application. The emulator is not strictly necessary if
you are running the application on real hardware (and have a way to transfer
the file).

VICE - the Versatile Commodore Emulator (at least v3.5)

https://vice-emu.sourceforge.io/

**ROMs and Disk Images**

If you wish you run the app in emulation, there are a couple of extra files
that you must provide:

* `rom/c64os.dhd`
* `rom/cmd_hd_bootrom.bin`

The first one is included on your C64 OS SD card. For more info:

https://c64os.com/c64os/usersguide/installation#installation_vice

The second one can be purchased from Retro Innovations here:

https://store.go4retro.com/commodore/cmd-hdd-boot-rom-2-80-binary-image/

If you use JiffyDOS (highly recommended for better performance) you may
optionally provide those binaries as well:

* `rom/JiffyDOS_C64.bin`
* `rom/JiffyDOS_1541-II.bin`

Those binaries are also available for purchase from Retro Innovations:

https://store.go4retro.com/jiffydos-64-kernal-rom-overlay-image/  
https://store.go4retro.com/jiffydos-1541-dos-rom-overlay-image/

## Build

To simply cross-assemble:

    make all

The assembled artifacts are available in the `dist/example-app_0.1` folder.

To generate a disk image:

    make d64

The final artifact is `dist/example-app_0.1.d64`.

## Run

If using real hardware, burn the `.d64` to a floppy. Boot up C64 OS on one
drive, and put your floppy in the other drive.

If using emulation, the Makefile can mount the `.d64` on drive #8 and boot
C64 OS from drive #9:

    make run

> Tip: Press Alt+M to let VICE "capture" your mouse and the same keystroke to
> release it back to the host OS.

The floppy contains the `main.o` and `menu.m` objects. You'll need to install
these as an application. See the programmers guide for more info:

https://c64os.com/c64os/programmersguide/devenvironment

## TODO

* [x] cross-assemble the borderflash example.
* [x] integrate VICE for testing.
* [x] incorporate C64 OS includes.
* [ ] research toolkit, add basic window controls.
* [ ] research menus, tooling for building `.m` files.
* [ ] generate `.car` files. burn these to disk instead of objects.
* [ ] generate `menu.m` files from something like `.toml`?
* [ ] generate `.d71`, `.d81`, and `.t64` images?
* [ ] research libraries, add an example.
* [ ] research applications vs utilities, showcase both.
* [ ] set up CookieCutter template so people can quick-init projects.
* [ ] `cmake` example with multi-binary/multi-library projects?
* [ ] research drivers, write an example driver?
