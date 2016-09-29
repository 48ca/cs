#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cmath>
#include <cstdlib>
#include "split/string_split.h"
#include <string.h>

#define SCALAR 1

using std::vector;
using std::string;
using std::stod;
using std::cout;
using std::endl;

typedef vector<double> vecf;
typedef vector<vector<vecf>> matrix_vecf;
typedef vector<vecf> matrix_double;
vector<vecf> points;
vector<vecf> lines;

void printvec(vector<auto> vec)
{
	for(const auto& el : vec)
	{
		cout << el << " ";
	}
	cout << endl;
}

#define PHI 1.6180339887
#define INV_PHI 0.61803398875
double valmap(string value) {
	if(value == "+PHI") {
		return PHI;
	}
	else if(value == "-PHI") {
		return -PHI;
	}
	else if(value == "+INV_PHI") {
		return INV_PHI;
	}
	else if(value == "-INV_PHI") {
		return -INV_PHI;
	}
	return stod(value);
}

int addPoint(string const& point) {
	vector<string> coordinates = split(point,',');
	vector<double> p;
	for(string const& value: coordinates) {
		p.push_back(SCALAR * valmap(value));
	}
	points.push_back(p);
	return 0;
}

int readFile(char* filename) {
	std::ifstream infile(filename);
	string line;
	int num = 0;
	while(std::getline(infile, line)) {
		if(line.at(0) == '#') continue;
		if(line == ";;") continue;
		vector<string> tokens = split(line,';');
		for(string const& value: tokens) {
			addPoint(value);
			++num;
		}
		
	}
	return num;
}

void setProjectionMatrix(const float &angleOfView, const float &near, const float &far, matrix_double &M) {
	float scale = 1 / tan(angleOfView * .5 * M_PI / 180);
	M[0][0] = scale;
	M[1][1] = scale;
	M[2][2] = -far / (far - near);
	M[3][2] = -far * near / (far - near);
	M[2][3] = -1;
	M[3][3] = 0;
}

void multiPointMatrix(const vecf& in, vecf& out, const matrix_double& M)
{
	double x = in[0] * M[0][0] + in[1] * M[1][0] + in[2] * M[2][0] + M[3][0];
	double y = in[0] * M[0][1] + in[1] * M[1][1] + in[2] * M[2][1] + M[3][1];
	double z = in[0] * M[0][2] + in[1] * M[1][2] + in[2] * M[2][2] + M[3][2];
	double w = in[0] * M[0][3] + in[1] * M[1][3] + in[2] * M[2][3] + M[3][3];
	x/=w;
	y/=w;
	z/=w;
	out[0] = x;
	out[1] = y;
	out[2] = z;
}

int main(int argc, char** argv) {

	const uint32_t width = 512;
	const uint32_t height = 512;

	unsigned char *buffer = new unsigned char[width*height];

	matrix_vecf mat = *(new matrix_vecf(height));
	matrix_double m_proj = *(new matrix_double(4));
	register int i, j;
	for(i=0;i<4;++i)
	{
		m_proj[i] = *(new vector<double>(4));
	}
	for(i=0;i<height;++i)
	{
		mat[i]= *(new vector<vecf>(width));
		for(j=0;j<4;++j)
		{
			mat[i][j] = *(new vecf(3));
		}
	}
	int numVertices;
	if(argc != 2) {
		numVertices = readFile((char*)"cube.txt");
		// cerr << "invalid number of arguments" << endl;
		// return 1;
	} else {
		numVertices = readFile(argv[1]);
	}

	/*
	for(vector<double> const& v1: points) {
		cout << "P:";
		for(double const& v2: v1) {
			cout << " " << v2;
		}
		cout << endl << endl;
	}
	*/

	setProjectionMatrix(90, .1, 100, m_proj);
	memset(buffer, 0x0, width * height);
	for(i=0;i<numVertices;i++)
	{
		vecf cam(3), projectedvert(3);
		// multiPointMatrix(points[i], cam, /* worldToCamera */);
		multiPointMatrix(points[i], projectedvert, m_proj);
		printvec(points[i]);
		printvec(projectedvert);

		if (projectedvert[0] < -1 || \
			projectedvert[0] > 1 || \
			projectedvert[1] < -1 || \
			projectedvert[1] > 1)
			continue;
		uint32_t x = std::min(width - 1, (uint32_t)((projectedvert[0] + 1) * 0.5 * width)); 
		uint32_t y = std::min(height - 1, (uint32_t)((1 - (projectedvert[1] + 1) * 0.5) * height));
		// int x = width * abs(projectedvert[0]);
		// int y = height * abs(projectedvert[1]);
		cout << x << " " << y << endl;
		buffer[y * width + x] = 255;
	}
	std::ofstream ofs;
	ofs.open("out.ppm");
	ofs << "P5\n" << width << " " << height << "\n255\n";
	ofs.write((char*)buffer, width * height);
	ofs.close();
	delete [] buffer;

	return 0;
}
