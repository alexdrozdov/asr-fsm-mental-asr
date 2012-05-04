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

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include <pthread.h>

#include <iostream>

#include "netlink_pack.h"
#include "crc.h"


using namespace std;

enum EBufProcessState {
	bps_unknown = 0,
	bps_start   = 1,
	bps_body    = 2,
	bps_escape  = 3,
	bps_end     = 4
};


void* netlinksender_thread_function (void* thread_arg);
void* netlink_rcv_thread_function (void* thread_arg);


NetlinkOut::NetlinkOut(int id, double value) {
	out_id    = id;
	out_value = value;
}

void NetlinkOut::Dump(unsigned char* space) const {
	ptrig_msg_item itm = (ptrig_msg_item)space;
	itm->out_id = out_id;
	itm->value  = out_value;
}

int NetlinkOut::RequiredSize() {
	return sizeof(trig_msg_item);
}

////////////////////////////////////////////////////////////

NetlinkTrigger::NetlinkTrigger(int id) {
	trigger_id = id;
}

NetlinkTrigger::~NetlinkTrigger() {
	for (unsigned int i=0;i<outs.size();i++) {
		if (outs[i] != NULL) {
			delete outs[i];
		}
	}
}

void NetlinkTrigger::Add(NetlinkOut* out) {
	//Проверяем, что такого выхода не зарегистрировано
	vector<NetlinkOut*>::iterator it;
	for (it=outs.begin();it<outs.end();it++) {
		NetlinkOut* cur = *it;
		if (out->out_id == cur->out_id) {
			//Такой уже есть
			cout << "NetlinkTrigger::Add error - output with id=" << cur->out_id << " is already registered" << endl;
			return;
		}
	}

	outs.push_back(out);
}

void NetlinkTrigger::Add(int out_id, double value) {
	//Проверяем, что такого выхода не зарегистрировано
	vector<NetlinkOut*>::iterator it;
	for (it=outs.begin();it<outs.end();it++) {
		NetlinkOut* cur = *it;
		if (cur->out_id == out_id) {
			//Такой уже есть. Обновляем его
			cout << "NetlinkTrigger::Add warning - output with id=" << cur->out_id << " is already registered" << endl;
			cur->out_value = value;
			return;
		}
	}

	outs.push_back(new NetlinkOut(out_id,value));
}

int NetlinkTrigger::RequiredSize() {
	int nsize = sizeof(trig_msg_trg_item);

	vector<NetlinkOut*>::iterator it;
	for (it=outs.begin();it<outs.end();it++) {
		NetlinkOut* cur = *it;
		nsize += cur->RequiredSize();
	}

	return nsize;
}

void NetlinkTrigger::Dump(unsigned char* space) {
	unsigned char* pnt = space;

	ptrig_msg_trg_item ptrig_ptr = (ptrig_msg_trg_item)pnt;
	ptrig_ptr->trig_id   = trigger_id;
	ptrig_ptr->out_count = outs.size();

	pnt += sizeof(trig_msg_trg_item);
	vector<NetlinkOut*>::iterator it;
	for (it=outs.begin();it<outs.end();it++) {
		NetlinkOut* cur = *it;
		cur->Dump(pnt);
		pnt += cur->RequiredSize();
	}
}

NetlinkMessage::~NetlinkMessage() {
}

NetlinkMessageTrig::NetlinkMessageTrig() {
	msg_type = nlmt_trig;
}

NetlinkMessageTrig::~NetlinkMessageTrig() {
	for (unsigned int i=0;i<triggers.size();i++) {
		if (triggers[i] != NULL) {
			delete triggers[i];
		}
	}
}

void NetlinkMessageTrig::Add(NetlinkTrigger* trigger) {
	//Проверяем, что такого триггера не зарегистрировано
	vector<NetlinkTrigger*>::iterator it;
	for (it=triggers.begin();it<triggers.end();it++) {
		NetlinkTrigger* cur = *it;
		if (cur->trigger_id == trigger->trigger_id) {
			//Такой уже есть
			cout << "NetlinkMessageTrig::Add error - trigger with id=" << trigger->trigger_id << " is already registered" << endl;
			return;
		}
	}

	triggers.push_back(trigger);
}

