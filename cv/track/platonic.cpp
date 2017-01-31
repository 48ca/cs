#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <string.h>

#define SCALAR 1

#define MAX_DOUBLE 0xFFFFFF

#define DELTA_T 0.001

#define LINE_LIMIT -1

#define DEBUG 0

#define NEAR .1
#define FAR 100
#define FOV 80

#define WIDTH 800
#define HEIGHT 800

#define FRAMES 1

#define DO_LINES 1

using std::vector;
using std::string;
using std::stod;
using std::cout;
using std::endl;

#include <sstream>
using std::stringstream;
void split(const string &s, char delim, vector<string> &elems) {
    stringstream ss;
    ss.str(s);
    string item;
    while (getline(ss, item, delim)) {
        elems.push_back(item);
    }
}

vector<string> split(const string &s, char delim) {
    vector<string> elems;
    split(s, delim, elems);
    return elems;
}

typedef vector<double> vecf;
typedef vector<vector<vecf>> matrix_vecf;
typedef vector<vecf> matrix_double;
vector<vecf> points;
vector<vecf> lines;

#define DO_ROTATE 1
#define THETA_X 2* M_PI
#define THETA_Y 2* M_PI
#define THETA_Z 2* M_PI

matrix_double Rx;
matrix_double Ry;
matrix_double Rz;

vecf apply(matrix_double a , vecf b) {
	register int r;
	register int rp, cp;
	vecf tmp = {0, 0, 0};
	for(r=0;r<3;++r) {
		register double tot = 0;
		for(cp=0,rp=0;rp<3;++rp,++cp) {
			tot += a[r][cp] * b[rp];
		}
		tmp[r] = tot;
	}
	return tmp;
}

matrix_double multiply(matrix_double a , matrix_double b) {
	register int r, c;
	register int rp, cp;
	for(r=0;r<4;++r) {
		for(c=0;c<4;++c) {
			register double tot = 0;
			for(cp=0,rp=0;rp<4;++rp,++cp) {
				tot += a[r][cp] * b[rp][c];
			}
			b[r][c] = tot;
		}
	}
	return b;
}

void printvec(vector<auto> vec)
{
	for(const auto& el : vec)
	{
		cout << el << " ";
	}
	cout << endl;
}

void setWorldToCameraMatrix(matrix_double& worldToCamera) {
	// worldToCamera[3]
	// worldToCamera[0][2] = .5;
	// worldToCamera[2][0] = .5;
	worldToCamera[0][0] = 1;
	worldToCamera[1][1] = 1;
	worldToCamera[2][2] = 1;
	worldToCamera[3][3] = 1;
	worldToCamera[3][0] = 0;
	worldToCamera[3][1] = -.5;
	worldToCamera[3][2] = -4;
	if(DEBUG) {
		cout << " ---- " << endl;
		printvec(worldToCamera[0]);
		printvec(worldToCamera[1]);
		printvec(worldToCamera[2]);
		printvec(worldToCamera[3]);
		cout << endl << " ---- "  << endl;
	}
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

int addPoint(double x, double y, double z) {
	vector<double> p = {x, y, z};
	points.push_back(p);
	return 0;
}
int addPoint(string const& point) {
	vector<string> coordinates = split(point,',');
	vector<double> p;
	for(string const& value: coordinates) {
		p.push_back(SCALAR * valmap(value));
	}
	if(DO_ROTATE) {
		p = apply(Rx, p);
		p = apply(Ry, p);
		p = apply(Rz, p);
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
	float scale = 1.0 / tan(angleOfView * .5 * M_PI / 180.0);
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
	out[0] = x/w;
	out[1] = y/w;
	out[2] = z/w;
}

vector<vector<int>> drawnLines;

int setLines(int numV, int limit) {
	register int num = 0, lines = 0;
	register double x, y, z, t, px, py, pz;
	register int v1, v2;
	vecf p1, p2;
	for(v1=0;v1<numV;++v1) {
		p1 = points[v1];
		double min_dist = MAX_DOUBLE;
		double tmp_d;
		vector<int> vec_min_v = {};
		for(v2=0;v2<numV;++v2) {
			if(v1 == v2) continue;
			p2 = points[v2];
			px = p2[0] - p1[0];
			py = p2[1] - p1[1];
			pz = p2[2] - p1[2];
			tmp_d = px*px + py*py + pz*pz;
			if(abs(tmp_d - min_dist) < .05) {
				vec_min_v.push_back(v2);
			}
			else if(tmp_d < min_dist) {
				vec_min_v = {v2};
				min_dist = tmp_d;
			}
		}
		for(const int& min_v : vec_min_v) {
			vector<int> new_v = {v1 < min_v ? v1 : min_v, v1 > min_v ? v1 : min_v, (int)min_dist};
			drawnLines.push_back(new_v);
			x = points[min_v][0];
			y = points[min_v][1];
			z = points[min_v][2];
			px = p1[0] - x;
			py = p1[1] - y;
			pz = p1[2] - z;
			for(t=0;t<1;t+=DELTA_T) {
				addPoint(x + t * px, y + t * py, z + t * pz);
				++num;
			}
			if(limit >= 0 && ++lines >= limit) return num;
		}
	}
	return num;
}

int main(int argc, char** argv) {

	const uint32_t width = WIDTH;
	const uint32_t height = HEIGHT;

	unsigned char *buffer = new unsigned char[width*height];

	matrix_double m_proj = *(new matrix_double(4));
	matrix_double worldToCamera = *(new matrix_double(4));
	register int i, j;
	for(i=0;i<4;++i)
	{
		m_proj[i] = *(new vecf(4));
		worldToCamera[i] = *(new vecf(4));
	}

	setProjectionMatrix(FOV, NEAR, FAR, m_proj);
	setWorldToCameraMatrix(worldToCamera);

	double tx = THETA_X;
	double ty = THETA_Y;
	double tz = THETA_Z;

	points = {};

	Rx = {
		{1, 0, 0},
		{0, cos(tx), -sin(tx)},
		{0, sin(tx), cos(tx)}
	};
	Ry = {
		{cos(ty), 0, sin(ty)},
		{0, 1, 0},
		{-sin(ty), 0, cos(ty)}
	};
	Rz = {
		{cos(tz), -sin(tz), 0},
		{sin(tz), cos(tz), 0},
		{0, 0, 1}
	};

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

	// cout << "num: " << numVertices << endl;
	int d = DO_LINES ? setLines(numVertices, LINE_LIMIT) : 0;
	// cout << "added " << d << " vertices" << endl;

	memset(buffer, 0x0, width * height);
	int tot = numVertices + d;
	for(i=tot-1;i>=0;--i)
	{
		vecf cam(3), projectedvert(3);
		multiPointMatrix(points[i], cam, worldToCamera);
		multiPointMatrix(cam, projectedvert, m_proj);
		/*
		cout << "start" << endl;
		printvec(points[i]);
		printvec(cam);
		printvec(projectedvert);
		cout << "end" << endl;
		*/

		if (projectedvert[0] < -1 ||
			projectedvert[0] > 1 ||
			projectedvert[1] < -1 ||
			projectedvert[1] > 1)
			continue;
		uint32_t x = (projectedvert[0] + 1) * 0.5 * width; 
		uint32_t y = (1 - (projectedvert[1] + 1) * 0.5) * height;
		// int x = width * abs(projectedvert[0]);
		// int y = height * abs(projectedvert[1]);
		// cout << "X: " << x << " Y: " << y << endl;
		buffer[y * width + x] = i < numVertices ? 255 : 125;
	}

	return buffer;
}
