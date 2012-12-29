CFLAGS=-Wall -c -g

OS=$(shell uname -s)
ifeq ($(OS),Darwin)
	CFLAGS_AUX= `pkg-config --cflags libxml-2.0` \
          -I ./xml_support/ \
          -I ../../aux-packages/tcl8.5.9/generic/ \
          -I ../../aux-packages/build/include/ \
          -DMACOSX -DAUXPACKAGES
    install_targets=install.macos
    PROTOC_PATH=$(shell pwd)/../../aux-packages/build/bin/
    
    LDFLAGS=-ltcl8.5 \
        -lpthread \
        -ldl \
        -L ./xml_support/obj/ -lxmlsup  \
        -L ../../aux-packages/build/lib/ -lprotobuf \
        -rdynamic
else
ifeq ($(AUXBUILD),AUX)
	CFLAGS_AUX= `pkg-config --cflags libxml-2.0` \
          -I ../../aux-packages/tcl8.5.9/generic/ \
          -I ../../aux-packages/build/include/ \
          -I ./xml_support/ \
          -DGNULINUX -DAUXPACKAGES
    PROTOC_PATH=$(shell pwd)/../../aux-packages/build/bin/
    
    LDFLAGS=-ltcl8.5 \
        -lpthread \
        -ldl \
        -L ./xml_support/obj/ -lxmlsup  \
        -L ../../aux-packages/build/lib/ -lprotobuf \
        -rdynamic
else
    CFLAGS_AUX= `pkg-config --cflags libxml-2.0` \
          `pkg-config --cflags protobuf` \
          -I ./xml_support/ \
          -DGNULINUX
    
    LDFLAGS=-ltcl8.5 \
        -lpthread \
        -ldl \
        -L ./xml_support/obj/ -lxmlsup  \
        `pkg-config --libs protobuf` \
        -rdynamic
endif
	install_targets=install.gnulinux
endif

CCP=g++
CCC=gcc
PROTOC=$(PROTOC_PATH)protoc


CCP=g++
CCC=gcc
PROTOC=$(PROTOC_PATH)protoc

PROG=_mental_asr.bin
BUILD_DIR=./obj

SRCS=$(wildcard *.cpp)
OBJS:=$(SRCS:%.cpp=$(BUILD_DIR)/%.o)

PROTO=$(wildcard *.proto)
PROTO_CC=$(PROTO:%.proto=%.pb.cc)
PROTO_OBJ=$(PROTO_CC:%.cc=$(BUILD_DIR)/%.o)

all:$(BUILD_DIR)/$(PROG) wav_input spectrum_v1 wavelet_v1 $(install_targets)

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
	@install_name_tool -change /usr/local/lib/libprotobuf.7.dylib  @executable_path/libs/libprotobuf.7.dylib $(BUILD_DIR)/$(PROG)
	@cp $(BUILD_DIR)/$(PROG) ../bin/
	@echo Done


wav_input: FORCE
	@$(MAKE) -C ./wav_input/ AUXBUILD=$(AUXBUILD)

spectrum_v1 : FORCE xmlsup
	@$(MAKE) -C ./processors/spectrum_v1/ AUXBUILD=$(AUXBUILD)
	
wavelet_v1 : FORCE xmlsup
	@$(MAKE) -C ./processors/wavelet_v1/ AUXBUILD=$(AUXBUILD)
	
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
	@$(MAKE) clean -C ./processors/wavelet_v1

