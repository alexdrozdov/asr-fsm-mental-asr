/*
 * wav_input.cpp
 *
 *  Created on: 31.07.2011
 *      Author: drozdov
 */

#include <iostream>
#include <string>

#ifdef AUXPACKAGES
#include <tcl.h>
#else
#include <tcl8.5/tcl.h>
#endif

#include "base_input.h"
#include "wav_input.h"
#include "wav_io.h"

using namespace std;

CWavIo* wav_io = NULL;
string wav_name = "";

int wav_input_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]);

int inpdrv_init(dynamiclib_init* dl_init) {
	if (NULL == dl_init) {
		return 1;
	}
	if (dl_init->ck_size != sizeof(dynamiclib_init)) {
		std::cout << "wav_input_init error: supplied dl_init->ck_size differes from local structure size" << std::endl;
		std::cout << "This means, library is incompatible with asr core" << std::endl;
		return 2;
	}
	dl_init->tcl_init  = wavdrv_tcl_init_proc;
	dl_init->core_init = wavdrv_core_init_proc;
	dl_init->open      = wavdrv_open_proc;
	dl_init->read      = wavdrv_read_proc;
	dl_init->close     = wavdrv_close_proc;

	dl_init->get_samplerate = wavdrv_get_samplerate;
	dl_init->set_samplerate = wavdrv_set_samplerate;

	dl_init->asr_minor = 0;
	dl_init->asr_major = 0x00010000;

	return 0;
}

int wavdrv_tcl_init_proc(Tcl_Interp* interp) {
	Tcl_CreateCommand(interp,
			"wav_input",
			wav_input_handler,
			(ClientData) NULL,
			(Tcl_CmdDeleteProc*) NULL
	);
	return 0;
}

int wav_input_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]) {
	if (2 == argc) {
		string cmd = argv[1];
		if ("open" == cmd) {
			if (NULL != wav_io) {
				wav_io->open();
			} else if (wav_name.length()>0){
				wav_io = new CWavIo(wav_name.c_str());
				wav_io->open();
			} else {
				cout << "wav_input_handler error: open failed because no wav file name was specified." << endl;
				cout << "hint: call wav_input name <wav_file_name> first" << endl;
				return TCL_ERROR;
			}
			return TCL_OK;
		}
		if ("close" == cmd) {
			if (NULL != wav_io) {
				wav_io->close();
				delete wav_io;
				wav_io = NULL;
			}
			return TCL_OK;
		}
		if ("samplerate" == cmd) {
			if (NULL != wav_io) {
				cout << wav_io->get_defsamplerate() << endl;
			}
			return TCL_OK;
		}
		if ("bitspersample" == cmd) {
			if (NULL != wav_io) {
				cout << wav_io->get_bitspersample() << endl;
			}
			return TCL_OK;
		}
		if ("length" == cmd) {
			if (NULL != wav_io) {
				cout << wav_io->size() *8 / wav_io->get_bitspersample() << endl;
			}
			return TCL_OK;
		}
		if ("opened" == cmd) {
			if (NULL != wav_io) {
				int i = wav_io->is_opened()?1:0;
				cout << i << endl;
			}
			return TCL_OK;
		}
		if ("getpos" == cmd) {
			if (NULL != wav_io) {
				cout << wav_io->getpos() *8 / wav_io->get_bitspersample() << endl;
			}
			return TCL_OK;
		}
	}
	if (3 == argc) {
		string cmd = argv[1];
		string opt = argv[2];

		if ("name" == cmd) {
			if (NULL != wav_io) {
				wav_io->close();
				delete wav_io;
			}
			wav_name = opt;
			wav_io = new CWavIo(wav_name);
			return TCL_OK;
		}
	}
	cout << "wav_input_handler error: wrong options" << endl;
	return TCL_ERROR;
}

int wavdrv_core_init_proc() {
	return 0;
}

int wavdrv_open_proc() {
	if (NULL != wav_io) {
		return wav_io->open();
	}
	return 0;
}

int wavdrv_read_proc(int* buf,int n) {
	if (NULL == wav_io) {
		return -1;
	}

	switch (wav_io->get_bitspersample()) {
		case 16:
			{
				short* tmp_ptr = new short[n];
				//cout << "dsfsd" << endl;
				unsigned nn = wav_io->read((unsigned char*)tmp_ptr,n*2);
				nn /= 2; //Определяем количество считанных выборок
				for (unsigned ii=0;ii<nn;ii++) {
					buf[ii] = tmp_ptr[ii];
				}
				delete[] tmp_ptr;
				return nn;
			}
		case 8:
			{
				char* tmp_ptr = new char[n];
				unsigned nn = wav_io->read((unsigned char*)tmp_ptr,n);
				for (unsigned ii=0;ii<nn;ii++) {
					buf[ii] = tmp_ptr[ii];
				}
				delete[] tmp_ptr;
				return nn;
			}
		default:
			cout << "wavdrv_read_proc error: unsupported bits per sample" << endl;
			return 0;
	}

	return 0;
}

int wavdrv_close_proc() {
	if (NULL != wav_io) {
		wav_io->close();
	}
	return 0;
}

int wavdrv_get_samplerate() {
	if (NULL == wav_io)
		return 0;

	return wav_io->get_defsamplerate();
}

int wavdrv_set_samplerate(int samplerate) {
	//FIXME Реализовать преобразование частоты
	return 1;
}

