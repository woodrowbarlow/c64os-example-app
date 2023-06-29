APP_NAME := example-app
APP_VERSION := 0.1
APP_FULLNAME := $(APP_NAME)_$(APP_VERSION)
APP_AUTHOR := $(USER)

BINDIR := ./bin
VENVDIR := ./.env
UTILDIR := ./c64util
ROMDIR := ./rom
DLDIR := ./dl
SRCDIR := ./src
INCDIR := ./inc
OUTDIR := ./out
DISTDIR := ./dist

OBJ := $(OUTDIR)/main.o $(OUTDIR)/menu.m $(OUTDIR)/about.t

PYTHON := python

ASM := $(BINDIR)/tmpx
ASMFLAGS := -I $(INCDIR)

TMPX_VERSION = TMPx_v1.1.0-STYLE
TMPX_ARCH = linux-x86_64

C64EMU := x64sc
C1541EMU := c1541

C64OS_DHD := $(ROMDIR)/c64os.dhd
CMDHD_ROM := $(ROMDIR)/cmd_hd_bootrom.bin
JD_KERNAL_ROM := $(ROMDIR)/JiffyDOS_C64.bin

C64EMU_EXTRAFLAGS := -controlport1device 3 -fslongnames
C64EMU_ROMFLAGS := -kernal $(JD_KERNAL_ROM) -dosCMDHD $(CMDHD_ROM)
C64EMU_MOUNTFLAGS := -iecdevice8 -drive8type 0 -drive9type 4844 -fs8 $(DISTDIR) -9 $(OUTDIR)/c64os.dhd
C64EMU_UPDATE_MOUNTFLAGS := -drive8type 1581 -drive9type 4844 -8 $(DISTDIR)/updates-disk.d81 -9 $(OUTDIR)/c64os.dhd
C64EMU_BOOTCMD := load \"c64os\",9\nrun\n

C64OS_UPDATES := $(DLDIR)/updates/1.01.update.car $(DLDIR)/updates/1.02.update.car $(DLDIR)/updates/1.03.update.car $(DLDIR)/updates/1.04.upd1.03.car
C64OS_SOFTWARE := $(DLDIR)/software/cgfxsamples1.car $(DLDIR)/software/petsciibots.car $(DLDIR)/software/backdrops1.car

.PHONY: download dist d64 clean clean-dl update run help

dist: $(DISTDIR)/$(APP_FULLNAME).car
download: $(ASM) $(VENVDIR)
d64: $(DISTDIR)/$(APP_FULLNAME).d64

$(C64OS_DHD):
	@echo "You must provide a C64 OS disk image. See README.md for more info."
	false

$(CMDHD_ROM):
	@echo "You must provide a CMD HD Boot ROM. See README.md for more info."
	false

$(VENVDIR):
	$(PYTHON) -m venv $(VENVDIR)
	$(VENVDIR)/bin/pip install -r ./requirements.txt

$(DLDIR)/$(TMPX_VERSION): $(DLDIR)
	wget https://style64.org/file/$(TMPX_VERSION).zip -P $(DLDIR)
	unzip $(DLDIR)/$(TMPX_VERSION).zip -d $(DLDIR)/$(TMPX_VERSION)

$(DLDIR)/updates/%.car: $(DLDIR)/updates
	rm -f $@
	wget https://s3.amazonaws.com/com.c64os.resources/c64os/software_updates/$(notdir $@) -P $<

$(DLDIR)/software/%.car: $(DLDIR)/software
	rm -f $@
	wget https://s3.amazonaws.com/com.c64os.resources/c64os/software_installs/$(notdir $@) -P $<

$(ASM): $(DLDIR)/$(TMPX_VERSION)
	install -D $</$(TMPX_VERSION)/$(TMPX_ARCH)/tmpx $@
	chmod +x $@

$(OUTDIR):
	mkdir -p $@

$(DLDIR):
	mkdir -p $@

$(DLDIR)/updates:
	mkdir -p $@

$(DLDIR)/software:
	mkdir -p $@

