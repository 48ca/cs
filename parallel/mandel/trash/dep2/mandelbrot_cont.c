#include <stdlib.h>
#include <GL/glut.h>
#include <math.h>
#include <mpi.h>
#include "png.c"

#define LOOPS 50
#define SQ_ESC_RADIUS 4
#define ESCAPE 2

#define MAX_SIZE 2000
// #define MAX_SIZE 10000
// MAX_SIZE 10000 REQUIRES 4GB RAM SPACE

// MPI
const int tag = 0;
const int kill_tag = 1;
int num_procs;
MPI_Status status;

/* Switched to dynamic allocation for larger RAM potential
static double colors[MAX_SIZE][MAX_SIZE];
static double display_colors[MAX_SIZE][MAX_SIZE][3];
*/
double** colors;
double*** display_colors;
double min_color;
double max_color;

double loop_scalar = .6;
long double gxc = 0.0L; // global x center
long double gyc = 0.0L; // global y center

static int win_width = 1200;
static int win_height = 900;
/*
static int win_width = MAX_SIZE;
static int win_height = MAX_SIZE;
*/

static double aspect = .75; // inverted -- 3:4 by default

long double last_gen_xcenter;
long double last_gen_ycenter;
long double last_gen_xwidth;

int xinit; // for use with drag function
int yinit;


#define PALETTE_SCALE 3
double palette[][3] = {

		// Ultra Fractal (Linear)
		#define PALETTE_SIZE 5
		{0.0,7.0/255,100.0/255},
		{32.0/255,107.0/255,203.0/255},
		{237.0/255,1.0,1.0},
		{1.0,170.0/255,0.0},
		{0.0,2.0/255,0.0}

		// Custom
		/*
		#define PALETTE_SIZE 5
		{0.0,7.0/255,60.0/255},
		{1.0,105.0/255,0.0},
		{1.0,150.0/255,0.2},
		{32.0/255,107.0/255,203.0/255},
		{10.0/255,200.0/255,30.0/255}
		*/
		
		// RGB
		/*
		#define PALETTE_SIZE 3
		{1.0,0.0,0.0},
		{0.0,1.0,0.0},
		{0.0,0.0,1.0}
		*/
};

int resized = 0;
int fullscreen = 0;


// Function prototypes
void generate(long double xcenter, long double ycenter, long double xwidth);
void load_loc(const char* filename);
void save_loc(const char* filename);
void keyfunc(unsigned char key,int xscr,int yscr);
void displayfunc();
void reshapefunc(int wscr,int hscr);
void displayfrac();
void mousefunc(int button,int state,int xscr,int yscr);
void dragfunc(int x, int y);
void manager(int argc, char* argv[]);
void worker();
void add_color(int x, int y, double color);

