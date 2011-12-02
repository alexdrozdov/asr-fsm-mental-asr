/*
 * spectrum_processor.h
 *
 *  Created on: 30.07.2011
 *      Author: drozdov
 */

#ifndef SPECTRUM_PROCESSOR_H_
#define SPECTRUM_PROCESSOR_H_


#include "base_processor.h"

typedef struct _dds_state {
	unsigned int pnt;
	unsigned int pnt2;
	unsigned int pnt_incr;
	unsigned int pnt_mask;
} dds_state, *pdds_state;

typedef struct _cmplx {
	double r;
	double i;
} cmplx;

class CSpectrumProcessor : public CBaseProcessor {
public:
	CSpectrumProcessor(std::string filename);
	int ProcessInput(pprocess_task pt);
	int Initialize(pproc_math_init pmi);

	virtual int MkDump(bool enable);
	virtual int MkDump(bool enable, std::string file_name);

private:
	std::vector<int> frequencies;

	std::vector<double> fdds;
	int v2N;
	int v2Nl;
	int v2Nlh;

	std::vector<dds_state> dds_states;
	std::vector<cmplx> powers;
	double power;
	double power_norm;

	bool adjust_power;
	bool adjust_max;
};

#ifdef __cplusplus
extern "C" {
#endif

extern int asr_proccessor_init(dynamicproc_init* dp_init);

extern int   spectrum_v1_init_tcl(Tcl_Interp* interp);
extern int   spectrum_v1_init_core(proc_init_environ* env);
extern void* spectrum_v1_create(std::string filename);

#ifdef __cplusplus
}
#endif

#endif /* SPECTRUM_PROCESSOR_H_ */
