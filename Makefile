CCP=g++
CCC=gcc
CFLAGS=-Wall -c -g
CF_TCL_H=-I ../tcl8.5.9/generic/ -I ../libxml2-2.7.8/include
LDFLAGS=-L ../tcl8.5.9/unix/ -ltcl8.5 -L ../libxml2-2.7.8/.libs/  -lxml2 -lpthread -dl -L ./xml_support/obj/ -lxmlsup 

SRCS=   main.cpp \
        netlink_pack.cpp \
        crc.cpp \
        mental_asr.cpp \
        asr_core.cpp \
        input_manager.cpp \
        processor_loader.cpp

OBJS:=$(SRCS:%.cpp=./obj/%.o)

PROG=mental_asr.bin
BUILD_DIR=./obj

all:$(BUILD_DIR)/$(PROG)

$(BUILD_DIR)/$(PROG): dirs $(OBJS) wav_input spectrum_v1 xmlsup
	@echo [LD] $(PROG); \
	$(CCP) $(OBJS) $(LDFLAGS) -o $(BUILD_DIR)/$(PROG)
	@cp $(BUILD_DIR)/$(PROG) ../bin/
	@echo Done


$(BUILD_DIR)/%.o: %.cpp
	@echo [CC] $< ; \
	$(CCP) $(CFLAGS) $(CF_TCL_H) -o $@ -c $< ;

wav_input: FORCE
	@$(MAKE) -C ./wav_input/

spectrum_v1 : FORCE xmlsup
	@$(MAKE) -C ./processors/spectrum_v1/
	
xmlsup : FORCE
	@$(MAKE) -C ./xml_support/

dirs: FORCE
	-@if [ ! -d $(BUILD_DIR) ]; then mkdir $(BUILD_DIR); fi

FORCE:

clean:
	rm -rf $(BUILD_DIR)
	@$(MAKE) clean -C ./wav_input/
	@$(MAKE) clean -C ./xml_support/
	@$(MAKE) clean -C ./processors/spectrum_v1

