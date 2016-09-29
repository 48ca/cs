#include<iostream>
#include"include.h"

int main(int argc, char** argv) {
	int i;

	for(i=0;i<argc;i++) {
		std::cout << argv[i] << std::endl;
	}

	int a = 2;
	int b = 3;
	std::cout << dank::wow(2,3) << std::endl;
	return 0;
}