void generate(long double xcenter, long double ycenter, long double xwidth) {
	printf("Regenerating...\n");
	int x;
	int y;
	long double ywidth = aspect * xwidth;
	long double xscalar = win_width / xwidth;
	long double yscalar = win_height / ywidth;
	long double hwidth = win_width/2.0L;
	long double hheight = win_height/2.0L;
	long double loop_factor;
	if(xwidth >= 4) loop_factor = 1.0L;
	else loop_factor = loop_scalar * sqrt(2 * log(4/xwidth));
	if(loop_factor < 1) loop_factor = 1.0L;
	long double max_loop = LOOPS*loop_factor;


	if(xwidth <      .000000000000001L) {
		printf("\x1B[31mWARNING:\x1B[0m Approaching long double precision barrier!\n");
	}
	/*
	else if(xwidth < .0000000000005) {
		printf("\x1B[31mWARNING:\x1B[0m Approaching double precision barrier!\n");
	}
	*/
	last_gen_xcenter = xcenter;
	last_gen_ycenter = ycenter;
	last_gen_xwidth = xwidth;

	int node = 1;
	int recv = 0;
	int sent = 0;
	long double send[5];
	double res[3];
	send[2] = max_loop;
	max_color = 0.0;
	min_color = 1.0;

	glBegin(GL_POINTS);

	for(y=0;y<win_height;y++) {
		for(x=0;x<win_width;x++) {
			send[0] = xcenter + (x - hwidth) / xscalar;
			send[1] = ycenter + (y - hheight) / yscalar;
			send[3] = (long double)x;
			send[4] = (long double)y;
			MPI_Send( &send, 5, MPI_LONG_DOUBLE, node++, tag, MPI_COMM_WORLD );
			sent++;
			if(node == num_procs) break;
		}
		if(node == num_procs) break;
	}
	for(;y<win_height;y++) {
		for(;x<win_width;x++) {
			send[0] = xcenter + (x - hwidth) / xscalar;
			send[1] = ycenter + (y - hheight) / yscalar;
			send[3] = (long double)x;
			send[4] = (long double)y;

			MPI_Recv( &res, 3, MPI_DOUBLE, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status );
			recv++;
			node = status.MPI_SOURCE;
			MPI_Send( &send, 5, MPI_LONG_DOUBLE, node, tag, MPI_COMM_WORLD );
			sent++;

			int color_x = (int)res[0];
			int color_y = (int)res[1];
			colors[color_x][color_y] = res[2];
			add_color(color_x, color_y, res[2]);
		}
		x=0;
	}
	while(recv<sent) {
		MPI_Recv( &res, 3, MPI_DOUBLE, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status );
		recv++;
		int color_x = (int)res[0];
		int color_y = (int)res[1];
		colors[color_x][color_y] = res[2];
		add_color(color_x, color_y, res[2]);
	}

	glEnd();

	printf("Generated\n");
}

void add_color(int x, int y, double color) {
	
	double red = 0.0;
	double blue = 0.0;
	double green = 0.0;

	if(color != 0.0) {
		color *= PALETTE_SIZE * PALETTE_SCALE;
		/* SMOOTHING PASS 2 */
		double* left_el = palette[(int)(color)%PALETTE_SIZE];
		double* right_el = palette[((int)(color)+1)%PALETTE_SIZE];

		double left;
		double right;
		right = color - (int)color;
		left = 1 - right;

		red = left_el[0] * left + right_el[0] * right;
		green = left_el[1] * left + right_el[1] * right;
		blue = left_el[2] * left + right_el[2] * right;
	}

	display_colors[x][y][0] = red;
	display_colors[x][y][1] = green;
	display_colors[x][y][2] = blue;

	glColor3f(red,green,blue);
	glVertex2f(x,y);

	// if(y%20 == (win_height - 1)%20) glFlush();
}

void reset() {
	generate(0,0,4);
	gxc = 0.0;
	gyc = 0.0;
	loop_scalar = .6;
	glutPostRedisplay();
}

void save_png() {
	bitmap_t fractal;
	int x;
	int y;
	fractal.height = win_height;
	fractal.width = win_width;
	
	fractal.pixels = calloc(sizeof(pixel_t),fractal.width*fractal.height);

	for(y=0;y<fractal.height;y++) {
		for(x=0;x<fractal.width;x++) {
			pixel_t *pixel = pixel_at(&fractal,x,fractal.height-y-1);
			pixel-> red = (int)(255 * display_colors[x][y][0]);
			pixel-> green = (int)(255 * display_colors[x][y][1]);
			pixel-> blue = (int)(255 * display_colors[x][y][2]);
		}
	}
	// defined in png.c
	save_png_to_file(&fractal,"frac.png");
	return;
}

