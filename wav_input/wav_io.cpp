/*
 * wav_io.cpp
 *
 *  Created on: 01.08.2011
 *      Author: drozdov
 */

#include <iostream>
#include "wav_io.h"


using namespace std;


CWavIo::CWavIo (string filename) {
	wav_filename = filename;
	bopened = false;
	wfile = NULL;
}

bool CWavIo::open() {
	if (bopened) {
		//Закрываем файл. Перечитываем его заново
		close();
	}

	if( ( wfile=fopen(wav_filename.c_str(), "rb") ) == NULL ) {
		cout << "CWavIo::open error: failed to open wav file " << wav_filename << endl;
		return 2;
	}

	bopened = true;

	fread( &wheader, sizeof(wav_file_header), 1, wfile);
	return 0;
}

bool CWavIo::is_opened() {
	return bopened;
}

bool CWavIo::close() {
	if (bopened) {
		fclose(wfile);
	}
	return false;
}

unsigned int CWavIo::getpos() {
	if (! bopened) {
		return false;
	}

	return ftell(wfile) - sizeof(wav_file_header);
}

unsigned int CWavIo::seek(unsigned int pos) {
	if (!bopened) {
		return 0;
	}

	fseek(wfile, pos+sizeof(wav_file_header),SEEK_SET);
	return 0;
}

unsigned int CWavIo::size() {
	return wheader.ch_data.chunksize;
}

unsigned int CWavIo::read(unsigned char* buf, unsigned int count) {
	if (!bopened) {
		return 0;
	}
	//cout << "requested read count " << count << endl;
	int r = fread(buf,1,count,wfile);
	//cout << "read count " << r << endl;
	return r;
}

int CWavIo::get_defsamplerate() {
	return wheader.format.wf.nSamplesPerSec;
}

int CWavIo::get_bitspersample() {
	return wheader.format.wf.wBitsPerSample;
}


