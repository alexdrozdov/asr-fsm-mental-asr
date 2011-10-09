CCP=g++
CCC=gcc
CFLAGS=-Wall -c -g -fPIC
CF_TCL_H=-I ../../tcl8.5.9/generic/ -I ../../libxml2-2.7.8/include -I ../
LDFLAGS=-shared -L ../../tcl8.5.9/unix/ -ltcl8.5 -L ../../libxml2-2.7.8/.libs/  -lxml2 -lpthread

SRCS=   wav_input.cpp \
        wav_io.cpp
	
OBJS:=$(SRCS:%.cpp=./obj/%.o)

PROG=libwav_input.so
BUILD_DIR=./obj

all:$(BUILD_DIR)/$(PROG)

$(BUILD_DIR)/$(PROG): dirs $(OBJS)
	@echo [LD] $(PROG); \
	$(CCP) $(OBJS) $(LDFLAGS) -o $(BUILD_DIR)/$(PROG)
	@cp $(BUILD_DIR)/$(PROG) ../../bin/

$(BUILD_DIR)/%.o: %.cpp
	@echo [CC] $< ; \
	$(CCP) $(CFLAGS) $(CF_TCL_H) -o $@ -c $< ;
	
dirs: FORCE
	-@if [ ! -d $(BUILD_DIR) ]; then mkdir $(BUILD_DIR); fi

	
FORCE:

clean:
	rm -rf $(BUILD_DIR)