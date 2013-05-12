/*
 * netlink_pack.cpp
 *
 *  Created on: 04.07.2011
 *      Author: drozdov
 */


#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <pthread.h>

#include <iostream>

#include "netlink_pack.h"

using namespace std;

void* netlinksender_thread_function (void* thread_arg);
void* netlink_rcv_thread_function (void* thread_arg);



NetlinkMessage::~NetlinkMessage() {
}


bool NetlinkMessage::get_data(std::string& str) const {
	return pkg.SerializeToString(&str);
}

int NetlinkMessage::get_data(void* data, int max_data_size) const {
	int required_size = pkg.ByteSize();
	if (required_size > max_data_size) return 0;
	pkg.SerializeToArray(data, required_size);
	return required_size;
}

int NetlinkMessage::get_data_size() const {
	return pkg.ByteSize();
}

bool NetlinkMessage::set_data(void* data, int data_size) {
	if (NULL == data) return false;
	return pkg.ParseFromArray(data, data_size);
}

bool NetlinkMessage::set_data(std::string &str) {
	return pkg.ParseFromString(str);
}


/////////////////////////////////////////////////////////////////////////////////////////////



NetlinkMessageTrig::NetlinkMessageTrig() {
	pkg.add_modified_triggers_inst();
}

NetlinkMessageTrig::~NetlinkMessageTrig() {
}

void NetlinkMessageTrig::Add(int trigger_id, int out_id, double value) {
	//Ищем триггер с указанным id
	dsp::modified_triggers *mt = pkg.mutable_modified_triggers_inst(0);
	dsp::modified_triger *mmt = NULL;
	::google::protobuf::RepeatedPtrField< ::dsp::modified_triger >::iterator it;
	for (it=mt->mutable_items()->begin();it!=mt->mutable_items()->end();it++){
		if (it->id() == trigger_id) {
			mmt = &(*it);
			break;
		}
	}
	if (NULL == mmt) {
		mmt = mt->add_items();
	}
	mmt->set_id(trigger_id);
	dsp::trigger_output* tro = mmt->add_outputs();
	tro->set_out_id(out_id);
	tro->set_value(value);
}

void NetlinkMessageTrig::NetlinkMessageTrig::Clear() {
	pkg.mutable_modified_triggers_inst(0)->Clear();
}

////////////////////////////////////////////////////////////////////


NetlinkMessageTime::NetlinkMessageTime(long long time) {
	pkg.add_time_inst()->set_current_time(time);
}

NetlinkMessageTime::~NetlinkMessageTime() {
}

void NetlinkMessageTime::SetTime(long long time) {
	pkg.mutable_time_inst(0)->set_current_time(time);
}

void NetlinkMessageTime::Clear() {
	pkg.mutable_time_inst(0)->Clear();
}
////////////////////////////////////////////////////////////////////

NetlinkMessageSamplerate::NetlinkMessageSamplerate(unsigned int samplerate) {
	pkg.add_samplerate_inst()->set_samplerate(samplerate);
}

NetlinkMessageSamplerate::~NetlinkMessageSamplerate() {
}

void NetlinkMessageSamplerate::SetSamplerate(unsigned int samplerate) {
	pkg.mutable_samplerate_inst(0)->set_samplerate(samplerate);
}

void NetlinkMessageSamplerate::Clear() {
	pkg.mutable_samplerate_inst(0)->Clear();
}

////////////////////////////////////////////////////////////////////

NetlinkSender::NetlinkSender() {
	connected = false;
}

NetlinkSender::~NetlinkSender() {
	cout << "NetlinkSender::~NetlinkSender error - no appropriate method for net destruction implemented" << endl;
}

int NetlinkSender::OpenConnection(std::string addr, std::string port) {
	if (connected) {
		cout << "NetlinkSender::OpenConnection warning - already connected" << endl;
	}
	sockaddr_in sock_addr;
	sock = socket(AF_INET, SOCK_STREAM, 0);
	if(sock < 0) {
		cout << "NetlinkSender::OpenConnection error - couldnt create socket" << endl;
		return errno;
	}

	sock_addr.sin_family = AF_INET;
	sock_addr.sin_port = htons(atoi(port.c_str()));

	if ("localhost" == addr) {
		sock_addr.sin_addr.s_addr = htonl(0x7f000001);
	} else {
		if (0 == inet_aton(addr.c_str(), &(sock_addr.sin_addr))) {
			cout << "netlink_handler error: wrong server address" << endl;
			return 1;
		}
	}

	if (connect(sock, (struct sockaddr *)&sock_addr, sizeof(sock_addr)) < 0) {
		cout << "NetlinkSender::OpenConnection error - couldnt connect to remote host" << endl;
		cout << strerror(errno) << endl;
		return errno;
	}

	//Запускаем процесс взаимодействия с сервером
	pthread_t thread_id;
	pthread_create(&thread_id, NULL, &netlinksender_thread_function, this);
	pthread_create(&thread_id, NULL, &netlink_rcv_thread_function, this);

	connected = true;

	return 0;
}

