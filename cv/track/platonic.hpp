#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <string.h>

using std::vector;
using std::string;
using std::stod;
using std::cout;
using std::endl;

#include <opencv/opencv2.hpp>
using cv::Mat;

#include <sstream>
using std::stringstream;
void split(const string &s, char delim, vector<string> &elems);
vector<string> split(const string &s, char delim);
vecf apply(matrix_double a , vecf b);
matrix_double multiply(matrix_double a , matrix_double b);
void printvec(vector<auto> vec);

void setWorldToCameraMatrix(matrix_double& worldToCamera);

double valmap(string value);

int addPoint(double x, double y, double z);
int addPoint(string const& point);

int readFile(char* filename);

void setProjectionMatrix(const float &angleOfView, const float &near, const float &far, matrix_double &M);

void multiPointMatrix(const vecf& in, vecf& out, const matrix_double& M);

int setLines(int numV, int limit);

void drawShape(cv::Mat mat);
