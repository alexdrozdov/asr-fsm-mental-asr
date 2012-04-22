/*
 * input_manager.h
 *
 *  Created on: 31.07.2011
 *      Author: drozdov
 */

#ifndef INPUT_MANAGER_H_
#define INPUT_MANAGER_H_

#include <iostream>
#include <string>

#include <tcl8.5/tcl.h>

#include "base_input.h"

class CInputManager {
public:
	CInputManager();
	int open();
	int read(int* buf, int samples);
	int close();

	bool is_opened() const;
	std::string get_driver_name();
	unsigned int get_samplerate();
	bool set_samplerate(unsigned int samplerate);

	int LoadInputDriver(Tcl_Interp* interp,std::string libname);
private:
	bool library_loaded;
	void* libhandle;
	bool opened;
	std::string library_name;
	std::string driver_name;
	std::string init_func_name;

	dynamiclib_init *dl_init;
};

extern CInputManager *inpm;

#endif /* INPUT_MANAGER_H_ */