int NetlinkSender::CloseConnection() {
	connected  = false;
	return 0;
}

bool NetlinkSender::Connected() const {
	return connected;
}

int NetlinkSender::Send(NetlinkMessage* msg) {
	return 0;
}


int NetlinkSender::thread_function() {
	while (1) {
		/* Lock the mutex before accessing the flag value.  */
		pthread_mutex_lock (&send_queue_mutex);
		while (0 == send_queue_size) {
			/* The flag is clear.  Wait for a signal on the condition
			variable, indicating that the flag value has changed.  When the
			signal arrives and this thread unblocks, loop and check the
			flag again.  */
			pthread_cond_wait (&send_queue_cv, &send_queue_mutex);
		}
		/* When we’ve gotten here, we know the flag must be set.  Unlock
		the mutex.*/
		pthread_mutex_unlock (&send_queue_mutex);

		pthread_mutex_lock(&to_send_mutex);
/*		send_message_struct sms = to_send.front();
		to_send.pop();*/
		pthread_mutex_unlock(&to_send_mutex);

/*		pack_n_send(sms);*/

		if (dump_enabled && dump_to_file) {
			dump_stream << "pop " << send_queue_size << endl;
		} else if (dump_enabled) {
			cout << "pop " << send_queue_size << endl;
		}
	}
	return 0;
}

int NetlinkSender::receive_thread_function() {
	unsigned char buf[1024];

	while(true) {
		int bytes_read = read(sock, buf, 1024);
		if(bytes_read <= 0) {
			cout << "NetlinkSender::receive_thread_function - server disconnected with code "<< errno << endl;
			break;
		}
		//cout << "Some bytes received " << bytes_read << endl;
/*		process_buffer(buf,bytes_read);*/
	}

	return 0;
}

int NetlinkSender::process_buffer(unsigned char* buf, int len) {
	return 0;
}

int NetlinkSender::process_message(unsigned char* buf, int len) {
	/*
	//Разбираем сообщение по его типу
	switch (msg_type) {
		case nlmt_text:
			process_string_message(buf, len);
			break;
		default:
			cout << "NetlinkSender::process_message atacked - unknown message type" << endl;
			cout << "Will now exit" << endl;
			exit(4);
	}*/
	return 0;
}

int NetlinkSender::process_string_message(unsigned char* buf, int len) {
	int req_size = 4+4+sizeof(long long)*2 + 1; //type+len+time_start+duration+zero char
	if (len < req_size) {
		cout << "NetlinkSender::process_string_message - frame is too short to be valid" << endl;
		exit(4);
	}

	long long *ptime = (long long*)(buf + 8);
	long long *pduration = (long long*)(buf + 16);
	buf[len-1] = 0; //На всякий случай завершаем буфер нулем
	char* pmessage = (char*)buf + 24;
	cout << "NetlinkSender::process_string_message info - message \"" << pmessage << "\" received at " << *ptime;
	if (-1 != *pduration) {
		cout << ". Valid for " << *pduration << endl;
	} else {
		cout << endl;
	}
	return 0;
}


void NetlinkSender::GetStatistics(unsigned int &out, unsigned int &in) {
	out = outcomming;
	in  = incomming;
}


int NetlinkSender::MkDump(bool enable) {
	if (dump_enabled) {
		//Дамп и так выводится. Закрываем существующий дескрптор
		if (dump_stream != cout) {
			dump_stream.close();
		}
	}
	dump_enabled = enable;
	dump_to_file = false;
	return 0;
}

int NetlinkSender::MkDump(bool enable, string file_name) {
	if (dump_enabled) {
		//Дамп и так выводится. Закрываем существующий дескриптор
		if (dump_stream != cout) {
			dump_stream.close();
		}
	}

	dump_enabled = enable;
	if (dump_enabled) {
		if ("cout" == file_name) {
			dump_to_file = false;
		} else {
			dump_to_file = true;
			dump_stream.open(file_name.c_str());
		}
	}
	return 0;
}

void* netlinksender_thread_function (void* thread_arg) {
	NetlinkSender* nls = (NetlinkSender*) thread_arg;
	nls->thread_function();

	return NULL;
}


void* netlink_rcv_thread_function (void* thread_arg) {
	NetlinkSender* nls = (NetlinkSender*) thread_arg;
	nls->receive_thread_function();

	return NULL;
}

