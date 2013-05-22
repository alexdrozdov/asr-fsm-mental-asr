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
	RegisterProcessor(NULL);
}

int CAsrCore::RegisterProcessor(CBaseProcessor* proc) {
	if (NULL == proc) {
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
	pmi.bitspersample = inpm->get_bitpersample();

	cout << "CAsrCore::Process info: initializing processors" << endl;
	cout << "Processors count " << processors.size() << endl;
	for (itp=processors.begin();itp < processors.end();itp++) {
		CBaseProcessor* pr = *itp;
		if (0 != pr->Initialize(&pmi)) {
			return 1;
		}
	}

	int rsize = 0; //Количество считанных байт из входного потока

	DspMessageTrig nmt;
	DspMessageTime nmtt(0);
	DspMessageSamplerate nlsr(inpm->get_samplerate());

	P2VeraStream p2s_c2s = p2v->create_outstream("c2s-proc-data");
	p2s_c2s << nlsr;

	process_task pt;
	pt.buf = buf;
	long long cur_time = 0;
	while ( (rsize=inpm->read(buf,bufsize)) > 0 ) {
		nmt.Clear();

		pt.sample_count = rsize;
		//FIXME Время растет для каждого процессора по отдельности. По идее, необходимо сортировать все события, а потом отправлять их на сервер в поярдке их возникновения. Текущая схема работает только для одного "процессора" - источника событий
		for (itp=processors.begin();itp < processors.end();itp++) {
			CBaseProcessor* pr = *itp;
			pr->SetInitialTime(cur_time);
			pr->SetTimeIncrement(1);
			pr->ProcessInput(&pt);

			while (pr->OutputsPresent()) {
				pr->ShiftOutput();
				nmt.Clear();
				for (int i=0;i<pr->out_count;i++) {
					if (pr->outs[i].value != pr->prev_outs[i].value) {
						nmt.Add(pr->trigger_id,pr->outs[i].out_id,pr->outs[i].value);
						pr->prev_outs[i].value = pr->outs[i].value;
					}
				}
				cur_time = pr->output_time;
				nmtt.SetTime(cur_time);
				p2s_c2s << nmt << nmtt;
			}
		}

		cur_time += rsize;
	}
	return 0;
}


CAsrCore* asr = NULL;

