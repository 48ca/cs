#include <stdlib.h>
#include <stdio.h>

#define M 200000

double* display_colors;
double* colors;

int main() {
	display_colors = (double*)malloc(sizeof(double) * M * M * 3);
	colors = (double*)malloc(sizeof(double) * M * M);
	printf("Passed\n");
	return 0;
}