void NetlinkMessageTrig::Add(int trigger_id, int out_id, double value) {
	//Ищем триггер с указанным id
	NetlinkTrigger* trigger = NULL;
	vector<NetlinkTrigger*>::iterator it;
	for (it=triggers.begin();it<triggers.end();it++) {
		NetlinkTrigger* cur = *it;
		if (cur->trigger_id == trigger_id) {
			trigger = cur;
			break;
		}
	}

	if (NULL == trigger) {
		//Триггер с таким id не найден. Создаем его
		trigger = new NetlinkTrigger(trigger_id);
		triggers.push_back(trigger);
	}

	trigger->Add(out_id,value);
}

int NetlinkMessageTrig::RequiredSize() {
	int nsize = sizeof(netlink_msg);

	vector<NetlinkTrigger*>::iterator it;
	for (it=triggers.begin();it<triggers.end();it++) {
		NetlinkTrigger* cur = *it;
		nsize += cur->RequiredSize();
	}

	return nsize;
}

void NetlinkMessageTrig::Dump(unsigned char* space) {
	unsigned char* pnt = space;

	pnetlink_msg pmsg_ptr = (pnetlink_msg)pnt;
	pmsg_ptr->msg_type   = msg_type;
	pmsg_ptr->msg_length = RequiredSize();
	pmsg_ptr->trig_count = triggers.size();

	pnt += sizeof(netlink_msg);
	vector<NetlinkTrigger*>::iterator it;
	for (it=triggers.begin();it<triggers.end();it++) {
		NetlinkTrigger* cur = *it;
		cur->Dump(pnt);
		pnt += cur->RequiredSize();
	}
}

void NetlinkMessageTrig::Clear() {
	vector<NetlinkTrigger*>::iterator it;
	for (it=triggers.begin();it<triggers.end();it++) {
		NetlinkTrigger* cur = *it;
		delete cur;
	}

	triggers.resize(0);
}

////////////////////////////////////////////////////////////////////


NetlinkMessageTime::NetlinkMessageTime(long long time) {
	current_time = time;
}

NetlinkMessageTime::~NetlinkMessageTime() {
}

void NetlinkMessageTime::SetTime(long long time) {
	current_time = time;
}

int NetlinkMessageTime::RequiredSize() {
	int nsize = sizeof(netlink_hdr);
	nsize += sizeof(long long);
	return nsize;
}

void NetlinkMessageTime::Dump(unsigned char* space) {
	unsigned char* pnt = space;

	netlink_hdr *pmsg_ptr = (netlink_hdr*)pnt;
	pmsg_ptr->msg_type   = nlmt_time;
	pmsg_ptr->msg_length = RequiredSize();

	pnt += sizeof(netlink_hdr);
	long long *ptime = (long long*)pnt;
	*ptime = current_time;
}

void NetlinkMessageTime::Clear() {
	current_time =0;
}
////////////////////////////////////////////////////////////////////

NetlinkMessageSamplerate::NetlinkMessageSamplerate(unsigned int samplerate) {
	this->samplerate = samplerate;
}

NetlinkMessageSamplerate::~NetlinkMessageSamplerate() {
}

void NetlinkMessageSamplerate::SetSamplerate(unsigned int samplerate) {
	this->samplerate = samplerate;
}

int NetlinkMessageSamplerate::RequiredSize() {
	int nsize = sizeof(netlink_hdr);
	nsize += sizeof(unsigned int)*2;
	return nsize;
}

