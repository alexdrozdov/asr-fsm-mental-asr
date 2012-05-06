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
#include <stdint.h>

typedef struct {
/* File header */
  char riff[4];
  int32_t filesize;
  char rifftype[4];
} RiffHeader;

typedef struct {
  char chunk_id[4];
  int32_t chunksize;
} Chunk;

typedef struct {
  int16_t wFormatTag;
  int16_t nChannels;
  int32_t nSamplesPerSec;
  int32_t nAvgBytesPerSec;
  int16_t nBlockAlign;
  int16_t wBitsPerSample;
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
	bool is_opened() const;
	bool close();
	unsigned int getpos();
	unsigned int seek(unsigned int pos);
	unsigned int size() const;
	unsigned int read(unsigned char* buf, unsigned int count);


	int get_defsamplerate() const;
	int get_bitspersample() const;
private:
	std::string wav_filename;
	bool bopened;
	FILE *wfile;
	wav_file_header wheader;
};


#endif /* WAV_IO_H_ */
