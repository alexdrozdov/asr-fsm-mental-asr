/*
 * input_manager.cpp
 *
 *  Created on: 31.07.2011
 *      Author: drozdov
 */


#include <dlfcn.h>

#ifdef AUXPACKAGES
#include <tcl.h>
#else
#include <tcl8.5/tcl.h>
#endif

#include "input_manager.h"
#include "mental_asr.h"

#include "common.h"

using namespace std;

#ifdef MACOSX

#define LIB_EXT ".dylib"
#define LIB_EXT_LEN 6

#else

#define LIB_EXT ".so"
#define LIB_EXT_LEN 3

#endif

CInputManager::CInputManager() {
	library_loaded = false;
	opened = false;
	libhandle = 0;

	dl_init = NULL;
}

int CInputManager::open() {
	if (!library_loaded) {
		cout << "CInputManager::open() error: no input library loaded" << endl;
		return 1;
	}
	if (NULL == dl_init->open) {
		cout << "CInputManager::open() warning: input library doesn`t supply open function" << endl;
		return 0;
	}

	int r = dl_init->open();
	if (0 == r) {
		opened = true;
	}
	return r;
}

int CInputManager::read(int* buf,int samples) {
	if (opened) {
		return dl_init->read(buf,samples);
	}
	return 1;
}

int CInputManager::close() {
	if (!library_loaded) {
		cout << "CInputManager::close() error: no input library loaded" << endl;
		return 1;
	}
	if (!opened) {
		return 0;
	}
	if (NULL == dl_init->close) {
		cout << "CInputManager::close() warning: input library doesn`t supply close function" << endl;
		return 0;
	}

	int r = dl_init->close();
	if (0 == r) {
		opened = false;
	}
	return r;
}

bool CInputManager::is_opened() const {
	return opened;
}

typedef int (*inputdrv_init_proc)(dynamiclib_init* dl_init);

int CInputManager::LoadInputDriver(Tcl_Interp* interp,std::string libname) {
	if ('.' == libname[0]) {
		libname = libname.substr(1);
	}
	if ('/' == libname[0]) {
		libname = libname.substr(1);
	}

	if (0 != libname.compare(libname.size()-LIB_EXT_LEN,LIB_EXT_LEN, LIB_EXT)) {
		cout << "CInputManager::LoadInputDriver error: library name " << libname << "couldn`t be used because extension '" << LIB_EXT << "' is missing" << endl;
		return 1;
	}

	driver_name = libname.substr(3,libname.length()-3-LIB_EXT_LEN);

	library_name = build_file_path(libname);
	cout << "Loading library " << library_name << endl;
	init_func_name = "inpdrv_init";

	dlerror();
	libhandle = dlopen(library_name.c_str(),RTLD_LAZY);
	if (0 == libhandle) {
		cout << "CInputManager::LoadInputDriver error: couldn`t load library" << endl;
		char* msg = dlerror();
		if (NULL != msg) {
			cout << "Error was: " << msg << endl;
		}
		return 1;
	}

	inputdrv_init_proc inpdrv_init = (inputdrv_init_proc)dlsym(libhandle,init_func_name.c_str());
	if (NULL == inpdrv_init) {
		cout << "CInputManager::LoadInputDriver error: couldn`t find symbol " << init_func_name << " in library" << endl;
		dlclose(libhandle);
		return 1;
	}

	delete dl_init;

	try {
		dl_init = new dynamiclib_init;
		dl_init->ck_size = sizeof(dynamiclib_init);
		if (0 != inpdrv_init(dl_init)) {
			cout << "CInputManager::LoadInputDriver error - функция инициализации внешней библиотеки вернула ошибку" << endl;
			dlclose(libhandle);
			return 2;
		}

		dl_init->tcl_init(interp);

		library_loaded = true;
	} catch (...) {
		return 1;
	}
	return 0;
}

std::string CInputManager::get_driver_name() {
	if (library_loaded) {
		return driver_name;
	}
	return "stdin";
}

unsigned int CInputManager::get_samplerate() {
	if (library_loaded && dl_init->get_samplerate!=NULL)
		return (unsigned int)dl_init->get_samplerate();

	return 0;
}

bool CInputManager::set_samplerate(unsigned int samplerate) {
	if (!library_loaded || NULL==dl_init->set_samplerate)
		return false;

	if (0 == dl_init->set_samplerate((int)samplerate))
		return true;

	return false;
}

CInputManager *inpm = NULL;


