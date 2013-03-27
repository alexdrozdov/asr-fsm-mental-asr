/*
 * wavelet_processor.cpp
 *
 *  Created on: 10.12.2012
 *      Author: drozdov
 */

#include <math.h>
#include <sstream>

#include <wavelet1d.h>

#include "wavelet_processor.h"
#include "array2d.h"
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
	level_count     = xmlGetIntValue(xml,"/processor/levels/value",-1);
	frame_size      = xmlGetIntValue(xml,"/processor/frame_length/value",-1);
	trigger_id      = xmlGetIntValue(xml,"/processor/id",-1);

	minwindowsize = xmlGetIntValue(xml, "/processor/limits/min_frame_size/value", -1);
	maxwindowsize = xmlGetIntValue(xml, "/processor/limits/max_frame_size/value", -1);

	level_count++;
	out_count = level_count;

	if (out_count < 1) {
		cout << "CWaveletProcessor::CWaveletProcessor error: out_count must be at least 1" << endl;
		return;
	}

	src_frame.resize(frame_size);
	src_frame_usage = 0;

	outs.resize(out_count);
	prev_outs.resize(out_count);

	max_dwt_repeat = 1; //Рассчитываем максимальное значение прореживания. Настолько необходимо продублировать каждый отсчет наиболее прореженного сигнала, чтобы получить полноценную матрицу вейвлет преобразования
	for (int i=0;i<level_count;i++) max_dwt_repeat *= 2;

	arr_dwt = new CArray2d(frame_size, level_count);

	asr->RegisterProcessor((CBaseProcessor*)this);

	dump_to_file = false;
	dump_enabled = false;
}

int CWaveletProcessor::ProcessInput(pprocess_task pt) {
	int *buf = pt->buf;
	int unproccessed_samples = pt->sample_count;

	int cnt = 0;
	while (unproccessed_samples>0) {
		//Заполняем буфер для wavelet1d
		int frame_underrun = frame_size - src_frame_usage; //Количество незаполненных ячеек во входном буфере
		int copy_count = frame_underrun>unproccessed_samples?unproccessed_samples:frame_underrun;

		unproccessed_samples -= copy_count;
		for (int i=0;i<copy_count;i++) {
			src_frame[src_frame_usage] = (double)buf[cnt] * sample_scale;
			src_frame_usage++;
			cnt++;
		}
		if (src_frame_usage<frame_size) {
			break; //Не удалось заполнить до конца буфер. Значит, обработать его также не получится. Выходим и ждем пока в следующий раз этот буфер не дозаполнят
		}

		vector<double> swt_output;
		int length;
		swt(src_frame, level_count-1, "db2", swt_output, length);
		int cur = 0;
		int max_rows = (int)swt_output.size() / length;
		cout << max_rows << endl;
		for (int i=0;i<max_rows;i++) {
			for (int j=0;j<length;j++)
				arr_dwt->operator ()(i,j) = swt_output[cur++];
		}
		arr_dwt->save_to_file("dwt_arr.txt");

		src_frame_usage = 0;
	}

	//Копируем результаты расчета в очередь выходных результатов
	for (int i=0;i<frame_size;i++) {
		output_snapshot os;
		os.outputs.resize(level_count);
		current_time += time_increment;
		os.snapshot_time = current_time;
		for (int j=0;j<level_count;j++) os.outputs[j] = arr_dwt->operator ()(j, i);
		snapshots.push(os);

		if (dump_enabled && dump_to_file) {
			dump_stream << "TIME: " << current_time << " OUTS: ";
			for (int i=0;i<out_count;i++) {
				dump_stream << outs[i].value << " ";
			}
			dump_stream << endl;
		} else  if (dump_enabled) {
			cout << "TIME: " << current_time << " OUTS: ";
			for (int i=0;i<out_count;i++) {
				cout << outs[i].value << " ";
			}
			cout << endl;
		}
	}
	return 0;
}

int CWaveletProcessor::Initialize(pproc_math_init pmi) {
	if (NULL == pmi) {
		cout << "CSpectrumProcessor::Initialize error - null pointer to math init struct" << endl;
		return 1;
	}
	samplerate = pmi->samplerate;
	sample_scale = 1.0 / pow(2.0, (double)(pmi->bitspersample-1));
	arr_dwt->clear_file("dwt_arr.txt");
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

bool CWaveletProcessor::SupportsTimeflow() {
	return false;
}

bool CWaveletProcessor::RevertTime(long long revert_time) {
	return false;
}

void CWaveletProcessor::SetInitialTime(long long init_time) {
	this->init_time = init_time;
	this->current_time = init_time;
	this->output_time = init_time;
}

void CWaveletProcessor::SetTimeIncrement(long long time_increment) {
	this->time_increment = time_increment;
}

bool CWaveletProcessor::OutputsPresent() {
	if (snapshots.size() > 0) return true;
	return false;
}

void CWaveletProcessor::ShiftOutput() {
	if (0 == snapshots.size()) return;
	output_snapshot os =  snapshots.front();
	snapshots.pop();
	for (int i=0;i<out_count;i++) {
		outs[i].value = os.outputs[i];
		outs[i].out_id = i;
	}
	output_time = os.snapshot_time;
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



