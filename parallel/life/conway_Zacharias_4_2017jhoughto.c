#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <GL/glut.h>
#include <mpi.h>

static int* oldboard;
static int* newboard;
static int* tmpboard; // not to be allocated
int changes;
int steps = 0;

#define X 2000
#define Y 2000

unsigned int win_width = 800;
unsigned int win_height = 600;
double aspect = 800/600.0;

int offsetx = 200;
int offsety = 200;

int resized = 0;

// MPI
int rank;
MPI_Status status;
int num_procs;


#define START -1
#define OK 0
#define KILL 1
#define REQUEST 2
#define OPTIONS 3
#define RESPONSE 4
const int kill_tag = KILL;
const int request_tag = REQUEST;
const int options_tag = OPTIONS;
const int response_tag = RESPONSE;
const int start_code = START;

void wait(unsigned int ms) {
	struct timeval t;
	gettimeofday(&t,NULL);
	volatile double tf = t.tv_sec + (t.tv_usec + ms*1000.0) / 1000000.0 ;
	gettimeofday(&t,NULL);
	while(t.tv_sec + (t.tv_usec) / 1000000.0 < tf) gettimeofday(&t,NULL);
}

int neighbors(int* board, int y, int x, int pos) {
	int ret = 0;
	
	int sq = win_width*win_height;
	pos += sq;
	int pd = pos/win_width;
	int right = ((pos+1)%win_width + win_width*(pd) + sq)%(sq);
	int left  = ((pos-1)%win_width + win_width*(pd) + sq)%(sq);
	int up    = (pos%win_width + win_width*(pd-1) + sq)%(sq);
	int down  = (pos%win_width + win_width*(pd+1) + sq)%(sq);
	int lu    = ((pos-1)%win_width + win_width*(pd-1) + sq)%(sq);
	int ld    = ((pos-1)%win_width + win_width*(pd+1) + sq)%(sq);
	int ru    = ((pos+1)%win_width + win_width*(pd-1) + sq)%(sq);
	int rd    = ((pos+1)%win_width + win_width*(pd+1) + sq)%(sq);
	ret = board[right] + board[left] + board[up] + board[down] + board[lu] + board[ru] + board[ld] + board[rd];
	return ret;
}

