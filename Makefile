CCP=g++
CCC=gcc
PROTOC=protoc
CFLAGS=-Wall -c -g

OS=$(shell uname -s)
ifeq ($(OS),Darwin)
	CFLAGS_AUX= `pkg-config --cflags libxml-2.0` \
          -I ./xml_support/ \
          -I ../../aux-packages/tcl8.5.9/generic/ \
          -DMACOSX
    install_targets=install.macos
else
    CFLAGS_AUX= `pkg-config --cflags libxml-2.0` \
          `pkg-config --cflags protobuf` \
          -I ./xml_support/ \
          -DGNULINUX
    install_targets=install.gnulinux
endif

LDFLAGS=-ltcl8.5 \
        -lpthread \
        -ldl \
        -L ./xml_support/obj/ -lxmlsup  \
        `pkg-config --libs protobuf` \
        -rdynamic

PROG=_mental_asr.bin
BUILD_DIR=./obj

SRCS=$(wildcard *.cpp)
OBJS:=$(SRCS:%.cpp=$(BUILD_DIR)/%.o)

PROTO=$(wildcard *.proto)
PROTO_CC=$(PROTO:%.proto=%.pb.cc)
PROTO_OBJ=$(PROTO_CC:%.cc=$(BUILD_DIR)/%.o)

all:$(BUILD_DIR)/$(PROG) wav_input spectrum_v1 $(install_targets)

$(BUILD_DIR)/$(PROG): dirs xmlsup $(PROTO_CC) $(PROTO_OBJ) $(OBJS)
	@echo [LD] $(PROG); \
	$(CCP) $(OBJS) $(PROTO_OBJ) $(LDFLAGS) -o $(BUILD_DIR)/$(PROG)

$(BUILD_DIR)/%.o: %.cpp
	@echo [CC] $< ; \
	$(CCP) $(CFLAGS) $(CFLAGS_AUX) -MD -o $@ -c $< ;
	
$(BUILD_DIR)/%.o: %.cc
	@echo [CC] $< ; \
	$(CCP) $(CFLAGS) $(CFLAGS_AUX) -MD -o $@ -c $< ;
	
%.pb.cc: %.proto
	@echo [PROTO] $< ; \
	$(PROTOC) -I=./ --cpp_out=./ $< ;

include $(wildcard $(BUILD_DIR)/*.d) 

install.gnulinux: FORCE
	@cp $(BUILD_DIR)/$(PROG) ../bin/
	@echo Done
	
install.macos: FORCE
	@install_name_tool -change ./obj/libxmlsup.dylib  @executable_path/libs/libxmlsup.dylib $(BUILD_DIR)/$(PROG)
	@cp $(BUILD_DIR)/$(PROG) ../bin/
	@echo Done


wav_input: FORCE
	@$(MAKE) -C ./wav_input/

spectrum_v1 : FORCE xmlsup
	@$(MAKE) -C ./processors/spectrum_v1/
	
xmlsup : FORCE
	@$(MAKE) -C ./xml_support/

dirs: FORCE
	-@if [ ! -d $(BUILD_DIR) ]; then mkdir $(BUILD_DIR); fi
	@cp -R ./bin ../

FORCE:

clean:
	rm -rf $(BUILD_DIR) *.pb.cc *.pb.h
	@$(MAKE) clean -C ./wav_input/
	@$(MAKE) clean -C ./xml_support/
	@$(MAKE) clean -C ./processors/spectrum_v1

