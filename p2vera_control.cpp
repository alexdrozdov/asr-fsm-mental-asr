/*
 * p2vera_control.cpp
 *
 *  Created on: 18.05.2013
 *      Author: drozdov
 */

#include <sys/poll.h>
#include <sys/time.h>

#include <iostream>

#include <p2vera.h>
#include <p2message.h>
#include <p2stream.h>

#include "p2vera_control.h"

using namespace std;


P2VeraControl::P2VeraControl(P2Vera *p2v) {
	is_connected = false;
	this->p2v = p2v;
	p2ctrl = p2v->create_stream("control");
}

bool P2VeraControl::connect_fsm_server() {
	if (is_connected) return true;
	pollfd *pfd = new pollfd[1];
	pfd[0].fd = p2ctrl.get_fd();
	pfd[0].events = POLLIN | POLLHUP;
	pfd[0].revents = 0;

	P2VeraTextMessage p2tm_connect((string)"connect request: " + p2v->get_uniq_id());
	P2VeraTextMessage p2tm_response;
	p2ctrl << p2tm_connect;

	timeval tv_now;
	timeval tv_request;
	gettimeofday(&tv_request, NULL);

	string response_grant = "connect grant: " + p2v->get_uniq_id();
	int connect_attemps = 0;
	const int max_connect_attemps = 20;
	while(!is_connected) {
		if (poll(pfd, 1, 100) < 1) {
			pfd[0].revents = 0;
			gettimeofday(&tv_now, NULL);
			unsigned  int delta = ((1000000-tv_request.tv_usec)+(tv_now.tv_usec-1000000)+(tv_now.tv_sec-tv_request.tv_sec)*1000000) / 1000;
			if (delta < 500) {
				continue;
			}
			gettimeofday(&tv_request, NULL);
			cout << "connect_fsm_server info - repeating server request..." << endl;
			p2ctrl << p2tm_connect;
			continue;
		}
		if (0==pfd[0].revents) continue;
		pfd[0].revents = 0;

		p2ctrl >> p2tm_response;
		//p2tm_response.print();
		string response_str = p2tm_response;
		if (response_str == response_grant) {
			is_connected = true;
			cout << "connect_fsm_server info - remote connection accepted" << endl;
			break;
		}

		connect_attemps++;
		if (connect_attemps >= max_connect_attemps) {
			cout << "connect_fsm_server error - failed to connect remote server, exiting" << endl;
			delete[] pfd;
			return false;
		}
	}

	delete[] pfd;
	return is_connected;
}

bool P2VeraControl::disconnect_fsm_server() {
	if (!is_connected) return true;
	pollfd *pfd = new pollfd[1];
	pfd[0].fd = p2ctrl.get_fd();
	pfd[0].events = POLLIN | POLLHUP;
	pfd[0].revents = 0;

	P2VeraTextMessage p2tm_connect((string)"disconnect request: " + p2v->get_uniq_id());
	P2VeraTextMessage p2tm_response;
	p2ctrl << p2tm_connect;

	timeval tv_now;
	timeval tv_request;
	gettimeofday(&tv_request, NULL);


	string response_grant = "disconnect grant: " + p2v->get_uniq_id();
	string response_deny = "disconnect deny: " + p2v->get_uniq_id();
	int connect_attemps = 0;
	const int max_connect_attemps = 20;
	while(is_connected) {
		if (poll(pfd, 1, 100) < 1) {
			pfd[0].revents = 0;
			gettimeofday(&tv_now, NULL);
			unsigned  int delta = ((1000000-tv_request.tv_usec)+(tv_now.tv_usec-1000000)+(tv_now.tv_sec-tv_request.tv_sec)*1000000) / 1000;
			if (delta < 500) {
				continue;
			}
			gettimeofday(&tv_request, NULL);
			cout << "disconnect_fsm_server info - repeating server request..." << endl;
			p2ctrl << p2tm_connect;
			continue;
		}
		if (0==pfd[0].revents) continue;
		pfd[0].revents = 0;

		p2ctrl >> p2tm_response;
		//p2tm_response.print();
		string response_str = p2tm_response;
		if (response_str == response_grant) {
			is_connected = false;
			cout << "disconnect_fsm_server info - disconnection accepted" << endl;
			break;
		}
		if (response_str == response_deny) {
			cout << "disconnect_fsm_server info - disconnection denied" << endl;
			break;
		}

		connect_attemps++;
		if (connect_attemps >= max_connect_attemps) {
			is_connected = false; //Связь прекратилась сама собой...
			cout << "disconnect_fsm_server error - no resonse from remote server, considering it to be disconnected" << endl;
			break;
		}
	}

	delete[] pfd;
	return !is_connected;
}

bool P2VeraControl::connected() {
	return is_connected;
	return true;
}

bool P2VeraControl::alive() {
	return true;
}

extern bool enable_p2vera_connect() {

	return true;
}


P2VeraControl *p2vctrl = NULL;

