/*
 * array2d.h
 *
 *  Created on: 31.12.2012
 *      Author: drozdov
 */

#ifndef ARRAY2D_H_
#define ARRAY2D_H_

#include <vector>
#include <string>

class CArray2d {
public:
	CArray2d(int width, int height);
	CArray2d(CArray2d&);
	virtual ~CArray2d();
	virtual double& operator()(int r, int c);
	virtual void clear();
	virtual int get_width();
	virtual int get_height();
	virtual void resize(int width, int height);
	virtual void clear_file(std::string file_name);
	virtual void save_to_file(std::string file_name);
private:
	std::vector< std::vector<double> > arr;
	int width;
	int height;

	virtual void dealloc_arrays();
	virtual void alloc_arrays();
};

#endif /* ARRAY2D_H_ */