void NetlinkMessageSamplerate::Dump(unsigned char* space) {
	unsigned char* pnt = space;

	netlink_hdr *pmsg_ptr = (netlink_hdr*)pnt;
	pmsg_ptr->msg_type   = nlmt_link;
	pmsg_ptr->msg_length = RequiredSize();
	pnt += sizeof(netlink_hdr);

	unsigned int* netlink_msg_subtype = (unsigned int*)pnt;
	*netlink_msg_subtype = nllt_samplerate;
	pnt += sizeof(unsigned int);

	unsigned int* psamplerate = (unsigned int*)pnt;
	*psamplerate = samplerate;
}

void NetlinkMessageSamplerate::Clear() {
	samplerate = 0;
}

////////////////////////////////////////////////////////////////////

NetlinkSender::NetlinkSender() {
	connected = false;

	pthread_mutex_init (&to_send_mutex, NULL);

	//Заполняем таблицу длин кодированных символов
	for (int i=0;i<256;i++) {
		coded_length[i] = 1;
	}
	coded_length[FRAME_START]  = 2;
	coded_length[FRAME_END]    = 2;
	coded_length[FRAME_ESCAPE] = 2;

	dump_enabled = false;
	dump_to_file = false;

	outcomming = 0;
	incomming  = 0;

	//Инициализация полей для приема сообщений от сервера
	buf_proc_state = 0;
	cur_buf = (unsigned char*)malloc(MAX_RCV_BUF);
	pcur_buf = cur_buf;
	cur_buf_usage = 0;
}

int NetlinkSender::OpenConnection(int addr, int port) {
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
	sock_addr.sin_port = htons(port); // или любой другой порт...
	sock_addr.sin_addr.s_addr = htonl(addr);
	if (connect(sock, (struct sockaddr *)&sock_addr, sizeof(sock_addr)) < 0) {
		cout << "NetlinkSender::OpenConnection error - couldnt connect to remote host" << endl;
		cout << strerror(errno) << endl;
		return errno;
	}

	//Включаем управление очередью
	initialize_send_queue();

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
	if (NULL == msg) {
		cout << "NetlinkSender::Send error - zero pointer received" << endl;
	}

	//Извлекаем данные, которые необходимо передать
	send_message_struct sms;
	sms.length = msg->RequiredSize();
	sms.data   = (unsigned char*)malloc(sms.length);
	msg->Dump(sms.data);

	//Записываем эти данные в очередь на отправку
	pthread_mutex_lock(&to_send_mutex);
	to_send.push(sms);
	pthread_mutex_unlock(&to_send_mutex);

	//Увеличиваем размер очереди
	incr_queue_size();

	if (dump_enabled && dump_to_file) {
		dump_stream << "push " << send_queue_size << endl;
	} else if (dump_enabled) {
		cout << "push " << send_queue_size << endl;
	}

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
		send_message_struct sms = to_send.front();
		to_send.pop();
		pthread_mutex_unlock(&to_send_mutex);
		//Уменьшаем размер очереди
		decr_queue_size();

		pack_n_send(sms);

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
		process_buffer(buf,bytes_read);
	}

	return 0;
}

