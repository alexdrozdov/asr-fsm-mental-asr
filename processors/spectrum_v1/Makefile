CCP=g++
CCC=gcc
CFLAGS=-Wall -c -g -fPIC
CF_TCL_H=-I ../../../tcl8.5.9/generic/ \
         -I ../../../libxml2-2.7.8/include \
         -I ../../

LDFLAGS=-shared \
        -L ../../../tcl8.5.9/unix/ \
        -L ../../../libxml2-2.7.8/.libs/ \
        -L ../../xml_support/obj/ \
        -ltcl8.5 -lxml2 -lpthread -lxmlsup -lm 

SRCS=   spectrum_processor.cpp	
OBJS:=$(SRCS:%.cpp=./obj/%.o)

PROG=libspectrum_v1.so
BUILD_DIR=./obj

all:$(BUILD_DIR)/$(PROG)

$(BUILD_DIR)/$(PROG): dirs $(OBJS)
	@echo [LD] $(PROG); \
	$(CCP) $(OBJS) $(LDFLAGS) -o $(BUILD_DIR)/$(PROG)
	@cp $(BUILD_DIR)/$(PROG) ../../../bin/

$(BUILD_DIR)/%.o: %.cpp
	@echo [CC] $< ; \
	$(CCP) $(CFLAGS) $(CF_TCL_H) -o $@ -c $< ;
	
dirs: FORCE
	-@if [ ! -d $(BUILD_DIR) ]; then mkdir $(BUILD_DIR); fi

	
FORCE:

clean:
	rm -rf $(BUILD_DIR)