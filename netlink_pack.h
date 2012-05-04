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

#define MAX_QUEUE_SIZE 200

#define FRAME_START  0xFB
#define FRAME_END    0xFE
#define FRAME_ESCAPE 0xFC

//Максимальный размер принимающего буфера
#define MAX_RCV_BUF 10000
//Количество принимающих буферов
#define RCV_BUF_COUNT 10


enum ENetlinkMsgType {
	nlmt_link = 0,       // Управление потоком передачи данных
	nlmt_security = 1,   // Управление безопасностью. Смена паролей и режима шифрования
	nlmt_time = 2,       // Информация о переключении времени
	nlmt_trig = 3,       // Информация о переключении триггеров в текущем такте
	nlmt_tcl = 4,        // tcl-команда. Предполагает ответ сервера
	nlmt_trig_manage = 5,// Управление работой триггеров клиента
	nlmt_text = 6        // Передача текстового отчета от сервера клиенту. Может интерпретироваться по соглашению клиента и сервера
};

enum ENetlinkLinkType {
	nllt_version  = 1,         //Определение текущей версии клиента и сервера. Не предполагает дополнительных данных
	nllt_reset_buffers = 2,    //Сброс буферов. Не предполагает дополнительных данных
	nllt_close_connection = 3, //Корректное завершение соединения. Не предполагает дополнительных данных.
	nllt_sleep = 4,            //Усыпление клиента на заданное время. Позволяет снизить нагрузку на сервер. Дополнительные данные: длина 1, время в миллисекундах (int).
	nllt_samplerate = 5        //Установить частоту дискретизации
};



typedef struct _time_msg {
	long long current_time;
} time_msg;

typedef struct _trig_msg_item {
	int out_id;
	double value;
} trig_msg_item, *ptrig_msg_item;

typedef struct _trig_msg_trg_item {
	int trig_id;
	int out_count;
} trig_msg_trg_item, *ptrig_msg_trg_item;

typedef struct _netlink_msg {
	int msg_type;
	int msg_length;
	int trig_count;
} netlink_msg, *pnetlink_msg;

typedef struct _netlink_header {
	int msg_type;
	int msg_length;
} netlink_hdr;

class NetlinkOut;
class NetlinkTrigger;
class NetlinkMessage;
class NetlinkMessageTrig;

class NetlinkOut {
public:
	friend class NetlinkTrigger;
	NetlinkOut(int id, double value);
	void Dump(unsigned char* space) const;
	int RequiredSize();
private:
	int out_id;
	double out_value;
};


class NetlinkTrigger {
public:
	friend class NetlinkMessageTrig;
	NetlinkTrigger(int id);
	~NetlinkTrigger();
	void Add(NetlinkOut* out);
	void Add(int out_id, double value);
	int RequiredSize();
	void Dump(unsigned char* space);
private:
	std::vector<NetlinkOut*> outs;
	int trigger_id;
};


class NetlinkMessage {
public:
	virtual ~NetlinkMessage();
	virtual int RequiredSize() = 0;
	virtual void Dump(unsigned char* space) = 0;
	virtual void Clear() = 0;
};


class NetlinkMessageTrig : public NetlinkMessage {
public:
	NetlinkMessageTrig();
	~NetlinkMessageTrig();
	void Add(NetlinkTrigger* trigger);
	void Add(int triger_id, int out_id, double value);
	int RequiredSize();
	void Dump(unsigned char* space);
	void Clear();
private:
	std::vector<NetlinkTrigger*> triggers;
	int msg_type;
};

class NetlinkMessageTime : public NetlinkMessage {
public:
	NetlinkMessageTime(long long time);
	~NetlinkMessageTime();

	void SetTime(long long time);

	int RequiredSize();
	void Dump(unsigned char* space);
	void Clear();
private:
	long long current_time;
};

class NetlinkMessageSamplerate : public NetlinkMessage {
public:
	NetlinkMessageSamplerate(unsigned int samplerate);
	~NetlinkMessageSamplerate();

	void SetSamplerate(unsigned int samplerate);

	int RequiredSize();
	void Dump(unsigned char* space);
	void Clear();
private:
	unsigned int samplerate;
};

//Структура описывает буфер, готовый к отправке через Netlink
typedef struct _send_message_struct {
	unsigned char* data;
	int length;
} send_message_struct, *psend_message_struct;

class NetlinkSender {
public:
	NetlinkSender();
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
	std::queue<send_message_struct> to_send;

	int thread_function();
	void initialize_send_queue();
	void set_queue_size(int queue_size, bool signal_change);
	void incr_queue_size();
	void decr_queue_size();

	int pack_n_send(send_message_struct sms);

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