int NetlinkSender::process_buffer(unsigned char* buf, int len) {
	unsigned char* pbuf = buf;

	//if (dump_instream) {
	//	cout << "NetlinkSender::process_buffer: " << len << endl;
	//	cout << "Initial state is " << buf_proc_state << endl;

	//	char ch[6];
	//	for (int i=0;i<len;i++) {
	//		sprintf(ch,"0x%X",buf[i]);
	//		cout << ch << " ";
	//	}
	//	cout << endl;
	//}

	int i = 0;
	while (i<len) {
		switch (buf_proc_state) {
			case bps_unknown:
				//cout << "bps_unknown" << endl;
				if (FRAME_START == *pbuf) {
					//Из неизвестного состояния перешли в начало фрейма
					buf_proc_state = bps_start;
				} else {
					pbuf++;
					i++;
				}
				break;

			case bps_start:
				//cout << "bps_start" << endl;
				//Безусловно переходим к обработке тела сообщения
				buf_proc_state = bps_body;
				pbuf++;
				i++;

				pcur_buf = cur_buf;
				cur_buf_usage = 0;
				break;

			case bps_body:
				//cout << "bps_body" << endl;
				if (FRAME_ESCAPE == *pbuf) {
					pbuf++;
					i++;
					buf_proc_state = bps_escape;
					break;
				} else if (FRAME_START == *pbuf) {
					cout << "NetlinkSender::process_buffer atacked - frame start in message body" << endl;

					cout << "Position " << i << endl;

					cout << "Will now exit" << endl;
					exit(4);
				} else if (FRAME_END == *pbuf) {
					//Прием буфера закончился. Обрабатываем принятый буфер
					buf_proc_state = bps_unknown;

					if (len < 8) {
						//Фрейм имеет правильную струткуру, но содержит менее 8 байт
						//В нем гарантированно отсутствует тип сообщения и длина
						//Проверить правильность данных в этом буфере невозможно
						cout << "NetlinkSender::process_buffer atacked - frame is too short to be valid" << endl;
						exit(4);
					}
					process_message(cur_buf,cur_buf_usage);
					pbuf++;
					i++;
					break;
				}
				//Обычный символ. Записываем его в буфер декодированного сообщения
				*pcur_buf = *pbuf;
				pcur_buf++;
				cur_buf_usage++;
				i++;
				pbuf++;
				if (MAX_RCV_BUF <= cur_buf_usage) {
					cout << "NetlinkSender::process_buffer atacked - frame length overflow" << endl;
					cout << "Will now exit" << endl;
					exit(4);
				}
				break;
			case bps_escape:
				//cout << "bps_escape" << endl;
				{
					unsigned char c = 0;
					if (0xCB == *pbuf) {
						c = FRAME_START;
					} else if (0xCE == *pbuf) {
						c = FRAME_END;
					} else if (FRAME_ESCAPE == *pbuf) {
						c = FRAME_ESCAPE;
					} else {
						cout << "NetlinkSender::process_buffer - unknown escape symbol" << endl;
						cout << "Will now exit" << endl;
						exit(4);
					}
					*pcur_buf = c;
					pcur_buf++;
					cur_buf_usage++;
					i++;
					pbuf++;
					buf_proc_state = bps_body;
					if (MAX_RCV_BUF <= cur_buf_usage) {
						cout << "NetlinkSender::process_buffer atacked - frame length overflow" << endl;
						cout << "Will now exit" << endl;
						exit(4);
					}
				}
				break;
		}
	}
	return 0;
}

