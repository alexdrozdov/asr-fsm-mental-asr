/*
 * p2vera_control.h
 *
 *  Created on: 18.05.2013
 *      Author: drozdov
 */

#ifndef P2VERA_CONTROL_H_
#define P2VERA_CONTROL_H_

#include <p2vera.h>
#include <p2message.h>
#include <p2stream.h>

class P2VeraControl {
public:
	P2VeraControl(P2Vera *p2v);
	bool connect_fsm_server();
	bool disconnect_fsm_server();
	bool connected();
	bool alive();
private:
	P2Vera *p2v;
	P2VeraStream p2ctrl;
	bool is_connected;
};

extern P2VeraControl *p2vctrl;

#endif /* P2VERA_CONTROL_H_ */