$(OUTDIR)/%.o: $(SRCDIR)/%.s $(ASM) $(OUTDIR)
	$(ASM) $(ASMFLAGS) -i $< -o $@

$(OUTDIR)/about.t: $(VENVDIR)
	$(VENVDIR)/bin/python $(UTILDIR)/gen_meta.py -a "$(APP_AUTHOR)" "$(APP_NAME)" "$(APP_VERSION)" > $@

$(OUTDIR)/menu.m: $(SRCDIR)/menu.json $(VENVDIR)
	$(VENVDIR)/bin/python $(UTILDIR)/gen_menu.py $< > $@

$(DISTDIR)/$(APP_FULLNAME): $(OBJ)
	mkdir -p $@
	cp -t $@ $?

$(DISTDIR)/$(APP_FULLNAME).car: $(DISTDIR)/$(APP_FULLNAME) $(VENVDIR)
	$(VENVDIR)/bin/python $(UTILDIR)/gen_car.py $</* > $@

$(OUTDIR)/c64os.dhd: $(C64OS_DHD) $(OUTDIR)
	cp $< $@

$(DISTDIR)/$(APP_FULLNAME).d64: $(DISTDIR)/$(APP_FULLNAME)
	$(C1541EMU) -format $(APP_NAME),8 d64 $@ \
	  -attach $@ \
	  -write $(DISTDIR)/$(APP_FULLNAME)/about.t about.t \
	  -write $(DISTDIR)/$(APP_FULLNAME)/main.o main.o \
	  -write $(DISTDIR)/$(APP_FULLNAME)/menu.m menu.m

$(DISTDIR)/updates-disk.d81: $(C64OS_UPDATES)
	mkdir -p $(DISTDIR)
	$(C1541EMU) -format c64os-updates,8 d81 $@ \
	  -attach $@ \
	  -write $(DLDIR)/updates/1.01.update.car 1.01.update.car \
	  -write $(DLDIR)/updates/1.02.update.car 1.02.update.car \
	  -write $(DLDIR)/updates/1.03.update.car 1.03.update.car \
	  -write $(DLDIR)/updates/1.04.upd1.03.car 1.04.upd1.03.car

$(DISTDIR)/software-disk.d81: $(C64OS_SOFTWARE)
	mkdir -p $(DISTDIR)
	$(C1541EMU) -format c64os-updates,8 d81 $@ \
	  -attach $@ \
	  -write $(DLDIR)/software/cgfxsamples1.car cgfxsamples1.car \
	  -write $(DLDIR)/software/petsciibots.car petsciibots.car \
	  -write $(DLDIR)/software/backdrops1.car backdrops1.car

clean:
	rm -rf $(OUTDIR) $(DISTDIR) $(DLDIR)

update: $(DISTDIR)/updates-disk.d81 $(OUTDIR)/c64os.dhd $(CMDHD_ROM)
	$(C64EMU) -default \
	  $(C64EMU_ROMFLAGS) $(C64EMU_EXTRAFLAGS) \
	  $(C64EMU_UPDATE_MOUNTFLAGS) -keybuf "$(C64EMU_BOOTCMD)"

run: d64 $(OUTDIR)/c64os.dhd $(CMDHD_ROM)
	$(C64EMU) -default \
	  $(C64EMU_ROMFLAGS) $(C64EMU_EXTRAFLAGS) \
	  $(C64EMU_MOUNTFLAGS) -keybuf "$(C64EMU_BOOTCMD)"

help:
	@echo "supported targets:"
	@echo "  download: download all dependencies (for offline build)"
	@echo "  dist: build re-distributable artifacts"
	@echo "  d64: create a .d64 disk image (requires VICE)"
	@echo "  clean: delete all objects and artifacts"
	@echo "  clean-dl: as above, plus delete all downloaded dependencies (not ROMs)"
	@echo "  run: run the application in emulation (requires VICE)"
	@echo "  update: boot in emulation with a disk containing OS updates (requires VICE)"
	@echo "  help: show this help text"
	@echo "the default target is 'dist'."