void load_loc(const char* filename) {
	FILE* f = fopen(filename,"r");
	if(f==NULL) {
		printf("Error loading location!\n");
		return;
	}
	char* line = NULL;
	size_t len = 0;
	ssize_t read;

	long double xwidth;

	read = getline(&line, &len, f);
	gxc = strtold(line,&(line)+(read));
	read = getline(&line, &len, f);
	gyc = strtold(line,&(line)+(read));
	read = getline(&line, &len, f);
	xwidth = strtold(line,&(line)+(read));
	fclose(f);
	generate(gxc,gyc,xwidth);
	glutPostRedisplay();
}

void save_loc(const char* filename) {
	FILE* f = fopen(filename,"w");
	if(f==NULL) {
		printf("Error saving location!\n");
		return;
	}
	fprintf(f,"%.40LfL\n",last_gen_xcenter);
	fprintf(f,"%.40LfL\n",last_gen_ycenter);
	fprintf(f,"%.40LfL\n",last_gen_xwidth);
	fclose(f);
}

void keyfunc(unsigned char key,int xscr,int yscr) {

	register int i;

	// CONTROLS
	switch(key) {
		case 'q':
			printf("Exiting\n");
			int node;
			double send[3] = {0};
			for(node=1;node<num_procs;node++) {
				MPI_Send( &send, 3, MPI_DOUBLE, node, kill_tag, MPI_COMM_WORLD );
			}
			MPI_Finalize();
			exit(0);
			break;
		case 'r':
			printf("Reseting...\n");
			reset();
			printf("Reset\n");
			break;
		case 'p':
			printf("Saving PNG...\n");
			save_png();
			printf("Saved PNG\n");
			break;
		case 'l':
			printf("Loading config...\n");
			load_loc("save.txt");
			printf("Loaded config\n");
			break;
		case 'd': //debug
			printf("Last generation properties:\n");
			printf("\tx center: %Le\n",last_gen_xcenter);
			printf("\ty center: %Le\n",last_gen_ycenter);
			printf("\tx width:  %Le\n",last_gen_xwidth);
			printf("\tmagnification level: 10^%f\n",log(4/last_gen_xwidth)/log(10));
			break;
		case 's':
			printf("Saving config...\n");
			save_loc("save.txt");
			printf("Saved config\n");
			break;
		case 'z':
			printf("Reverting...\n");
			load_loc(".fallback.txt");
			printf("Reverted\n");
			break;
		case 'i':
			printf("Zooming in...\n");
			generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth/2);
			glutPostRedisplay();
			printf("Zoom finished\n");
			break;
		case 'o':
			printf("Zooming out...\n");
			generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth*2);
			glutPostRedisplay();
			printf("Zoom finished\n");
			break;
		case 'f':
			printf("Toggling fullscreen...\n");
			if(fullscreen) {
				glutPositionWindow(120,LOOPS);
				glutReshapeWindow(1200,900);
				fullscreen = 0;
			} else {
				glutFullScreen();
				fullscreen = 1;
			}
			printf("Toggled fullscreen\n");
			break;
		case 'm':
			printf("Increasing loops...\n");
			loop_scalar *= 2;
			generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth);
			glutPostRedisplay();
			printf("Increased loops\n");
			break;
		case 'n':
			printf("Decreasing loops...\n");
			loop_scalar /= 2;
			generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth);
			glutPostRedisplay();
			printf("Decreased loops\n");
			break;
		case 'b':
			for(i=0;i<100;i++) {
				generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth*.95);
				displayfunc();
			}
			break;
	}
}

