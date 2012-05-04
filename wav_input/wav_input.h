/*
 * wav_input.h
 *
 *  Created on: 31.07.2011
 *      Author: drozdov
 */

#ifndef WAV_INPUT_H_
#define WAV_INPUT_H_

#ifdef MACOSX
#include <tcl.h>
#else
#include <tcl8.5/tcl.h>
#endif

#include "base_input.h"

#ifdef __cplusplus
extern "C" {
#endif

extern int inpdrv_init(dynamiclib_init* dl_init);

extern int wavdrv_tcl_init_proc(Tcl_Interp* interp);
extern int wavdrv_core_init_proc();
extern int wavdrv_open_proc();
extern int wavdrv_read_proc(int* buf,int n);
extern int wavdrv_close_proc();

extern int wavdrv_get_samplerate();
extern int wavdrv_set_samplerate(int samplerate);

#ifdef __cplusplus
}
#endif

#endif /* WAV_INPUT_H_ */