int NetlinkSender::process_message(unsigned char* buf, int len) {
	int msg_type = *(int*)buf;
	int msg_len  = *(int*)(buf+4);

	//Проверяем длину сообщения
	if (msg_len != len-2) {
		cout << "NetlinkSender::process_message atacked - wrong message length specified" << endl;
		cout << "Will now exit" << endl;
		exit(4);
	}
	//Длина сообщения, заданная в самом сообщении совпадает с полученной длиной фрейма

	//Разбираем сообщение по его типу
	switch (msg_type) {
		//case nlmt_link:
		//	return process_link_msg(buf, len);
		//	break;
		//case nlmt_security:
		//	return process_sec_msg(buf, len);
		//	break;
		//case nlmt_time:
		//	return process_time_msg(buf, len);
		//	break;
		//case nlmt_trig:
		//	return process_trig_msg(buf, len);
		//	break;
		//case nlmt_tcl:
		//	break;
		case nlmt_text:
			process_string_message(buf, len);
			break;
		default:
			cout << "NetlinkSender::process_message atacked - unknown message type" << endl;
			cout << "Will now exit" << endl;
			exit(4);
	}
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

int NetlinkSender::pack_n_send(send_message_struct sms) {
	//Определяем длину сообщения после его кодирования
	int msg_len = 0;
	for (int i=0;i<sms.length;i++) {
		msg_len += coded_length[sms.data[i]];
	}
	msg_len += 4; // FRAME_START + CRC-16 + FRAME_END

	unsigned char *coded_msg = (unsigned char*)malloc(msg_len);
	unsigned char *pcoded_msg = coded_msg;

	*pcoded_msg = FRAME_START;
	pcoded_msg++;

	unsigned short crc = CRC_INIT;

	for (int i=0;i<sms.length;i++) {
		unsigned char c = sms.data[i];
		CRC(crc, c);
		if (FRAME_START == c) {
			pcoded_msg[0] = FRAME_ESCAPE;
			pcoded_msg[1] = 0xCB;
			pcoded_msg += 2;
			continue;
		}
		if (FRAME_END == c) {
			pcoded_msg[0] = FRAME_ESCAPE;
			pcoded_msg[1] = 0xCE;
			pcoded_msg += 2;
			continue;
		}
		if (FRAME_ESCAPE == c) {
			pcoded_msg[0] = FRAME_ESCAPE;
			pcoded_msg[1] = FRAME_ESCAPE;
			pcoded_msg += 2;
			continue;
		}
		pcoded_msg[0] = c;
		pcoded_msg++;
	}
	free(sms.data);

	coded_msg[msg_len-3] = 0;//(crc&0xFF00) >> 8;
	coded_msg[msg_len-2] = 0;//crc & 0xFF;
	coded_msg[msg_len-1] = FRAME_END;

	if (dump_enabled && dump_to_file) {
		char ch[6];
		for (int i=0;i<msg_len;i++) {
			sprintf(ch,"0x%X",coded_msg[i]);
			dump_stream << ch << " ";
		}
		dump_stream << endl;
	} else if (dump_enabled) {
		char ch[6];
		for (int i=0;i<msg_len;i++) {
			sprintf(ch,"0x%X",coded_msg[i]);
			cout << ch << " ";
		}
		cout << endl;
	}


	int send_res = send(sock, coded_msg, msg_len, 0);//MSG_DONTWAIT);
	free(coded_msg);
	if (-1 == send_res) {
		if (EAGAIN == errno) {
			cout << "NetlinkSender::pack_n_send error - socket overflow" << endl;
		} else {
			cout << "NetlinkSender::pack_n_send error - " << errno << endl;
			cout << strerror(errno) << endl;
			cout << "Will now exit" << endl;
			exit(3);
		}
	}

	outcomming += msg_len;

	return 0;
}

void NetlinkSender::GetStatistics(unsigned int &out, unsigned int &in) {
	out = outcomming;
	in  = incomming;
}

void NetlinkSender::set_queue_size(int queue_size, bool signal_change) {
	/* Lock the mutex before accessing the flag value.  */
	pthread_mutex_lock(&send_queue_mutex);

	/* Set the flag value, and then signal in case thread_function is
	blocked, waiting for the flag to become set.  However,
	thread_function can’t actually check the flag until the mutex is
	unlocked.  */

	send_queue_size = queue_size;
	if (signal_change) {
		pthread_cond_signal(&send_queue_cv);
	}
	/* Unlock the mutex.  */
	pthread_mutex_unlock(&send_queue_mutex);
}

void NetlinkSender::incr_queue_size() {
	bool overflow = false;
	/* Lock the mutex before accessing the flag value.  */
	pthread_mutex_lock(&send_queue_mutex);

	if (send_queue_size >= MAX_QUEUE_SIZE) {
		overflow = true;
	} else {
		send_queue_size++;
		pthread_cond_signal(&send_queue_cv);
	}
	pthread_mutex_unlock(&send_queue_mutex);

	if ( overflow ) {
		cout << "NetlinkSender error - message queue overflow. Will now exit" << endl;
		exit(3);
	}
}

void NetlinkSender::decr_queue_size() {
	/* Lock the mutex before accessing the flag value.  */
	pthread_mutex_lock(&send_queue_mutex);

	if (send_queue_size > 0) {
		send_queue_size--;
	}
	pthread_mutex_unlock(&send_queue_mutex);
}


void NetlinkSender::initialize_send_queue() {
	pthread_mutex_init (&send_queue_mutex, NULL);
	pthread_cond_init (&send_queue_cv, NULL);

	send_queue_size = 0;
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