void displayfunc() {
	if(resized) {
		generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth);
		resized = 0;
	}
	printf("Displaying...\n");
	glFlush();
	// glClear(GL_COLOR_BUFFER_BIT); // | GL_DEPTH_BUFFER_BIT);
	int x;
	int y;
	double color;
	for(y=0;y<win_height;y++) {
		for(x=0;x<win_width;x++) {
			color = colors[x][y];

			// COLOR RENDERER
			
			if(color == 0.0) {
				glColor3f(0.0,0.0,0.0); // black
				display_colors[x][y][0] = 0.0;
				display_colors[x][y][1] = 0.0;
				display_colors[x][y][2] = 0.0;
			} else {
				// NORMALIZATION
				/*
				color -= (min_color);
				color /= (max_color-min_color);
				*/

				color *= PALETTE_SIZE * PALETTE_SCALE;

				double red;
				double blue;
				double green;

				/* SMOOTHING PASS 2 */
				double* left_el = palette[(int)(color)%PALETTE_SIZE];
				double* right_el = palette[((int)(color)+1)%PALETTE_SIZE];

				double left;
				double right;
				right = color - (int)color;
				left = 1 - right;

				red = left_el[0] * left + right_el[0] * right;
				green = left_el[1] * left + right_el[1] * right;
				blue = left_el[2] * left + right_el[2] * right;

				/*
				red = left_el[0];
				green = left_el[1];
				blue = left_el[2];
				*/

				display_colors[x][y][0] = red;
				display_colors[x][y][1] = green;
				display_colors[x][y][2] = blue;
				glColor3f(red,green,blue);
			}
			glBegin(GL_POINTS);
			glVertex3f(x,y,0.0);
			glEnd();
		}
	}
	glutSwapBuffers();
	printf("Displayed\n");
}

void reshapefunc(int wscr,int hscr)
{
	win_width = wscr;
	win_height = hscr;
	aspect = (double)(win_height) / win_width;
	glViewport(0,0,(GLsizei)win_width,(GLsizei)win_height);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluOrtho2D(0.0,1.0*win_width,0.0,1.0*win_height);
	glMatrixMode(GL_MODELVIEW);
	resized = 1;
	glutPostRedisplay();
}

void displayfrac() {
	int x;
	int y;
	glClear(GL_COLOR_BUFFER_BIT); // | GL_DEPTH_BUFFER_BIT);
	glBegin(GL_POINTS);
	for(y=0;y<win_height;y++) {
		for(x=0;x<win_width;x++) {
			glColor3f(display_colors[x][y][0],display_colors[x][y][1],display_colors[x][y][2]);
			glVertex2f(x,y);
		}
	}
	glEnd();
	glutSwapBuffers();
}

void mousefunc(int button,int state,int xscr,int yscr)
{
	if(button==GLUT_LEFT_BUTTON) {
		if(state==GLUT_DOWN) {
			/*
			gxc += gfx * (xscr - win_width/2) / win_width;
			gyc += gfy * (win_height/2 - yscr) / win_height;
			*/
			xinit = xscr;
			yinit = win_height - yscr;
		}
		else if(state==GLUT_UP) {
			if(xscr==xinit || yscr==yinit)
				return;
			save_loc(".fallback.txt");
			double x = xscr;
			double y = win_height - yscr;
			printf("Drawing...\n");
			glLineWidth(1.5);
			glColor3f(1.0,1.0,1.0);
			glBegin(GL_LINES);
			glVertex3f(x,y,1.0);
			glVertex3f(xinit,y,1.0);
			glEnd();
			glBegin(GL_LINES);
			glVertex3f(x,y,1.0);
			glVertex3f(x,yinit,1.0);
			glEnd();
			glBegin(GL_LINES);
			glVertex3f(xinit,yinit,1.0);
			glVertex3f(x,yinit,1.0);
			glEnd();
			glBegin(GL_LINES);
			glVertex3f(xinit,yinit,1.0);
			glVertex3f(xinit,y,1.0);
			glEnd();
			glFlush();
			glutSwapBuffers();

			long double xwidth = last_gen_xwidth*(abs(x-xinit)/(long double)(win_width));
			gxc = last_gen_xcenter + last_gen_xwidth*((x+xinit)/(2*win_width) - .5);
			gyc = last_gen_ycenter + last_gen_xwidth*aspect*((y+yinit)/(2*win_height) - .5);
			generate(gxc,gyc,xwidth);
			glutPostRedisplay();
		}
	}
}

