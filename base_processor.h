/*
 * base_processor.h
 *
 *  Created on: 30.07.2011
 *      Author: drozdov
 */

#ifndef BASE_PROCESSOR_H_
#define BASE_PROCESSOR_H_

#include <string>
#include <vector>
#include <fstream>

#include "fwd_classes.h"

#include "p2vera_dsp.h"
#include "asr_core.h"

typedef struct _process_task {
	int sample_count;
	int* buf;
} process_task, *pprocess_task;

typedef struct _proc_math_init {
	unsigned int ck_size;
	unsigned int samplerate;
	unsigned int bufsize;
	unsigned int bitspersample;
} proc_math_init, *pproc_math_init;


typedef struct _proc_init_environ {
	unsigned int ck_size;
	CAsrCore* asr;
} proc_init_environ;

typedef int (*proc_tcl_init_proc)(Tcl_Interp* interp);
typedef int (*proc_core_init_proc)(proc_init_environ* env);
typedef void* (*proc_create_proc)(std::string filename);

typedef struct _dynamicproc_init {
	unsigned int ck_size;
	proc_tcl_init_proc  tcl_init;  //Функция, отвечающая за инициализацию интерпретатора
	proc_core_init_proc core_init; //Функция, отвечающая за инициализацию основного функционала
	proc_create_proc    create;    //Функция, создающая новый экземпляр процессора

	unsigned int asr_minor;          //Минимальная совместимая версия asr
	unsigned int asr_major;          //Максимальная совместимая версия asr
} dynamicproc_init;

//Базовая версия низкоуровневого обработчика.
class CBaseProcessor {
public:
	std::string szProcessorName;
	bool enabled;

	int trigger_id;

	int out_count;
	std::vector<trig_msg_item> outs;
	std::vector<trig_msg_item> prev_outs;

	virtual int ProcessInput(pprocess_task pt) = 0;
	virtual int Initialize(pproc_math_init pmi) = 0;


	virtual int MkDump(bool enable) = 0;
	virtual int MkDump(bool enable, std::string file_name) = 0;

	virtual bool SupportsTimeflow() = 0;                         //Проверка поддержки управления временем
	virtual bool RevertTime(long long revert_time) = 0;          //Возврат к указанному моменту времени
	virtual void SetInitialTime(long long init_time) = 0;        //Установка текущего времени (например, на момент передачи буфера данных)
	virtual void SetTimeIncrement(long long time_increment) = 0; //Установка шага увеличения времени на один отсчет данных

	virtual bool OutputsPresent() = 0;                           //Проверка наличия необработанных выходов
	virtual void ShiftOutput() = 0;                              //Поместить в выходной буфер очередные данные

	long long init_time;
	long long current_time;
	long long time_increment;
	long long output_time;


	bool dump_enabled; //Триггер должен выводить входные и выходные парамеры при каждом вызове ProcessAnchestors
	bool dump_to_file;
	std::ofstream dump_stream; //Поток, в который выводится дамп

	int samplerate;    //Samplerate входящих данных
	int minwindowsize; //Минимальный объем обрабатываемых данных
	int maxwindowsize; //Максимальный объем обрабатываемых данных
};


#endif /* BASE_PROCESSOR_H_ */
