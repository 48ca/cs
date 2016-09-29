#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <mpi.h>

static int* oldboard;
static int* newboard;
int changes;
int steps = 0;

#define X 170
#define Y 70

int ierr, rank, num_procs;

MPI_Status status;
const int tag = 0;
const int kill_tag = 1;



void wait(unsigned int ms) {
	struct timeval t;
	gettimeofday(&t,NULL);
	double tf = t.tv_sec + (t.tv_usec + ms*1000.0) / 1000000.0 ;
	gettimeofday(&t,NULL);
	while(t.tv_sec + (t.tv_usec) / 1000000.0 < tf) gettimeofday(&t,NULL);
}

int neighbors(int* board, int y, int x, int pos) {
	int ret = 0;

	/*
	int yg = y>0;
	int yl = y<Y-1;
	int xg = x>0;
	int xl = x<X-1;

	if(xl) {
		ret+=board[pos+1];
		if(yg) {
			ret+=board[pos+1-X];
		} if (yl) {
			ret+=board[pos+1+X];
		}
	} if(xg) {
		ret+=board[pos-1];
		if(yg) {
			ret+=board[pos-1-X];
		} if (yl) {
			ret+=board[pos-1+X];
		}
	} if (yg) {
		ret+=board[pos-X];
	} if (yl) {
		ret+=board[pos+X];
	}
	*/
	int sq = X*Y;
	pos += sq;
	int right = ((pos+1)%X + X*(pos/X) + sq)%(sq);
	int left  = ((pos-1)%X + X*(pos/X) + sq)%(sq);
	int up    = (pos%X + X*(pos/X-1) + sq)%(sq);
	int down  = (pos%X + X*(pos/X+1) + sq)%(sq);
	int lu    = ((pos-1)%X + X*(pos/X-1) + sq)%(sq);
	int ld    = ((pos-1)%X + X*(pos/X+1) + sq)%(sq);
	int ru    = ((pos+1)%X + X*(pos/X-1) + sq)%(sq);
	int rd    = ((pos+1)%X + X*(pos/X+1) + sq)%(sq);
	ret = board[right] + board[left] + board[up] + board[down] + board[lu] + board[ru] + board[ld] + board[rd];
	return ret;
}

int step(int* board, int* save) {
	// memcpy(save,board,sizeof(int) * X * Y);
	register int i;
	register int j;
	int pos;
	int diff = 0;
	for(i=0;i<Y;i++) {
		for(j=0;j<X;j++) {
			int pos = i*X + j;
			if(save[pos]) {
				switch(neighbors(save,i,j,pos)) {
					case(2):
					case(3):
						board[pos] = 1;
						break;
					default:
						board[pos] = 0;
						break;
				}
			} else {
				switch(neighbors(save,i,j,pos)) {
					case(3):
						board[pos] = 1;
						break;
					default:
						board[pos] = 0;
						break;
				}
			}
			diff += board[pos] != save[pos];
		}
	}
	return diff;
}

void print(int* board) {
	register int i;
	register int j;
	for(i=0;i<Y;i++) {
		for(j=0;j<X;j++) {
			printf("%c",board[i*X+j]?'#':' ');
		}
		printf("\n");
	}
	printf("Step %d\n",++steps);
}
void clearprint() {
	register int i;
	for(i=0;i<Y+1;i++) { // Y+1 due to step printout in void print()
		printf("\x1B[F");
	}
}

void init(int* board) {
	srand(time(NULL));
	register int i;
	register int j;
	for(i=0;i<Y;i++) {
		for(j=0;j<X;j++) {
			board[i*X+j] = ((double)rand() / (double)RAND_MAX) < 0.65 ? 1 : 0;
		}
	}
}

void init_with_mover(int* board) {
	board[1] = 1;
	board[X*1+2] = 1;
	board[X*2] = 1;
	board[X*2+1] = 1;
	board[X*2+2] = 1;
}

int main(int argc, char* argv[]) {

	MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

	char pname[MPI_MAX_PROCESSOR_NAME];
	int name_len;
	MPI_Get_processor_name(pname, &name_len);


	int* tmpboard;
	oldboard = (int*)malloc(sizeof(int) * X * Y);
	newboard = (int*)malloc(sizeof(int) * X * Y);

	init(oldboard);
	changes = 1;
	print(oldboard);
	clearprint();
	while(changes) {
		changes = step(newboard, oldboard);
		print(newboard);
		wait(6);
		clearprint();
		tmpboard = oldboard;
		oldboard = newboard;
		newboard = tmpboard;
	}

	free(oldboard);
	free(newboard);

	return 0;
}
