APP_NAME := example-app
APP_VERSION := 0.1
APP_FULLNAME := $(APP_NAME)_$(APP_VERSION)
APP_AUTHOR := $(USER)

BINDIR := ./bin
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

.PHONY: clean all package d64 run help

package: all $(DISTDIR) $(DISTDIR)/$(APP_FULLNAME)/
	cp -t $(DISTDIR)/$(APP_FULLNAME)/ $(OBJ)

all: $(ASM) $(OUTDIR) $(OBJ)

d64: package
	$(C1541EMU) -format $(APP_NAME),8 d64 $(DISTDIR)/$(APP_FULLNAME).d64 \
	  -attach $(DISTDIR)/$(APP_FULLNAME).d64 \
	  -write $(DISTDIR)/$(APP_FULLNAME)/about.t about.t \
	  -write $(DISTDIR)/$(APP_FULLNAME)/main.o main.o \
	  -write $(DISTDIR)/$(APP_FULLNAME)/menu.m menu.m

$(C64OS_DHD):
	@echo "You must provide a C64 OS disk image. See README.md for more info."
	false

$(CMDHD_ROM):
	@echo "You must provide a CMD HD Boot ROM. See README.md for more info."
	false

$(ASM):
	rm -rf /tmp/$(TMPX_VERSION)
	wget https://style64.org/file/$(TMPX_VERSION).zip -P /tmp/$(TMPX_VERSION)
	unzip /tmp/$(TMPX_VERSION)/$(TMPX_VERSION).zip -d /tmp/$(TMPX_VERSION)
	install -D /tmp/$(TMPX_VERSION)/$(TMPX_VERSION)/$(TMPX_ARCH)/tmpx $(ASM)
	rm -rf /tmp/$(TMPX_VERSION)
	chmod +x $(ASM)

$(OUTDIR)/about.t:
	$(PYTHON) -m poetry run ./scripts/generate/about.t.py "$(APP_NAME)" "$(APP_VERSION)" "$(APP_AUTHOR)" > $@


$(OUTDIR)/menu.m: $(SRCDIR)/menu.json
	$(PYTHON) -m poetry run ./scripts/generate/menu.m.py $< > $@

$(OUTDIR)/%.o: $(SRCDIR)/%.s
	$(ASM) $(ASMFLAGS) -i $< -o $@

$(OUTDIR)/c64os.dhd: $(C64OS_DHD)
	cp $(C64OS_DHD) $(OUTDIR)/c64os.dhd

$(OUTDIR):
	mkdir -p $@

$(DISTDIR):
	mkdir -p $@

$(DISTDIR)/$(APP_FULLNAME)/:
	mkdir -p $@

clean:
	rm -rf $(OUTDIR) $(DISTDIR)

run: d64 $(OUTDIR)/c64os.dhd $(CMDHD_ROM)
	$(C64EMU) -default \
	  $(C64EMU_ROMFLAGS) $(C64EMU_EXTRAFLAGS) \
	  $(C64EMU_MOUNTFLAGS) -keybuf "$(C64EMU_BOOTCMD)"

help:
	@echo "all: build all object files"
	@echo "package: build re-distributable artifacts"
	@echo "d64: create a disk image artifact (requires VICE)"
	@echo "clean: delete all objects and artifacts"
	@echo "run: run the application in emulation (requires VICE)"
	@echo "help: show this help text"