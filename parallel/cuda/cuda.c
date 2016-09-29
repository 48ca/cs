#include "uril/cuPrintf.cu"
#include <stdio.h>

__global__ void device_greetings(void) {
	cuPrintf("Hello, word from the device!\n");
}

int main(void) {
	printf("wasd\n");
	cudaPrintfInit();
	device_greetings<<<1,1>>>();
	cudaPrintfDisplay();
	cudaPrintfEnd();
	return 0;
}
