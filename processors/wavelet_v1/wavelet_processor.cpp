/*
 * wavelet_processor.cpp
 *
 *  Created on: 10.12.2012
 *      Author: drozdov
 */

#include <math.h>
#include <sstream>

#include "wavelet_processor.h"
#include "asr_core.h"
#include "xml_support/xml_support.h"

using namespace std;

//Максимально разрешенная частота входного сигнала
#define MAX_SAMPLERATE 400000

CAsrCore* asr;

CWaveletProcessor::CWaveletProcessor(std::string filename) {
	xmlConfigPtr xml = CreateXmlConfig((char*)filename.c_str());
	if (NULL == xml) {
		cout << "CWaveletProcessor::CWaveletProcessor error: couldn`t load file <" << filename << ">" << endl;
		return;
	}

	szProcessorName = xmlGetStringValue(xml, "/processor/name");
	enabled         = xmlGetBooleanValue(xml,"/processor/enabled",false);
	adjust_power    = xmlGetBooleanValue(xml,"/processor/adjust_power",false);
	if (adjust_power) {
		power_norm = xmlGetDoubleValue(xml,"/processor/adjust_power/norm",1.0);
	}
	adjust_max      = xmlGetBooleanValue(xml,"/processor/adjust_max",false);
	out_count       = xmlGetIntValue(xml,"/processor/frequencies/count",-1);
	trigger_id      = xmlGetIntValue(xml,"/processor/id",-1);

	if (out_count < 1) {
		cout << "CWaveletProcessor::CWaveletProcessor error: out_count must be at least 1" << endl;
		return;
	}

	outs.resize(out_count);
	prev_outs.resize(out_count);
	frequencies.resize(out_count);

	powers.resize(out_count);
	for (int i=0;i<out_count;i++) {
		std::ostringstream stream;
		stream << i;
		string val_path = "/processor/frequencies/i" + stream.str() + "/";

		int nid    = xmlGetIntValue(xml,(val_path+"id").c_str(),0);
		double frq = xmlGetDoubleValue(xml,(val_path+"value").c_str(),0.0);

		frequencies[i] = frq;
		outs[i].out_id = nid;
		prev_outs[i].out_id = nid;

		powers[i].r = 0.0;
		powers[i].i = 0.0;
	}

	asr->RegisterProcessor((CBaseProcessor*)this);

	dump_to_file = false;
	dump_enabled = false;
}

int CWaveletProcessor::ProcessInput(pprocess_task pt) {
	int *buf = pt->buf;
	int sample_count = pt->sample_count;

	//При необходимости вычисляем полную мощность действующего сигнала
	if (adjust_power) {
		power = 0;
		for (int j=0;j<sample_count;j++) {
			power += fabs((double) buf[j]);
		}
	}

	//power = sqrt(power);

	//Вычисляем мощности каждой из спектральных составляющих
	int n_eff_frequencies = out_count;
	if (adjust_power) {
		n_eff_frequencies--;
		outs[out_count-1].value = power / power_norm;
	}
	for (int i=0;i<n_eff_frequencies;i++) {
		powers[i].r = 0.0;
		powers[i].i = 0.0;
		for (int j=0;j<pt->sample_count;j++) {
			powers[i].r += fdds[ dds_states[i].pnt ] * (double)buf[j];
			powers[i].i += fdds[ dds_states[i].pnt2 ] * (double)buf[j];

			dds_states[i].pnt  = (dds_states[i].pnt + dds_states[i].pnt_incr) & dds_states[i].pnt_mask;
			dds_states[i].pnt2 = (dds_states[i].pnt2 + dds_states[i].pnt_incr) & dds_states[i].pnt_mask;
		}

		if (adjust_power) {
			if (0.0 == power) {
				outs[i].value = 0.0;
			} else {
				outs[i].value = sqrt(powers[i].r*powers[i].r + powers[i].i*powers[i].i) / power;
			}
		} else {
			outs[i].value = sqrt(powers[i].r*powers[i].r + powers[i].i*powers[i].i);
		}
	}

	if (dump_enabled && dump_to_file) {
		for (int i=0;i<out_count;i++) {
			dump_stream << outs[i].value << " ";
		}
		dump_stream << endl;
	} else  if (dump_enabled) {
		for (int i=0;i<out_count;i++) {
			cout << outs[i].value << " ";
		}
		cout << endl;
	}
	return 0;
}

