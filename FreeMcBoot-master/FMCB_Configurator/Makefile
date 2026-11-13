EE_BIN = BOOT.ELF
EE_OBJS = main.o pad.o config.o elf.o draw.o loader.o  filer.o\
	icon_sys.o icon_icn.o \
	timer.o \
	font_uLE.o \
	cn_font.o cn_pinyin.o cn_im.o cn_gbk.o \
	iomanx_irx.o filexio_irx.o ps2dev9_irx.o ps2atad_irx.o ps2hdd_irx.o ps2fs_irx.o

EE_INCS := -I$(PS2DEV)/gsKit/include -I$(PS2DEV)/libjpg/include\
	-I$(PS2SDK)/sbv/include -I$(PS2DEV)/libcdvd/ee

EE_LDFLAGS := -L$(PS2DEV)/gsKit/lib -L$(PS2DEV)/libjpg\
	-L$(PS2SDK)/sbv/lib -L$(PS2DEV)/libcdvd/lib -s
EE_LIBS = -lfileXio -lpad -lgskit -ldmakit -lmc -lmf -lpatches -ldebug -lc

all:	$(EE_BIN)

run: comp
	ps2client -h 192.168.1.4 -t 1 execee host:FMCB_CFG.ELF
reset: clean
	ps2client -h 192.168.1.4 reset
comp: all
	ps2-packer BOOT.ELF FMCB_CFG.ELF

loader.s:
	$(MAKE) -C loader
	bin2s loader/loader.elf loader.s loader_elf

icon_sys.s:
	bin2s icons/icon.sys icon_sys.s icon_sys
icon_icn.s:
	bin2s icons/FMCB.icn icon_icn.s icon_icn

iomanx_irx.s:
	bin2s $(PS2SDK)/iop/irx/iomanX.irx iomanx_irx.s iomanx_irx
filexio_irx.s:
	bin2s $(PS2SDK)/iop/irx/fileXio.irx filexio_irx.s filexio_irx
ps2dev9_irx.s:
	bin2s $(PS2SDK)/iop/irx/ps2dev9.irx ps2dev9_irx.s ps2dev9_irx
ps2atad_irx.s:
	bin2s $(PS2SDK)/iop/irx/ps2atad.irx ps2atad_irx.s ps2atad_irx
ps2hdd_irx.s:
	bin2s $(PS2SDK)/iop/irx/ps2hdd.irx ps2hdd_irx.s ps2hdd_irx
ps2fs_irx.s:
	bin2s $(PS2SDK)/iop/irx/ps2fs.irx ps2fs_irx.s ps2fs_irx

clean:
	$(MAKE) -C loader clean
	rm -f *.o *.a loader.s icon_sys.s icon_icn.s BOOT.ELF BOOTc.ELF

include $(PS2SDK)/samples/Makefile.pref
include $(PS2SDK)/samples/Makefile.eeglobal
