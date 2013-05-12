/*
 * netlink_pack.h
 *
 *  Created on: 04.07.2011
 *      Author: drozdov
 */

#ifndef NETLINK_PACK_H_
#define NETLINK_PACK_H_

#include <pthread.h>

#include <string>
#include <vector>
#include <queue>
#include <fstream>
#include <stdint.h>

#include <p2vera.h>
#include <p2message.h>
#include <p2stream.h>

#include "dsp_stream.pb.h"

typedef struct _trig_msg_item {
	int32_t out_id;
	double value;
} trig_msg_item, *ptrig_msg_item;

class NetlinkMessage : public IP2VeraMessage {
public:
	virtual ~NetlinkMessage();
	virtual void Clear() = 0;

	virtual bool get_data(std::string& str) const;
	virtual int get_data(void* data, int max_data_size) const;
	virtual int get_data_size() const;
	virtual bool set_data(void* data, int data_size);
	virtual bool set_data(std::string &str);
protected:
	dsp::dsp_package pkg;
};


class NetlinkMessageTrig : public NetlinkMessage {
public:
	NetlinkMessageTrig();
	virtual ~NetlinkMessageTrig();
	void Add(int triger_id, int out_id, double value);
	void Clear();
};

class NetlinkMessageTime : public NetlinkMessage {
public:
	NetlinkMessageTime(long long time);
	virtual ~NetlinkMessageTime();

	void SetTime(long long time);
	void Clear();
};

class NetlinkMessageSamplerate : public NetlinkMessage {
public:
	NetlinkMessageSamplerate(unsigned int samplerate);
	virtual ~NetlinkMessageSamplerate();

	void SetSamplerate(unsigned int samplerate);
	void Clear();
};


class NetlinkSender {
public:
	NetlinkSender();
	virtual ~NetlinkSender();
	int OpenConnection(std::string addr, std::string port);
	bool Connected() const;
	int CloseConnection();

	int Send(NetlinkMessage* msg);

	virtual int MkDump(bool enable);
	virtual int MkDump(bool enable, std::string file_name);
	virtual void GetStatistics(unsigned int &out, unsigned int &in);
private:
	int send_queue_size;
	pthread_mutex_t send_queue_mutex;
	pthread_cond_t  send_queue_cv;

	pthread_mutex_t to_send_mutex;

	int thread_function();
	void initialize_send_queue();
	void set_queue_size(int queue_size, bool signal_change);
	void incr_queue_size();
	void decr_queue_size();

	friend void* netlinksender_thread_function (void* thread_arg);
	friend void* netlink_rcv_thread_function (void* thread_arg);

	int sock;
	bool connected;

	int coded_length[256];

	bool touched; //Признак того, что триггер уже добавлен в динамическое дерево
	bool dump_enabled; //Триггер должен выводить входные и выходные парамеры при каждом вызове ProcessAnchestors
	bool dump_to_file;
	std::ofstream dump_stream; //Поток, в который выводится дамп

	unsigned int outcomming;
	unsigned int incomming;

	//Методы и члены, обеспечивающие обратный канал передачи данных от сервера
	int receive_thread_function();
	int process_buffer(unsigned char* buf, int len);
	int process_message(unsigned char* buf, int len);
	int buf_proc_state;

	unsigned char *cur_buf; //Текущий буфер для декодируемого сообщения
	unsigned char *pcur_buf;
	int cur_buf_usage; //Количество использованных ячеек буфера

	int process_string_message(unsigned char* buf, int len);
};

extern NetlinkMessageTrig* nmt;
extern NetlinkMessageTime* nmtt;
extern NetlinkSender*      nls;
extern NetlinkMessageSamplerate* nlsr;



#endif /* NETLINK_PACK_H_ */
