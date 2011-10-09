/*
 * processor_loader.h
 *
 *  Created on: 03.08.2011
 *      Author: drozdov
 */

#ifndef PROCESSOR_LOADER_H_
#define PROCESSOR_LOADER_H_

#include <string>
#include <map>

#include "base_processor.h"

extern int load_processor_lib(std::string name, std::string libname);


//typedef CBaseProcessor* (*processor_init_ptr)(std::string);
extern std::map<std::string,proc_create_proc> load_processor_handlers;

#endif /* PROCESSOR_LOADER_H_ */
