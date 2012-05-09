CCP=g++
CCC=gcc

CFLAGS=-Wall -c -g -fPIC

OS=$(shell uname -s)
ifeq ($(OS),Darwin)
	CF_AUX_FLAGS= `pkg-config --cflags libxml-2.0` \
          -I ../xml_support/ \
          -I ../../../aux-packages/tcl8.5.9/generic/ \
          -DMACOSX -DAUXPACKAGES
    LIB_EXT=dylib
    install_targets=install.macos
    
    LDFLAGS= -shared \
         -lpthread \
         -ltcl8.5 \
         `pkg-config --libs libxml-2.0` \
         -lxmlsup -L ../xml_support/obj/
else
ifeq ($(AUXBUILD),AUX)
	CF_AUX_FLAGS= `pkg-config --cflags libxml-2.0` \
	      -I ../../../aux-packages/tcl8.5.9/generic/ \
	      -I ../../../aux-packages/build/include/ \
          -I ../xml_support/ \
          -DGNULINUX -DAUXPACKAGES
          
    LDFLAGS= -shared \
         -lpthread \
         -ltcl8.5 \
         `pkg-config --libs libxml-2.0` \
         -lxmlsup -L ../xml_support/obj/
else
    CF_AUX_FLAGS= `pkg-config --cflags libxml-2.0` \
          -I ../xml_support/ \
          -DGNULINUX
    
    LDFLAGS= -shared \
         -lpthread \
         -ltcl8.5 \
         `pkg-config --libs libxml-2.0` \
         -lxmlsup -L ../xml_support/obj/
endif
	LIB_EXT=so
    install_targets=install.gnulinux
endif

CF_ASR_FLAGS=-I ../ 

SRCS=$(wildcard *.cpp)
	
OBJS:=$(SRCS:%.cpp=./obj/%.o)

PROG=libwav_input.$(LIB_EXT)
BUILD_DIR=./obj

all:$(BUILD_DIR)/$(PROG) $(install_targets)

$(BUILD_DIR)/$(PROG): dirs $(OBJS)
	@echo [LD] $(PROG); \
	$(CCP) $(OBJS) $(LDFLAGS) -o $(BUILD_DIR)/$(PROG)

$(BUILD_DIR)/%.o: %.cpp
	@echo [CC] $< ; \
	$(CCP) $(CFLAGS) $(CF_ASR_FLAGS) $(CF_AUX_FLAGS) -MD -o $@ -c $< ;

install.gnulinux: FORCE
	@cp $(BUILD_DIR)/$(PROG) ../../bin/libs/
	
install.macos: FORCE
	@install_name_tool -change ./obj/libxmlsup.dylib  @executable_path/libs/libxmlsup.dylib $(BUILD_DIR)/$(PROG)
	@cp $(BUILD_DIR)/$(PROG) ../../bin/libs/

dirs: FORCE
	-@if [ ! -d $(BUILD_DIR) ]; then mkdir $(BUILD_DIR); fi

include $(wildcard $(BUILD_DIR)/*.d) 

FORCE:

clean:
	rm -rf $(BUILD_DIR)