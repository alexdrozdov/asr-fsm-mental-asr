/*
 * mental_asr.h
 *
 *  Created on: 30.07.2011
 *      Author: drozdov
 */

#ifndef MENTAL_ASR_H_
#define MENTAL_ASR_H_

#include <string>
#include <vector>

#ifdef AUXPACKAGES
#include <tcl.h>
#else
#include <tcl8.5/tcl.h>
#endif

#include "netlink_pack.h"

extern NetlinkMessageTrig* nmt;
extern NetlinkMessageTime* nmtt;
extern NetlinkSender* nls;

extern std::string executable_path;
extern std::string project_path;

extern int init_asr_structs(Tcl_Interp *interp);

#endif /* MENTAL_ASR_H_ */
