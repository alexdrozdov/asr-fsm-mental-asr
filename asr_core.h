/*
 * asr_core.h
 *
 *  Created on: 31.07.2011
 *      Author: drozdov
 */

#ifndef ASR_CORE_H_
#define ASR_CORE_H_

#include <string>
#include <vector>
#include <map>

#include <iostream>

#ifdef AUXPACKAGES
#include <tcl.h>
#else
#include <tcl8.5/tcl.h>
#endif

#include "fwd_classes.h"
#include "base_processor.h"
#include "mental_asr.h"
#include "p2vera_dsp.h"

class CAsrCore {
public:
	CAsrCore();

	virtual int RegisterProcessor(CBaseProcessor* proc);
	virtual int Process();

	virtual CBaseProcessor* FindProcessor(std::string proc_name);

	std::vector<CBaseProcessor*> processors;
	std::map<std::string, CBaseProcessor*> by_name;
};

extern CAsrCore* asr;

#endif /* ASR_CORE_H_ */
