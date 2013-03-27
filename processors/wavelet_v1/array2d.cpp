/*
 * array2d.cpp
 *
 *  Created on: 31.12.2012
 *      Author: drozdov
 */

#include <vector>
#include <iostream>
#include <fstream>
#include "array2d.h"

using namespace std;

CArray2d::CArray2d(int width, int height) {
	if (width<0 || height<0) {
		cout << "CArray2d::CArray2d error - negative array dimensions" << endl;
		return;
	}
	this->width = width;
	this->height = height;
	alloc_arrays();
}

CArray2d::CArray2d(CArray2d& a2d) {
	width  = a2d.width;
	height = a2d.height;
	dealloc_arrays();
	alloc_arrays();
}

CArray2d::~CArray2d() {
	dealloc_arrays();
}

double& CArray2d::operator()(int r, int c) {
	return arr[c][r];
}

void CArray2d::clear() {
	for (int i=0;i<width;i++) {
		for (int j=0;j<height;j++) {
			arr[i][j] = 0.0;
		}
	}
}

int CArray2d::get_width() {
	return width;
}

int CArray2d::get_height() {
	return height;
}

void CArray2d::resize(int width, int height) {
}

void CArray2d::dealloc_arrays() {
	for (int i=0;i<(int)arr.size();i++) {
		vector<double> tmp_v;
		arr[i].swap(tmp_v);
	}
	vector< vector<double> > tmp_v;
	arr.swap(tmp_v);
}

void CArray2d::alloc_arrays() {
	vector<double> tmp_v;
	tmp_v.resize(height, 0.0);
	arr.resize(width, tmp_v);
}

void CArray2d::save_to_file(std::string file_name) {
	ofstream f_arr(file_name.c_str(), ios::out|ios::app);
	for (vector< vector<double> >::iterator it = arr.begin(); it!=arr.end();it++) {
		for (vector<double>::iterator r_it=it->begin();r_it!=it->end();r_it++)
			f_arr << *r_it << " ";
		f_arr << endl;
	}
	f_arr.close();
	cout << "saved" << endl;
}

void CArray2d::clear_file(std::string file_name) {
	ofstream f_arr(file_name.c_str(), ios::trunc);
	f_arr.close();
}



