#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <mpi.h>

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

void burn(int* ptr, int i, int j) {
	if(*ptr == TREE) {
		Tree* tmp = (Tree*)malloc(sizeof(Tree));
		tmp->i = i;
		tmp->j = j;
		aforest[abegindex++] = tmp;
	}
}

int tick(int* ffm, int width) {
	abegindex = 0;

	register int i,j,k,count;
	for(k=0;k<begindex;k++) {
		i = forest[k]->i;
		j = forest[k]->j;
		if(*(ffm + i * width + j) == FIRE) {
			*(ffm + i * width + j) = MISSING;
			if(i > 0) {
				int* ptr = ffm + (i-1) * width + j;
				burn(ptr, i-1, j);
			}
			if(i < width - 1) {
				int* ptr = ffm + (i+1) * width + j;
				burn(ptr, i+1, j);
			}
			if(j > 0) { 
				int* ptr = ffm + i * width + j - 1;
				burn(ptr, i, j-1);
			}
			if(j < width - 1) {
				int* ptr = ffm + i * width + j + 1;
				burn(ptr, i, j+1);
			}
		}
		free(forest[k]);
	}
	
	begindex = 0;

	count = 0;
	for(k=0;k<abegindex;k++) {
		i = aforest[k]->i;
		j = aforest[k]->j;
		*(ffm + width * i + j) = FIRE;
		forest[begindex++] = aforest[k];
		count++;
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
	for(i=0;i<width;i++) {
		for(j=0;j<width;j++) {
			if((double)rand() / (double)RAND_MAX < prob) {
				*(ffm + width * i + j) = j==0 ? FIRE : TREE;
				if(j==0) {
					Tree* tmp = (Tree*)malloc(sizeof(Tree));
					tmp->j = 0;
					tmp->i = i;
					forest[begindex++] = tmp;
					count++;
				}
			}
			else {
				*(ffm + width * i + j) = MISSING;
			}
		}
	}
}

int main(int argc, char* argv[]) {

	int ierr, pid, num_procs;

	MPI_Status status;
	int tag = 0;
	int kill_tag = 1;

	MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &pid);
	MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

	char pname[MPI_MAX_PROCESSOR_NAME];
	int name_len;
	MPI_Get_processor_name(pname, &name_len);

	register int bigl;

	/*
	if(argc<4) {
		printf("usage: ff width iterations resolution\n");
		return 1;
	}
	*/

	int width = 100; // atoi(argv[1]); //1000;
	int iterations = 160; // atoi(argv[2]); //500;
	int resolution = 100000; // atoi(argv[3]); //1000;

	double increment = 1.0/resolution;

	register int sent = 0;
	register int count = 0;

	double prob;

	if(pid == 0) {
		fprintf(stderr,"Manager at %s\nIncrementing by %f\n",pname,increment);
		struct timeval tv0;
		gettimeofday(&tv0,NULL);
		int i;
		double prob = .594;
		for(i=1;i<num_procs;i++) {
			MPI_Send( &prob, 1, MPI_DOUBLE, i, tag, MPI_COMM_WORLD );
			sent++;
			prob += increment;
		}
		FILE* out;
		char* filename = "res/test";
		// sprintf(filename, "res/out%d%d%d.txt",width,iterations,resolution);
		double ans;
		double arr[2];
		double total = (.597 - .594) * resolution;
		while(prob < .597) {
			MPI_Recv( &arr, 2, MPI_DOUBLE, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status );
			count++;

			int node = status.MPI_SOURCE;
			prob += increment;
			MPI_Send( &prob, 1, MPI_DOUBLE, node, tag, MPI_COMM_WORLD );
			sent++;

			// printf("Done: %f%c        \r",100 * count/total,'%');
			// fflush(stdout);
			out = fopen(filename,"a");
			fprintf(out,"%7.6f %f\n",arr[0],arr[1]);
			printf("%7.6f %f\n",arr[0],arr[1]);
			fclose(out);
		}
		while(count<sent) {
			MPI_Recv( &arr, 2, MPI_DOUBLE, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status );
			int node = status.MPI_SOURCE;
			MPI_Send( &prob, 1, MPI_DOUBLE, node, kill_tag, MPI_COMM_WORLD );
			out = fopen(filename,"a");
			fprintf(out,"%7.6f %f\n",arr[0],arr[1]);
			printf("%7.6f %f\n",arr[0],arr[1]);
			fclose(out);
			// printf("Done: %f%c        \r",100 * count/total,'%');
			// fflush(stdout);
			count++;
		}
		struct timeval tv1;
		gettimeofday(&tv1,NULL);
		long long elapsed = (tv1.tv_sec-tv0.tv_sec)*1000000LL + tv1.tv_usec-tv0.tv_usec;
		// printf("                              \r");
		printf("\x1B[31mTime: %fs\x1B[0m\n",(double)elapsed/1000000);
	} else {
		struct timeval tv;
		gettimeofday(NULL, tv);
		srand(pid + tv.tv_usec);
		while(1) {

			Tree** cf = malloc(sizeof(Tree*) * width * width);
			Tree** cfa = malloc(sizeof(Tree*) * width * width);

			forest = cf;
			aforest = cfa;

			int* ffm;
			ffm = malloc(sizeof(int) * width * width);

			unsigned register int total = 0;

			MPI_Recv( &prob, 1, MPI_DOUBLE, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &status );
			
			if(status.MPI_TAG == kill_tag) break;

			register int loop;
			for(loop=0;loop<iterations;loop++) {

				flushall(width);

				register int count = regenerate(ffm,width,prob);
				unsigned register int time = 0;

				while(count) {
					count = tick(ffm,width);
					time++;
				}
				total += time; // / (double)width;
			}

			double ans;
			ans = (double)(total)/(double)(loop*width);

			double arr[] = {prob,ans};
			MPI_Send( &arr, 2, MPI_DOUBLE, 0, tag, MPI_COMM_WORLD );

			free(cfa);
			free(cf);
			free(ffm);
		}
	}
	MPI_Finalize();
	return 0;
}
