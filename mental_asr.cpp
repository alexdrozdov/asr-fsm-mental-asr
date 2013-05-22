/*
 * mental_asr.cpp
 *
 *  Created on: 30.07.2011
 *      Author: drozdov
 */

#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fts.h>

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>

#ifdef AUXPACKAGES
#include <tcl.h>
#else
#include <tcl8.5/tcl.h>
#endif

#include "common.h"

#include "mental_asr.h"
#include "asr_core.h"
#include "base_processor.h"
#include "xml_support/xml_support.h"
#include "input_manager.h"
#include "processor_loader.h"
#include "p2vera_dsp.h"
#include "p2vera_control.h"
#include "tclinterp_stream.h"

using namespace std;

int loadproc_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]);
int p2vera_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]);
int mkdump_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]);
int process_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]);
int inpdrv_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]);
int proclib_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]);

int load_processors(Tcl_Interp* interp, std::string foldername);
int init_loadproc_handlers(Tcl_Interp* interp);
int create_tcl_handlers (Tcl_Interp *interp);
std::string extract_processor_type(string filename);


int init_asr_structs(Tcl_Interp *interp) {
	Tcl_SetVar(interp, "mental_asr(executable)", executable_path.c_str(), TCL_GLOBAL_ONLY);
	Tcl_SetVar(interp, "mental_asr(project)", project_path.c_str(), TCL_GLOBAL_ONLY);
	Tcl_SetVar(interp, "mental_asr(loaded)", "0",TCL_GLOBAL_ONLY);

	create_tcl_handlers(interp);
	asr = new CAsrCore();
	inpm = new CInputManager();

	init_loadproc_handlers(interp);

	load_processors(interp, project_path + "processors/");

	Tcl_SetVar(interp, "mental_asr(loaded)", "1",TCL_GLOBAL_ONLY);

	return TCL_OK;
}

int create_tcl_handlers (Tcl_Interp *interp) {
	Tcl_CreateCommand(interp,
			"loadproc",
			loadproc_handler,
			(ClientData) NULL,
			(Tcl_CmdDeleteProc*) NULL
	);

	Tcl_CreateCommand(interp,
			"p2vera",
			p2vera_handler,
			(ClientData) NULL,
			(Tcl_CmdDeleteProc*) NULL
	);

	Tcl_CreateCommand(interp,
			"mkdump",
			mkdump_handler,
			(ClientData) NULL,
			(Tcl_CmdDeleteProc*) NULL
	);

	Tcl_CreateCommand(interp,
			"process",
			process_handler,
			(ClientData) NULL,
			(Tcl_CmdDeleteProc*) NULL
	);

	Tcl_CreateCommand(interp,
			"inpdrv",
			inpdrv_handler,
			(ClientData) NULL,
			(Tcl_CmdDeleteProc*) NULL
	);

	Tcl_CreateCommand(interp,
			"proclib",
			proclib_handler,
			(ClientData) NULL,
			(Tcl_CmdDeleteProc*) NULL
	);
	return 0;
}

int init_loadproc_handlers(Tcl_Interp* interp) {
	//load_processor_handlers["spectrum"]   = (processor_init_ptr)load_spectrum_processor;

	string tcl_command = "source " + project_path + "processors/load.tcl";
	Tcl_Eval(interp,tcl_command.c_str());
	return 0;
}


int loadproc_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]) {
	if (argc < 2) {
		Tcl_SetResult(interp,(char*)"loadproc_handler requires file name",TCL_STATIC);
		cout << "loadproc_handler error: requires file name" << endl;
		return TCL_ERROR;
	}
	string full_xml_name = argv[1];
	string processor_type = extract_processor_type(full_xml_name);

	cout << full_xml_name << ": " << processor_type << endl;

	//По типу триггера определяем обработчик, который должен его загрузить
	map<string,proc_create_proc>::iterator hit = load_processor_handlers.find(processor_type);
	if (hit == load_processor_handlers.end()) {
		//Такой обработчик не зарегистрирован
		cout << "\tError: handler for this processor type wasn`t registered" << endl;
	} else {
		proc_create_proc pip = load_processor_handlers[processor_type];
		CBaseProcessor* proc = (CBaseProcessor*)pip(full_xml_name);
		cout << "\tOK: processor <" << proc->szProcessorName << "> loaded" << endl;
	}
	return TCL_OK;
}

int p2vera_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]) {
	//p2vera load config_file_name
	//p2vera connect
	//p2vera disconnect
	//p2vera info
	//p2vera dump enable|disable
	InterpResultStream irs(interp);
	if (3 == argc) {
		string cmd = argv[1];
		if ("load" == cmd) {
			string config_name = build_project_path(argv[2]);
			p2v = new P2Vera(config_name);
			p2vctrl = new P2VeraControl(p2v);
			return TCL_OK;
		}
		irs << irs_clear << "p2vera_handler error: wrong parameters" << irs_apply;
		return TCL_ERROR;
	}
	if (2 == argc) {
		string cmd = argv[1];
		if ("connect" == cmd) {
			if (NULL == p2vctrl) {
				irs << irs_clear << "p2vera_handler error - p2vera wasnt initialized properly" << irs_apply;
				return TCL_ERROR;
			}
			if (p2vctrl->connect_fsm_server()) return TCL_OK;
			irs << irs_clear << "p2vera connect error - remote server doesnt respond" << irs_apply;
			return TCL_ERROR;
		}
		if ("enable" == cmd) {
			if (NULL == p2v) {
				irs << irs_clear << "p2vera_handler error - p2vera wasnt initialized properly" << irs_apply;
				return TCL_ERROR;
			}
			p2v->start_network();
			return TCL_OK;
		}
		if ("disconnect" == cmd) {
			if (NULL == p2vctrl) {
				irs << irs_clear << "p2vera_handler error - p2vera wasnt initialized properly" << irs_apply;
				return TCL_ERROR;
			}
			if (p2vctrl->disconnect_fsm_server()) return TCL_OK;
			irs << irs_clear << "p2vera disconnect error - remote server denied disconnect request, staying online" << irs_apply;
			return TCL_ERROR;
		}
		if ("connected" == cmd) {
			if (NULL == p2vctrl) {
				irs << irs_clear << "p2vera_handler error - p2vera wasnt initialized properly" << irs_apply;
				return TCL_ERROR;
			}
			int c = (int)p2vctrl->connected();
			irs << irs_clear << c << irs_apply;
			return TCL_OK;
		}
		if ("uniqid" == cmd) {
			if (NULL == p2v) {
				irs << irs_clear << "p2vera_handler error - p2vera wasnt initialized properly" << irs_apply;
				return TCL_ERROR;
			}
			irs << irs_clear << p2v->get_uniq_id() << irs_apply;
			return TCL_OK;
		}
	}
	irs << irs_clear << "p2vera_handler error: wrong parameters" << irs_apply;
	return TCL_ERROR;
}

