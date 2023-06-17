# C64 OS Example App

This is a (work in progress) project template set up to cross-assemble for the
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

**Unix Tools**

You'll need to be able to execute `Makefile`s. I use GNU Make but any
POSIX-compliant `Makefile` runner should do.

We also depend on a few standard UNIX tools: `cp`, `rm`, `mkdir`,
`false`, `install`, `chmod`, `unzip`, and `wget`.

**Python Tools**

Python is used to translate between some file formats and encodings. I suggest
version 3.8 or newer (I use 3.10).

https://www.python.org/

You'll also need Python's `venv` module, which usually ships with a standard
installation. All the other Python dependencies get installed in a virtual
environment behind the scenes by the `Makefile` (you do not need to install
them on your system).

**Cross-Assembler**

The cross-assembler is TMPx - Turbo Macro Pro (Cross).

https://style64.org/release/tmpx-v1.1.0-style

You do not need to download this. The Makefile will automatically download it
on first run.

Greg uses TMP, which means all the OS includes use TMP syntax.

**Emulator (VICE)**

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

> Tip: You might have the 1.0 DHD. The headers are for 1.03. It is recommended
> that you undergo an update procedure on your disk image.

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

    make

The assembled artifacts are available in the `dist/example-app_0.1` folder.

To generate a disk image:

    make d64

The final artifact is `dist/example-app_0.1.d64`.

To view all available build targets:

    make help

## Run

If using real hardware, burn the artifact to a floppy. Boot up C64 OS on one
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
* [x] research menus, tooling for building `.m` files.
* [ ] generate `.car` files. burn these to disk instead of objects.
* [x] generate `menu.m` files from `.json`
* [x] generate `about.t` files from metadata
* [ ] generate `.d71`, `.d81`, and `.t64` images?
* [ ] research libraries, add an example.
* [ ] research applications vs utilities, showcase both.
* [ ] set up CookieCutter template so people can quick-init projects.
* [ ] `cmake` example with multi-binary/multi-library projects?
* [ ] research drivers, write an example driver?