void dragfunc(int x, int y) {
	displayfrac();
	y = win_height - y;
	glLineWidth(1.5);
	glColor3f(1.0,1.0,1.0);
	glBegin(GL_LINES);
	glVertex2f(x,y);
	glVertex2f(xinit,y);
	glVertex2f(x,y);
	glVertex2f(x,yinit);
	glVertex2f(xinit,yinit);
	glVertex2f(x,yinit);
	glVertex2f(xinit,yinit);
	glVertex2f(xinit,y);
	glEnd();
	glutSwapBuffers();
}

void manager(int argc, char* argv[]) {
	printf("Allocating...\n");
	// Allocated memory here is freed upon termination
	colors = (double**)(malloc(sizeof(double**) * MAX_SIZE * MAX_SIZE));
	display_colors = (double***)(malloc(sizeof(double***) * MAX_SIZE * MAX_SIZE * 3));
	register int i,j;
	for(i=0;i<MAX_SIZE;i++) {
		colors[i] = malloc(sizeof(double) * MAX_SIZE);
		display_colors[i] = malloc(sizeof(double*) * MAX_SIZE * 3);
		for(j=0;j<MAX_SIZE;j++) {
			display_colors[i][j] = malloc(sizeof(double) * 3);
		}
	}
	printf("Allocated\n");

	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB);
	glutInitWindowSize(win_width,win_height);
	glutInitWindowPosition(100,LOOPS);
	glutCreateWindow("");
	glClearColor(1.0,1.0,1.0,0.0);
	glShadeModel(GL_SMOOTH);
	// glEnable(GL_DEPTH_TEST);

	last_gen_xcenter = 0.0L;
	last_gen_ycenter = 0.0L;
	last_gen_xwidth = 4.0L;

	glutReshapeFunc(reshapefunc);
	glutDisplayFunc(displayfunc);
	glutMouseFunc(mousefunc);
	glutMotionFunc(dragfunc);
	glutKeyboardFunc(keyfunc);
	glutMainLoop();
	return;
}

void worker() {
	long double send[5];
	double res[3];
	while(1) {
		MPI_Recv( &send, 5, MPI_LONG_DOUBLE, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &status );
		if(status.MPI_TAG == kill_tag) { break; } 
		else {
			long double cx = send[0];
			long double cy = send[1];

			long double a = cx;
			long double b = cy;
			long double old_a;
			// long double old_b;
			
			long double max_loop = send[2];
			int int_max_loop = (int)max_loop;
			int loop = int_max_loop;
			while(--loop) {
				old_a = a;
				a = a*a - b*b + cx;
				b = 2*old_a*b + cy;
				if(a*a + b*b > SQ_ESC_RADIUS) {
					break;
				}
			}
			double color = 0.0;
			if(loop) {
				// SMOOTHING PASS 1
				register int i; // Reduce error factor
				for(i=0;i<2;i++) {
					old_a = a;
					a = a*a - b*b + cx;
					b = 2*old_a*b + cy;
				}
				color = (double)((max_loop - loop - log(log(sqrt(a*a + b*b))/log(10))/log(ESCAPE))/max_loop);
				// color = (double)((max_loop - loop + (log(log(2) - log(log(a*a + b*b)))/log(2)))/max_loop);
				// color = loop/max_loop;
			}
			res[0] = send[3];
			res[1] = send[4];
			res[2] = color;
			MPI_Send( &res, 3, MPI_DOUBLE, 0, tag, MPI_COMM_WORLD );
		}
	}
	return;
}

int main(int argc, char* argv[]) {
	int ierr, rank;

	MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

	char pname[MPI_MAX_PROCESSOR_NAME];
	int name_len;
	MPI_Get_processor_name(pname, &name_len);
	if(rank == 0) {
		manager(argc, argv);
	} else {
		// printf("Worker at %s\n",pname);
		worker();
	}
	MPI_Finalize();
	return 0;

}
