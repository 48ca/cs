#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#define TREE 2
#define FIRE 1
#define FIRE_STARTED 3
#define MISSING 0

void wait(unsigned int ms) {
	struct timeval t;
	gettimeofday(&t,NULL);
	double tf = t.tv_sec + (t.tv_usec + ms*1000.0) / 1000000.0 ;
	gettimeofday(&t,NULL);
	while(t.tv_sec + (t.tv_usec) / 1000000.0 < tf) gettimeofday(&t,NULL);
}

void printff(int* ffm,int width) {

	system("clear");

	register int i,j;
	for(i=0;i<width;i++) {
		for(j=0;j<width;j++) {
			switch(*(ffm + width * i + j)) {
				case TREE:
					printf("X");
					break;
				case FIRE:
					printf("\x1B[33m*\x1B[0m");
					break;
				case FIRE_STARTED:
					printf("\x1B[33m&\x1B[0m");
					break;
				default:
					printf("-");
					break;
			}
		}
		printf("\n");
	}

}

void burn(int* ptr) {
	if(*ptr == TREE) {
		*ptr = FIRE_STARTED;
	}
}

int tick(int* ffm, int width) {
	register int i,j,count;
	for(i=0;i<width;i++) {
		for(j=0;j<width;j++) {
			if(*(ffm + i * width + j) == FIRE) {
				*(ffm + i * width + j) = MISSING;
				if(i > 0) {
					int* ptr = ffm + (i-1) * width + j;
					burn(ptr);
				}
				if(i < width - 1) {
					int* ptr = ffm + (i+1) * width + j;
					burn(ptr);
				}
				if(j > 0) { 
					int* ptr = ffm + i * width + j - 1;
					burn(ptr);
				}
				if(j < width - 1) {
					int* ptr = ffm + i * width + j + 1;
					burn(ptr);
				}
			}
		}
	}

	count = 0;
	for(i=0;i<width;i++) {
		for(j=0;j<width;j++) {
			if(*(ffm + width * i + j) == FIRE_STARTED) {
				*(ffm + width * i + j) = FIRE;
				count++;
			}
		}
	}
	return count;
}

int main(int argc, char* argv[]) {

	double prob;
	int width = 50;
	int* ffm;

	srand(077777U);

	if(argc > 1) {
		prob = atof(argv[1]);
	} else {
		// printf("Supply a number from 0 to 1.\n");
		return 1;
	}

	ffm = malloc(sizeof(int) * width * width);
	register int i,j;
	for(i=0;i<width*width;i++) {
		*(ffm + i) = MISSING;
	}
	for(i=0;i<width;i++) {
		for(j=0;j<width;j++) {
			if((double)rand() / (double)RAND_MAX < prob) {
				*(ffm + width * i + j) = TREE;
			}
		}
	}

	// Set fire to the trees
	int count = 0;
	for(i=0;i<width;i++) {
		if(*(ffm + width * i) == TREE) {
			*(ffm + width * i) = FIRE;
			count++;
		}
	}

	printff(ffm,width);
	wait(100);

	unsigned register int time = 0;

	while(count) {
		count = tick(ffm,width);
		printff(ffm,width);
		wait(100);
		++time;
	}
	
	printf("%d\n",time);

	return 0;
}
