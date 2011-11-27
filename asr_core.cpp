/*
 * asr_core.cpp
 *
 *  Created on: 31.07.2011
 *      Author: drozdov
 */

#include <unistd.h>
#include "asr_core.h"
#include "input_manager.h"

using namespace std;

CAsrCore::CAsrCore () {
	RegisterProcessor((CBaseProcessor*)1);
}

int CAsrCore::RegisterProcessor(CBaseProcessor* proc) {
	if (1 == (int)proc) {
		//Тестовая опция
		return 0;
	}

	//Проверяем, чо процессор с таким именем не зарегистрирован
	map<string,CBaseProcessor*>::iterator mit = by_name.find(proc->szProcessorName);
	if (mit != by_name.end()) {
		//Найден
		cout << "CAsrCore::RegisterProcessor error. Processor with this name already was registered" << endl;
		cout << "Processor name: " << proc->szProcessorName << endl;
		return -1;
	}

	processors.push_back(proc);
	by_name[proc->szProcessorName] = proc;
	return processors.size() - 1;
}

CBaseProcessor* CAsrCore::FindProcessor(std::string proc_name) {
	map<string,CBaseProcessor*>::iterator mit = by_name.find(proc_name);
	if (mit != by_name.end()) {
		return mit->second;
	}
	return NULL;
}

int CAsrCore::Process() {
	vector<CBaseProcessor*>::iterator itp;
	if (0 != inpm->open()) {
		cout << "CAsrCore::Process error: failed to open input" << endl;
	}

	int bufsize = inpm->get_samplerate() *100 / 1000;
	int *buf = new int[bufsize];

	//Инициализируем все процессоры
	proc_math_init pmi;
	pmi.ck_size = sizeof(proc_math_init);
	pmi.samplerate = inpm->get_samplerate();
	pmi.bufsize = bufsize;

	cout << "CAsrCore::Process info: initializing processors" << endl;
	for (itp=processors.begin();itp < processors.end();itp++) {
		CBaseProcessor* pr = *itp;
		pr->Initialize(&pmi);
	}

	int rsize = 0; //Количество считанных байт из входного потока

	nlsr->SetSamplerate(inpm->get_samplerate());
	nls->Send(nlsr);

	process_task pt;
	pt.buf = buf;
	long long cur_time = 0;
	while ( (rsize=inpm->read(buf,bufsize)) > 0 ) {
		nmt->Clear();

		pt.sample_count = rsize;
		for (itp=processors.begin();itp < processors.end();itp++) {
			CBaseProcessor* pr = *itp;
			pr->ProcessInput(&pt);

			for (int i=0;i<pr->out_count;i++) {
				if (pr->outs[i].value != pr->prev_outs[i].value) {
					nmt->Add(pr->trigger_id,pr->outs[i].out_id,pr->outs[i].value);
					pr->prev_outs[i].value = pr->outs[i].value;
				}
			}
		}

		cur_time += rsize;
		nmtt->SetTime(cur_time);

		nls->Send(nmt);
		nls->Send(nmtt);

		//usleep(2);
	}

	//inpm->close();
	return 0;
}


CAsrCore* asr = NULL;

