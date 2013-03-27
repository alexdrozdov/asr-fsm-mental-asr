/*
 * spectrum_processor.h
 *
 *  Created on: 10.12.2012
 *      Author: drozdov
 */

#ifndef WAVELET_PROCESSOR_H_
#define WAVELET_PROCESSOR_H_

#include <queue>

#include "base_processor.h"
#include "array2d.h"

typedef struct _output_snapshot {
	std::vector<double> outputs;
	long long snapshot_time;
} output_snapshot;

class CWaveletProcessor : public CBaseProcessor {
public:
	CWaveletProcessor(std::string filename);
	int ProcessInput(pprocess_task pt);
	int Initialize(pproc_math_init pmi);

	virtual int MkDump(bool enable);
	virtual int MkDump(bool enable, std::string file_name);

	virtual bool SupportsTimeflow();                         //Проверка поддержки управления временем
	virtual bool RevertTime(long long revert_time);          //Возврат к указанному моменту времени
	virtual void SetInitialTime(long long init_time);        //Установка текущего времени (например, на момент передачи буфера данных)
	virtual void SetTimeIncrement(long long time_increment); //Установка шага увеличения времени на один отсчет данных

	virtual bool OutputsPresent();                           //Проверка наличия необработанных выходов
	virtual void ShiftOutput();                              //Поместить в выходной буфер очередные данные

private:
	int level_count;
	int frame_size;
	int src_frame_usage;
	double sample_scale; //Коэфициент масштабирования выборок. Рассчитывается на основе числа бит на отсчет
	std::vector<double> src_frame;
	CArray2d *arr_dwt;
	int max_dwt_repeat; //Максимальное значение повторения значений dwt для самого прореженного варианта
	std::queue<output_snapshot> snapshots;
};

#ifdef __cplusplus
extern "C" {
#endif

extern int asr_proccessor_init(dynamicproc_init* dp_init);

extern int   wavelet_v1_init_tcl(Tcl_Interp* interp);
extern int   wavelet_v1_init_core(proc_init_environ* env);
extern void* wavelet_v1_create(std::string filename);

#ifdef __cplusplus
}
#endif

#endif /* WAVELET_PROCESSOR_H_ */