int mkdump_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]) {
	if (argc < 3) {
		return TCL_ERROR;
	}

	string proc_id = argv[1];
	string dump_state = argv[2];

	bool bfile_name = false;
	string file_name = "";
	if (argc > 3 ) {
		bfile_name = true;
		file_name = argv[3];
	}

	bool bdump_enable = false;
	if (dump_state == "enable") {
		bdump_enable = true;
	}

	if (proc_id == "-all") {
		//Управлять дампом всех триггеров. Вывод будет производиться в "имя_файла.имя_триггера"
		cout << "mkdump error: -all wasn`t implemented" << endl;
		return TCL_ERROR;
	} else {
		//Управлять дампом одного триггера.
		CBaseProcessor* pr =  asr->FindProcessor(proc_id);
		if (NULL == pr) {
			cout << "mkdump error: processor " << proc_id << " not found" << endl;
			return TCL_ERROR;
		}

		if (!bfile_name) {
			pr->MkDump(bdump_enable);
		} else {
			pr->MkDump(bdump_enable, file_name);
		}
	}

	return TCL_OK;
}


int process_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]) {
	asr->Process();
	return 0;
}

int inpdrv_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]) {
	if (3 == argc) {
		string cmd = argv[1];
		string opt = argv[2];

		if ("load" == cmd) {
			return inpm->LoadInputDriver(interp, opt);
		}
		cout << "inpdrv_handler error: wrong options" << endl;
		return TCL_ERROR;
	}
	if (2 == argc) {
		string cmd = argv[1];
		if ("open" == cmd) {
			if (!inpm->is_opened()) {
				return inpm->open();
			}
			cout << "inpdrv_handler warning: input manager is already opened" << endl;
			return TCL_OK;
		}
		if ("close" == cmd) {
			if (!inpm->is_opened()) {
				return inpm->close();
			}
			cout << "inpdrv_handler warning: input manager is already closed" << endl;
			return TCL_OK;
		}
		if ("name" == cmd) {
			cout << inpm->get_driver_name() << endl;
			return TCL_OK;
		}
		if ("samplerate" == cmd) {
			unsigned int samplerate = inpm->get_samplerate();
			ostringstream ostr;
			ostr << samplerate;
			Tcl_SetResult(interp,(char*)ostr.str().c_str(),TCL_VOLATILE);
			return TCL_OK;
		}
	}
	return TCL_ERROR;
}

int proclib_handler(ClientData clientData, Tcl_Interp* interp, int argc, CONST char *argv[]) {
	if (4 == argc) {
		string cmd = argv[1];
		string name = argv[2];
		string libname = argv[3];

		if ("load" == cmd) {
			return  load_processor_lib(name,libname);
		}
	}
	cout << "proclib_handler error: wrong options" << endl;
	return TCL_ERROR;
}

bool folder_exists(std::string folder_name) {
	struct stat st;
	if (0 != stat(folder_name.c_str(), &st)) {
		return false;
	}
	if (!S_ISDIR(st.st_mode)) {
		return false;
	}
	return true;
}

std::string extract_processor_type(string filename) {
	xmlConfigPtr xml = CreateXmlConfig((char*)filename.c_str());
	if (NULL == xml) {
		cout << "extract_trigger_type error: couldn`t load file <" << filename << ">" << endl;
		return "error";
	}

	string trigger_type = xmlGetStringValue(xml,"/processor/type");
	return trigger_type;
}

int load_processors(Tcl_Interp* interp, std::string foldername) {
	if (!folder_exists(foldername)) {
		cout << "load_processors error: folder " << foldername << " not found" << endl;
		return -1;
	}
	FTS      *tree;
	FTSENT   *node;

	char *paths[2];
	paths[0] = (char*)foldername.c_str();
	paths[1] = NULL;

	if ((tree = fts_open(paths, FTS_NOCHDIR, NULL)) == NULL) {
		cout << "load_processors error: couldn`t open folder " << foldername << endl;
		return -1;
	}

	cout << "Loading processors from folder <" << foldername <<">..." << endl;
	while ((node = fts_read(tree))) {
		if (S_ISDIR(node->fts_statp->st_mode)) {
			continue;
		}

		string full_xml_name = foldername + node->fts_name;
		if (0 != full_xml_name.compare(full_xml_name.size()-4,4,".xml")) {
			continue;
		}

		string tcl_command = "loadproc {" + full_xml_name + "}";
		Tcl_Eval(interp,tcl_command.c_str());
	}

	fts_close(tree);
	return 0;
}

