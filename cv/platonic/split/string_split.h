#ifndef STRING_SPLIT_H

#define STRING_SPLIT_H

#include <string>
#include <sstream>
#include <vector>

using namespace std;

void split(const string &s, char delim, vector<string> &elems);
vector<string> split(const string &s, char delim);

#endif
