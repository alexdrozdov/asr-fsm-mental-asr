/*
 * processor_loader.cpp
 *
 *  Created on: 03.08.2011
 *      Author: drozdov
 */

#include <dlfcn.h>

#include <iostream>
#include "processor_loader.h"
#include "asr_core.h"

using namespace std;

extern string executable_path;

map<std::string,proc_create_proc> load_processor_handlers;

typedef int (*processor_init_proc)(dynamicproc_init* dp_init);

int load_processor_lib(std::string name, std::string libname) {
	if ('.' == libname[0]) {
		libname = libname.substr(1);
	}
	if ('/' == libname[0]) {
		libname = libname.substr(1);
	}

	if (0 != libname.compare(0,3,"lib")) {
		cout << "load_processor_lib error: library name " << libname << "couldn`t be used because prefix 'lib' is missing" << endl;
		return 1;
	}
	if (0 != libname.compare(libname.size()-3,3,".so")) {
		cout << "load_processor_lib error: library name " << libname << "couldn`t be used because extension '.so' is missing" << endl;
		return 1;
	}

	string driver_name = libname.substr(3,libname.length()-6);

	string library_name = executable_path + libname;
	cout << "Loading library " << library_name << endl;
	string init_func_name = "asr_proccessor_init";

	dlerror();
	void* libhandle = dlopen(library_name.c_str(),RTLD_LAZY);
	if (0 == libhandle) {
		cout << "load_processor_lib error: couldn`t load library" << endl;
		char* msg = dlerror();
		if (NULL != msg) {
			cout << "Error was: " << msg << endl;
		}
		return 2;
	}

	processor_init_proc pr_init_ptr = (processor_init_proc)dlsym(libhandle,init_func_name.c_str());
	if (NULL == pr_init_ptr) {
		cout << "load_processor_lib error: couldn`t find symbol " << init_func_name << " in library" << endl;
		dlclose(libhandle);
		return 2;
	}

	dynamicproc_init di;
	di.ck_size = sizeof(dynamicproc_init);

	if (0 != pr_init_ptr(&di)) {
		return 2;
	}

	proc_init_environ pie;
	pie.ck_size = sizeof(proc_init_environ);
	pie.asr = asr;

	if (0 != di.core_init(&pie)) {
		cout << "load_processor_lib error: couldn`t execute core init proc" << endl;
		dlclose(libhandle);
		return 2;
	}

	load_processor_handlers[name] = (proc_create_proc)di.create;
	return 0;
}
