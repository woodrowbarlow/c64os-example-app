APP_NAME := example-app
APP_VERSION := 0.1
APP_FULLNAME := $(APP_NAME)_$(APP_VERSION)
APP_AUTHOR := $(USER)

BINDIR := ./bin
VENVDIR := ./.env
UTILDIR := ./c64util
ROMDIR := ./rom
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
JD_1541_ROM := $(ROMDIR)/JiffyDOS_1541-II.bin

C64EMU_EXTRAFLAGS := -controlport1device 3
C64EMU_ROMFLAGS := -kernal $(JD_KERNAL_ROM) -dos1541II $(JD_1541_ROM) -dosCMDHD $(CMDHD_ROM)
C64EMU_MOUNTFLAGS := -drive8type 1542 -drive9type 4844 -8 $(DISTDIR)/$(APP_FULLNAME).d64 -9 $(OUTDIR)/c64os.dhd
C64EMU_BOOTCMD := load \"c64os\",9\nrun\n

.PHONY: download dist d64 clean clean-dl run help

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

$(ASM):
	rm -rf /tmp/$(TMPX_VERSION)
	wget https://style64.org/file/$(TMPX_VERSION).zip -P /tmp/$(TMPX_VERSION)
	unzip /tmp/$(TMPX_VERSION)/$(TMPX_VERSION).zip -d /tmp/$(TMPX_VERSION)
	install -D /tmp/$(TMPX_VERSION)/$(TMPX_VERSION)/$(TMPX_ARCH)/tmpx $@
	rm -rf /tmp/$(TMPX_VERSION)
	chmod +x $@

$(OUTDIR):
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

$(OUTDIR)/c64os.dhd: $(C64OS_DHD)
	cp $< $@

$(DISTDIR)/$(APP_FULLNAME).d64: $(DISTDIR)/$(APP_FULLNAME)
	$(C1541EMU) -format $(APP_NAME),8 d64 $@ \
	  -attach $@ \
	  -write $(DISTDIR)/$(APP_FULLNAME)/about.t about.t \
	  -write $(DISTDIR)/$(APP_FULLNAME)/main.o main.o \
	  -write $(DISTDIR)/$(APP_FULLNAME)/menu.m menu.m

clean:
	rm -rf $(OUTDIR) $(DISTDIR)

clean-dl: clean
	rm -rf $(BINDIR) $(VENVDIR)

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
	@echo "  help: show this help text"
	@echo "the default target is 'dist'."