int tick(int* board, int* save) {
	// memcpy(save,board,sizeof(int) * X * Y);
	register int i;
	register int j;
	int diff = 0;

	/* Experimental parallel code
	int node;
	int ok;
	for(node=1;node<num_procs;node++)
		MPI_Send(board,win_width * win_height,MPI_INT,node,START,MPI_COMM_WORLD);
	for(node=1;node<num_procs;node++)
		MPI_Recv(&ok,1,MPI_INT,node,OK,MPI_COMM_WORLD,&status);

	printf("All workers sent OK\n");
	*/

	/* Serial code */
	int pos;
	for(i=0;i<win_height;i++) {
		for(j=0;j<win_width;j++) {
			pos = i*win_width + j;
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

	/* End of serial code */
	
	/*
	for(i=0;i<win_height;i++) {
		for(j=0;j<win_width;j++) {
			MPI_Recv(board+i*win_width+j,1,MPI_INT,1,response_tag,MPI_COMM_WORLD,&status);
		}
	}
	*/

	return 0;
}

void worker_tick(int* board, int* save) {
	register int i;
	register int j;
	int pos;
	for(i=0;i<win_height;i++) {
		for(j=0;j<win_width;j++) {
			pos = i*win_width + j;
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
		}
	}
}

void print(int* board) {
	register int i;
	register int j;
	for(i=0;i<70;i++) {
		for(j=0;j<100;j++) {
			printf("%c",board[i*win_width+j]?'#':' ');
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

void init_with_mover(int* board) {
	board[1] = 1;
	board[win_width*1+2] = 1;
	board[win_width*2] = 1;
	board[win_width*2+1] = 1;
	board[win_width*2+2] = 1;
}

void init(int* board) {
	srand(time(NULL));
	register int i;
	register int j;
	for(i=0;i<win_height;i++) {
		for(j=0;j<win_width;j++) {
			board[i*win_width+j] = ((double)rand() / (double)RAND_MAX) < 0.6 ? 1 : 0;
		}
	}
	// init_with_mover(board);
}

void keyfunc(unsigned char key, int xscr, int yscr) {
	switch(key) {
		case 'r':
			init(oldboard);
			steps = 0;
			break;
		case 'q':
			exit(0);
			break;
	}
}

void reshapefunc(int wscr, int hscr) {
	win_width = wscr;
	win_height = hscr;
	aspect = (double)(win_height) / win_width;
	glViewport(0,0,(GLsizei)win_width,(GLsizei)win_height);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluOrtho2D(0.0,1.0*win_width,0.0,1.0*win_height);
	glMatrixMode(GL_MODELVIEW);
	resized = 1;
	steps = 0;
	glutPostRedisplay();
}

void displayfunc() {
	if(resized) {
		resized = 0;
		init(oldboard);
		printf("Resizing\n");
	}
	register int i;
	register int j;
	double color;
	glBegin(GL_POINTS);
	for(i=0;i<win_height;i++) {
		for(j=0;j<win_width;j++) {
			double red = newboard[i*win_width + j];
			double green = newboard[i*win_width + j];
			double blue = newboard[i*win_width + j];
			glColor3f(red,green,blue);
			glVertex2f(j,i);
		}
	}
	glEnd();
	glutSwapBuffers();
}

void mousefunc(int button, int state, int xscr, int yscr) {

}

void dragfunc(int x, int y) {

}

void idlefunc() {
	if(changes) {
		changes = tick(newboard, oldboard);
		// tick(newboard,oldboard);
		glutPostRedisplay();
		tmpboard = oldboard;
		// print(newboard);
		oldboard = newboard;
		newboard = tmpboard;
	}
	printf("Tick %d (changes: %d)\n",steps++,changes);
}

void exitfunc() {
	free(oldboard);
	free(newboard);
}

void worker() {
	int tag;
	int recv;
	int options[2];
	int send[2];
	while(1) {
		MPI_Probe(MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
		tag = status.MPI_TAG;
		switch(tag) {
			case(KILL):
				MPI_Finalize();
				return;
			case(OPTIONS):
				MPI_Recv(options, 2, MPI_INT, status.MPI_SOURCE, options_tag, MPI_COMM_WORLD, &status);
				win_width = options[0];
				win_height = options[1];
				break;
			case(REQUEST):
				MPI_Recv(&recv, 1, MPI_INT, status.MPI_SOURCE,request_tag, MPI_COMM_WORLD, &status);
				send[0] = newboard[recv];
				send[1] = recv;
				MPI_Send(send, 2, MPI_INT, status.MPI_SOURCE, response_tag, MPI_COMM_WORLD);
			case(START):
				MPI_Recv(oldboard, win_height * win_width, MPI_INT, 0, START, MPI_COMM_WORLD, &status);
				worker_tick(newboard,oldboard);
				int ok = OK;
				MPI_Send(&ok, 1, MPI_INT, 0, OK, MPI_COMM_WORLD);
		}
	}
}

int main(int argc, char* argv[]) {

	MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &num_procs);


	oldboard = (int*)malloc(sizeof(int) * X * Y);
	newboard = (int*)malloc(sizeof(int) * X * Y);
	init(oldboard);
	changes = 1;
	atexit(exitfunc);
	if(rank == 0) {
		glutInit(&argc, argv);
		glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
		glutInitWindowSize(win_width,win_height);
		glutInitWindowPosition(offsetx,offsety);
		glutCreateWindow("Conway's Game of Life");
		glClearColor(0.0,0.0,0.0,0.0);
		glShadeModel(GL_SMOOTH);
		glutReshapeFunc(reshapefunc);
		glutIdleFunc(idlefunc);
		glutDisplayFunc(displayfunc);
		glutMouseFunc(mousefunc);
		glutMotionFunc(dragfunc);
		glutKeyboardFunc(keyfunc);
		glutMainLoop();
	} else {
		worker();
	}
	return 0;
}
