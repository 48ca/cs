#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#define TREE 2
#define FIRE 1
#define FIRE_STARTED 3
#define MISSING 0

typedef struct Node {

	int x;
	int y;

} ListNode;

ListNode** list_fire;
ListNode** list_afire;
int currIndex,currAIndex;

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
		ListNode* tmp = (ListNode*)malloc(sizeof(ListNode));
		list_afire[currAIndex++] = tmp;
	}
}

int tick(int* ffm, int width) {
	register int i,j,count;
	for(count=0;list_fire[count]!= NULL;count++) {
		i = list_fire[count]->x;
		j = list_fire[count]->y;
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

	for(count=0;count<width*width;count++) {
		list_fire[count] = NULL;
	}
	for(count=0;list_afire[count]!=NULL;count++) {
		i = list_afire[count]->x;
		j = list_afire[count]->y;
		*(ffm + width * i + j) = FIRE;
		list_fire[count] = list_afire[count];
		count++;
	}
	return count;
}

int main(int argc, char* argv[]) {

	register int bigl;

	for(bigl=0;bigl<=100;bigl++) {

		double prob;
		int width = 50;
		int total = 0;
		
		prob = bigl / 100.0;

		register int loop;
		for(loop=0;loop<100;loop++) {

			int* ffm;

			struct timeval t;
			gettimeofday(&t,NULL);

			srand(t.tv_sec + t.tv_usec + loop);

			/*
			if(argc > 1) {
				prob = atof(argv[1]);
			} else {
				// printf("Supply a number from 0 to 1.\n");
				return 1;
			}
			*/

			ffm = malloc(sizeof(int) * width * width);
			list_fire = malloc(sizeof(ListNode*) * width * width);
			list_afire = malloc(sizeof(ListNode*) * width * width);

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
					ListNode* node = (ListNode*)malloc(sizeof(ListNode));
					node->x = 0;
					node->y = i;
					list_fire[count++] = node;
				}
			}

			currIndex = count;

			//printff(ffm,width);
			//wait(100);

			unsigned register int time = 0;

			while(count) {
				count = tick(ffm,width);
				printff(ffm,width);
				wait(100);
				++time;
			}
			total += time;
		}
		printf("%3.2f %f\n",prob,(float)(total)/(float)(loop));
	}
	return 0;
}
