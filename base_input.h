/*
 * base_input.h
 *
 *  Created on: 31.07.2011
 *      Author: drozdov
 */

#ifndef BASE_INPUT_H_
#define BASE_INPUT_H_

#ifdef AUXPACKAGES
#include <tcl.h>
#else
#include <tcl8.5/tcl.h>
#endif

typedef int (*inpdrv_tcl_init_proc)(Tcl_Interp* interp);
typedef int (*inpdrv_core_init_proc)(void);
typedef int (*inpdrv_open_proc)(void);
typedef int (*inpdrv_read_proc)(int*, int);
typedef int (*inpdrv_close_proc)(void);
typedef int (*inpdrv_get_samplerate)(void);
typedef int (*inpdrv_set_samplerate)(int);
typedef int (*inpdrv_get_bitpersample)(void);

typedef struct _dynamiclib_init {
	unsigned int ck_size;
	inpdrv_tcl_init_proc  tcl_init;  //Функция, отвечающая за инициализацию интерпретатора
	inpdrv_core_init_proc core_init; //Функция, отвечающая за инициализацию основного функционала
	inpdrv_open_proc open;           //Функция, отвечющая за открытие канала ввода
	inpdrv_read_proc read;           //Функция, обеспечивающая чтение
	inpdrv_close_proc close;         //Функция, закрывающая канал

	inpdrv_get_samplerate get_samplerate;
	inpdrv_set_samplerate set_samplerate;

	inpdrv_get_bitpersample get_bitpersample;

	unsigned int asr_minor;          //Минимальная совместимая версия asr
	unsigned int asr_major;          //Максимальная совместимая версия asr
} dynamiclib_init;

#endif /* BASE_INPUT_H_ */
