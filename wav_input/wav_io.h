/*
 * wav_io.h
 *
 *  Created on: 01.08.2011
 *      Author: drozdov
 */

#ifndef WAV_IO_H_
#define WAV_IO_H_

#include <stdlib.h>
#include <stdio.h>
#include <string>

typedef struct {
/* File header */
  char riff[4];
  long filesize;
  char rifftype[4];
} RiffHeader;

typedef struct {
  char chunk_id[4];
  long chunksize;
} Chunk;

typedef struct {
  short wFormatTag;
  short nChannels;
  long nSamplesPerSec;
  long nAvgBytesPerSec;
  short nBlockAlign;
  short wBitsPerSample;
} WAVEFORMAT;

typedef struct {
  WAVEFORMAT wf;
  //short wBitsPerSample;
} PCMWAVEFORMAT;

typedef struct {
  RiffHeader header;
  Chunk ch_format;
  PCMWAVEFORMAT format;
  Chunk ch_data;
} wav_file_header;

class CWavIo {
public:
	CWavIo(std::string filename);
	bool open();
	bool is_opened();
	bool close();
	unsigned int getpos();
	unsigned int seek(unsigned int pos);
	unsigned int size();
	unsigned int read(unsigned char* buf, unsigned int count);


	int get_defsamplerate();
	int get_bitspersample();
private:
	std::string wav_filename;
	bool bopened;
	FILE *wfile;
	wav_file_header wheader;
};


#endif /* WAV_IO_H_ */
