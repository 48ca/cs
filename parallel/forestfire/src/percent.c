#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#define TREE 2
#define FIRE 1
#define FIRE_STARTED 3
#define MISSING 0

typedef struct Node {
	int i;
	int j;
} Tree;

Tree** forest;
Tree** aforest;
int begindex;
int abegindex;

void wait(unsigned int ms) {
	struct timeval t;
	gettimeofday(&t,NULL);
	double tf = t.tv_sec + (t.tv_usec + ms*1000.0) / 1000000.0 ;
	gettimeofday(&t,NULL);
	while(t.tv_sec + (t.tv_usec) / 1000000.0 < tf) gettimeofday(&t,NULL);
}
void flushforest(int width) {
	register int i;
	int finish = width*width;
	for(i=0;i<finish;i++) {
		// printf("%d %d\n",i, (unsigned int)(forest[i]));
		// if(forest[i] != NULL) free(forest[i]);
		forest[i] = NULL;
	}
	begindex = 0;
}

void flushaforest(int width) {
	register int i;
	int finish = width*width;
	for(i=0;i<finish;i++) {
		aforest[i] = NULL;
	}
	abegindex = 0;
}

void printff(int* ffm,int width) {

	register int i,j;

	for(i=0;i<width;i++) {
		printf("\x1B[F");
	}

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

int tick(int* ffm, int width, int i, int j) {
	// flushaforest(width);

	int count = 0;

	if(*(ffm + i * width + j) == TREE) {
		count++;
		*(ffm + i * width + j) = MISSING;
		if(i > 0) {
			count += tick(ffm, width, i-1, j);
		}
		if(i < width - 1) {
			count += tick(ffm, width, i+1, j);
		}
		if(j > 0) { 
			count += tick(ffm, width, i, j-1);
		}
		if(j < width - 1) {
			count += tick(ffm, width, i, j+1);
		}
	}
	return count;
}

void flushall(int width) {
	flushaforest(width);
	flushforest(width);
}

int regenerate(int* ffm, int width, double prob) {
	register int i,j;
	int count = 0;
	/* for(i=0;i<width*width;i++) {
		*(ffm + i) = MISSING;
	} */
	for(i=0;i<width;i++) {
		for(j=0;j<width;j++) {
			if((double)rand() / (double)RAND_MAX < prob) {
				*(ffm + width * i + j) = TREE;
				count++;
			}
			else {
				*(ffm + width * i + j) = MISSING;
			}
		}
	}

	// Set fire to the trees
	/*
	int count = 0;
	for(i=0;i<width;i++) {
		if(*(ffm + width * i) == TREE) {
			*(ffm + width * i) = FIRE;
			Tree* tmp = (Tree*)malloc(sizeof(Tree));
			tmp->j = 0;
			tmp->i = i;
			forest[begindex++] = tmp;
			count++;
		}
	}
	*/
	return count;
}

int main(int argc, char* argv[]) {

	register int bigl;

	if(argc<4) {
		printf("usage: ff width iterations resolution\n");
		return 1;
	}

	int width = atoi(argv[1]); //1000;
	int iterations = atoi(argv[2]); //500;
	int resolution = atoi(argv[3]); //1000;

	struct timeval t;
	gettimeofday(&t,NULL);
	srand(t.tv_sec + t.tv_usec);

	// printf("%7.6f %f\n",0.0,0.0); // 0

	Tree** cf = malloc(sizeof(Tree*) * width * width);
	Tree** cfa = malloc(sizeof(Tree*) * width * width);

	forest = cf;
	aforest = cfa;

	double lowerLimit = 0.0;
	double upperLimit = 1.0;

	int* ffm;
	ffm = malloc(sizeof(int) * width * width);

	for(bigl=1;bigl<=resolution;bigl++) {

		double prob;
		double total = 0;
		
		double burned = 0;


		prob = (double)bigl / resolution;

		if(prob < lowerLimit || prob > upperLimit) continue;

		register int loop;
		for(loop=0;loop<iterations;loop++) {

			int count = regenerate(ffm,width,prob);
			
			register int i;

			total += count;

			for(i=0;i<width;i++) {
				int t = tick(ffm,width,0,i);
				total -= t;
				burned += t;
				// fprintf(stderr,"%d : %d\n",count,t);
			}

		}
		printf("%7.6f %f %f\n",prob,(double)(100 * (1-((total)/(double)(iterations*width*width)))),(double)(burned * 100)/(double)(iterations*width*width));
	}
	
	// printf("%7.6f %f\n",1.0,1.0);

	free(cfa);
	free(cf);
	free(ffm);


	return 0;
}