int CWaveletProcessor::Initialize(pproc_math_init pmi) {
	if (NULL == pmi) {
		cout << "CSpectrumProcessor::Initialize error - null pointer to math init struct" << endl;
		return 1;
	}
	samplerate = pmi->samplerate;

	if (pmi->samplerate > MAX_SAMPLERATE) {
		cout << "CSpectrumProcessor::Initialize error - samplerate (" << pmi->samplerate << ") supplied exides allowed (" << MAX_SAMPLERATE << ")" << endl;
		return 1;
	}
	if (pmi->samplerate < 1) {
		cout << "CSpectrumProcessor::Initialize error - samplerate (" << pmi->samplerate << ") is lesser than allowed" << endl;
		return 1;
	}

	//Инициализируем таблицу DDS
	v2N  = (int)ceil(log2(ceil((double)samplerate/0.5)));
	v2Nl = (int)pow(2.0,(double)v2N);
	v2Nlh = v2Nl / 2;

	fdds.resize(v2Nl);
	for (int i=0;i<v2Nl;i++) {
		fdds[i] = cos(2*M_PI*(double)i / (double)v2Nl);
	}

	double freq_step = (double)samplerate / (double)v2Nl;
	dds_states.resize(out_count);
	for (int i=0;i<out_count;i++) {
		dds_states[i].pnt  = 0;
		dds_states[i].pnt2 = v2Nlh / 2;
		dds_states[i].pnt_mask = v2Nl-1;
		dds_states[i].pnt_incr = (int)((double)frequencies[i] / freq_step);
	}
	return 0;
}


void* wavelet_v1_create(std::string filename) {
	return (void*) (new CWaveletProcessor(filename));
}

int asr_proccessor_init(dynamicproc_init* dp_init) {
	if (NULL == dp_init) {
		return 1;
	}
	if (dp_init->ck_size != sizeof(dynamicproc_init)) {
		std::cout << "spectrum_v1_init error: supplied dp_init->ck_size differes from local structure size" << std::endl;
		std::cout << "This means, library is incompatible with asr core" << std::endl;
		return 2;
	}

	dp_init->core_init = wavelet_v1_init_core;
	dp_init->tcl_init  = wavelet_v1_init_tcl;
	dp_init->create    = wavelet_v1_create;

	dp_init->asr_minor = 0;
	dp_init->asr_major = 0x00010000;

	return 0;
}

int CWaveletProcessor::MkDump(bool enable) {
	if (dump_enabled) {
		//Дамп и так выводится. Закрываем существующий дескрптор
		if (dump_stream != cout) {
			dump_stream.close();
		}
	}
	dump_enabled = enable;
	dump_to_file = false;
	return 0;
}

int CWaveletProcessor::MkDump(bool enable, string file_name) {
	if (dump_enabled) {
		//Дамп и так выводится. Закрываем существующий дескриптор
		if (dump_stream != cout) {
			dump_stream.close();
		}
	}

	dump_enabled = enable;
	if (dump_enabled) {
		if ("cout" == file_name) {
			dump_to_file = false;
		} else {
			dump_to_file = true;
			dump_stream.open(file_name.c_str());
		}
	}
	return 0;
}

int wavelet_v1_init_tcl(Tcl_Interp* interp) {
	return 0;
}

int wavelet_v1_init_core(proc_init_environ* env) {
	if (env->ck_size < sizeof(proc_init_environ)) {
		std::cout << "spectrum_v1_init_core error: supplied env->ck_size is less than local structure size" << std::endl;
		std::cout << "This means, library is incompatible with asr core" << std::endl;
		return 2;
	}
	asr = env->asr;
	return 0;
}



