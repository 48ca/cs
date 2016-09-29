#include <stdlib.h>
#include <string.h>
#include <GL/glut.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <mpi.h>
#include <gmp.h>
#include "png.c"

#define SQ_ESC_RADIUS 4
#define ESCAPE 2

#define MAX_SIZE 10000
#define SEND_STR_SIZE 1000

/* Compiling and running
 *
 * Compile with:
 *    mpicc -lGL -lGLU -lglut -lpng -lgmp -lm -O2 mandelbrot.c -o mandelexec
 *
 * Run with:
 *    mpirun -np num_proc [MPI options] mandelexec
 *    
 *    Flags:
 *    	 -x: limit GL functions (better X11 forwarding performance)
 *    	 -h: set height (use 0 for max height)
 *    	 -w: set width (use 0 for max width)
 *    	 --load: load saved config (save.txt)
 *    	 --no-gl: disable all GL functions (for use when there is no display)
 *    	 --gmp: force GMP arithmetic
 *       --no-smoothing: disable smoothing
 *
 * Notes:
 *     To run with GL functions, the manager must be at a node that is connected to a display
 *
*/

// MPI
const int tag = 0;
const int gmp_tag = 1;
const int kill_tag = 2;
const int options_tag = 3;
int num_procs;
MPI_Status status;
int rank;

double* colors;
double* display_colors;
double min_color;
double max_color;

double loop_scalar = 30;

mpf_t gxc;
mpf_t gyc;
mpf_t oxw;

static unsigned int win_width = 1200;
static unsigned int win_height = 900;
static double aspect;

mpf_t last_gen_xcenter;
mpf_t last_gen_ycenter;
mpf_t last_gen_xwidth;

int xinit; // for use with drag function
int yinit;

int loops = 1;

#define PALETTE_SCALE 3
double palette[][3] = {

		// Ultra Fractal (Linear)
		#define PALETTE_SIZE 15
		{0.0,7.0/255,100.0/255},
		{32.0/255,107.0/255,203.0/255},
		{237.0/255,1.0,1.0},
		{1.0,170.0/255,0.0},
		{0.0,2.0/255,0.0},

		// + Ultra Fractal (BG Flip)
		// #define PALETTE_SIZE 5
		{0.0,100.0/255,7.0/255},
		{32.0/255,203.0/255,107.0/255},
		{237.0/255,1.0,1.0},
		{1.0,0.0,170.0/255},
		{0.0,0.0,2.0/255},

		// + Custom
		// #define PALETTE_SIZE 5
		{0.0,7.0/255,60.0/255},
		{1.0,105.0/255,0.0},
		{1.0,150.0/255,0.2},
		{32.0/255,107.0/255,203.0/255},
		{10.0/255,200.0/255,30.0/255}
		
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

// Execution arguments
int use_gmp = 0;
int use_glut = 1;
int load_on_init = 0;
int x11 = 0;
int smoothing = 1;

// Function prototypes
// Generate set
void generate(mpf_t xcenter, mpf_t ycenter, mpf_t xwidth);
void generateGMP(mpf_t xcenter, mpf_t ycenter, mpf_t xwidth);
void generateDOUBLE(double xcenter, double ycenter, double xwidth);
// Load and save generation parameters
void load_loc(const char* filename);
void save_loc(const char* filename);
// GL Controls
void keyfunc(unsigned char key,int xscr,int yscr);
void mousefunc(int button,int state,int xscr,int yscr);
// GL Display
void displayfunc();
void reshapefunc(int wscr,int hscr);
void dragfunc(int x, int y);
void add_color(int x, int y, double color);
// MPI
void manager(int argc, char* argv[]);
void worker();
void kill_nodes();

void generate(mpf_t xcenter, mpf_t ycenter, mpf_t xwidth) {
	printf("Regenerating...\n");
	if(use_gmp) generateGMP(xcenter, ycenter, xwidth);
	else generateDOUBLE(mpf_get_d(xcenter), mpf_get_d(ycenter), mpf_get_d(xwidth));
	printf("Generated\n");
	return;
}

void generateDOUBLE(double xcenter, double ycenter, double xwidth) {
	glClear(GL_COLOR_BUFFER_BIT);
	int x;
	int y;
	double ywidth = aspect * xwidth;
	double xscalar = xwidth / win_width;
	double yscalar = ywidth / win_height;

	double hwidth = win_width/2.0;
	double hheight = win_height/2.0;

	int max_loop = (int)(loops * loop_scalar);

	mpf_set_d(last_gen_xcenter,xcenter);
	mpf_set_d(last_gen_ycenter,ycenter); 
	mpf_set_d(last_gen_xwidth,xwidth);

	int node = 1;
	int recv = 0;
	int sent = 0;
	double res[MAX_SIZE + 1];
	double send[6];

	send[4] = (double)max_loop;

	for(y=0;y<win_height;y++) {
		send[0] = -hwidth*xscalar + xcenter;
		send[1] = xscalar;
		send[2] = (double)win_width;
		send[3] = (y-hheight)*yscalar + ycenter;
		send[5] = (double)y;
		MPI_Send(&send,6,MPI_DOUBLE,node++,tag,MPI_COMM_WORLD);
		sent++;
		if(node == num_procs) break;
	}
	for(;y<win_height;y++) {
		send[0] = -hwidth*xscalar + xcenter;
		send[1] = xscalar;
		send[2] = (double)win_width;
		send[3] = (y-hheight)*yscalar + ycenter;
		send[5] = (double)y;
		MPI_Recv(&res, MAX_SIZE + 1, MPI_DOUBLE, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status);
		recv++;
		node = status.MPI_SOURCE;
		MPI_Send(&send,6,MPI_DOUBLE,node++,tag,MPI_COMM_WORLD);
		sent++;
		if(!x11 && use_glut)
			glBegin(GL_POINTS);
		int color_y = (int)res[0];
		for(x=0;x<win_width;x++) {
			colors[x*MAX_SIZE + color_y] = res[x+1];
			add_color(x, color_y, res[x+1]);
		}
		printf("Generating: %f               \r",100*recv/(double)win_height);
		fflush(stdout);
		if(!x11 && use_glut) {
			glEnd();
			glFlush();
		}
	}
	while(recv<sent) {
		MPI_Recv( &res, MAX_SIZE + 1, MPI_DOUBLE, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status );
		recv++;
		if(!x11 && use_glut)
			glBegin(GL_POINTS);
		int color_y = (int)res[0];
		for(x=0;x<win_width;x++) {
			colors[x*MAX_SIZE + color_y] = res[x+1];
			add_color(x, color_y, res[x+1]);
		}
		printf("Generating: %f              \r",100*recv/(double)win_height);
		fflush(stdout);
		if(!x11 && use_glut) {
			glEnd();
			glFlush();
		}
	}
	printf("Generating: Done               \n");
}

void generateGMP(mpf_t xcenter, mpf_t ycenter, mpf_t xwidth) {

	glClear(GL_COLOR_BUFFER_BIT);
	int x;
	int y;

	mpf_t ywidth;
	mpf_init_set_d(ywidth, aspect);
	mpf_mul(ywidth, ywidth, xwidth);

	mpf_t xscalar;
	mpf_init(xscalar);
	mpf_div_ui(xscalar, xwidth, (unsigned long) win_width);

	mpf_t yscalar;
	mpf_init(yscalar);
	mpf_div_ui(yscalar, ywidth, (unsigned long) win_height);

	double hwidth = win_width/2.0;
	double hheight = win_height/2.0;

	int max_loop = (int)(loops*loop_scalar);

	mpf_set(last_gen_xcenter, xcenter);
	mpf_set(last_gen_ycenter, ycenter);
	mpf_set(last_gen_xwidth, xwidth);

	if(mpf_get_d(xwidth) < 0.0000000000000001L) {
		printf("\x1B[31mWARNING:\x1B[0m x-width hit long double precision barrier!\n");
	}

	int node = 1;
	int recv = 0;
	int sent = 0;
	char* send[4];

	double res[MAX_SIZE + 1];
	char ystr[100];
	char max_loop_str[100];

	sprintf(max_loop_str,"%d",max_loop);
	send[2] = max_loop_str;
	max_color = 0.0;
	min_color = 1.0;

	mpf_t tmp;
	mpf_init(tmp);

	char send_str[SEND_STR_SIZE];

	for(y=0;y<win_height;y++) {
		mpf_set_d(tmp, (double) -hwidth);
		mpf_mul(tmp, tmp, xscalar);
		mpf_add(tmp, tmp, xcenter);

		char send_arg0[300];
		send[0] = send_arg0;
		char send_arg1[100];
		send[1] = send_arg1;

		gmp_sprintf(send[0], "%.Ff:%.Ff:%d", tmp, xscalar, win_width);
		mpf_set_d(tmp, (double)y - hheight);
		mpf_mul(tmp, tmp, yscalar);
		mpf_add(tmp, tmp, ycenter);
		gmp_sprintf(send[1], "%.Ff", tmp);
		sprintf(ystr,"%d",y);
		send[3] = ystr;
		sprintf(send_str,"%s:%s:%s:%s:\0",send[0],send[1],send[2],send[3]);
		MPI_Send( &send_str, SEND_STR_SIZE, MPI_CHAR, node++, gmp_tag, MPI_COMM_WORLD );
		sent++;
		if(node == num_procs) break;
	}
	for(;y<win_height;y++) {
		mpf_set_d(tmp, (double) -hwidth);
		mpf_mul(tmp, tmp, xscalar);
		mpf_add(tmp, tmp, xcenter);

		char send_arg0[300];
		send[0] = send_arg0;
		char send_arg1[100];
		send[1] = send_arg1;

		gmp_sprintf(send[0], "%.Ff:%.Ff:%d", tmp, xscalar, win_width);
		mpf_set_d(tmp, (double)y - hheight);
		mpf_mul(tmp, tmp, yscalar);
		mpf_add(tmp, tmp, ycenter);
		gmp_sprintf(send[1], "%.Ff", tmp);

		sprintf(ystr,"%d",y);
		send[3] = ystr;
		sprintf(send_str,"%s:%s:%s:%s:\0",send[0],send[1],send[2],send[3]);
		MPI_Recv( &res, MAX_SIZE + 1, MPI_DOUBLE, MPI_ANY_SOURCE, gmp_tag, MPI_COMM_WORLD, &status );
		recv++;
		node = status.MPI_SOURCE;
		MPI_Send( &send_str, SEND_STR_SIZE , MPI_CHAR, node++, gmp_tag, MPI_COMM_WORLD );
		sent++;
		if(!x11 && use_glut) glBegin(GL_POINTS);
		for(x=0;x<win_width;x++) {
			int color_y = (int)res[0];
			colors[x * MAX_SIZE + color_y] = res[x+1];
			add_color(x, color_y, res[x+1]);
		}
		printf("Generating: %f\r",100*recv/(double)win_height);
		fflush(stdout);
		if(!x11 && use_glut) {
			glEnd();
			glFlush();
		}
	}
	while(recv<sent) {
		MPI_Recv( &res, MAX_SIZE + 1, MPI_DOUBLE, MPI_ANY_SOURCE, gmp_tag, MPI_COMM_WORLD, &status );
		recv++;
		if(!x11 && use_glut) glBegin(GL_POINTS);
		for(x=0;x<win_width;x++) {
			int color_y = (int)res[0];
			colors[x * MAX_SIZE + color_y] = res[x+1];
			add_color(x, color_y, res[x+1]);
		}
		printf("Generating: %f\r",100*recv/(double)win_height);
		fflush(stdout);
		if(!x11 && use_glut) {
			glEnd();
			glFlush();
		}
	}

	mpf_clear(ywidth);
	mpf_clear(xscalar);
	mpf_clear(yscalar);
	mpf_clear(tmp);
	printf("Generating: Done\n");
}


void reset() {
	mpf_set_ui(oxw, 4ul);
	mpf_set_ui(gxc, 0ul);
	mpf_set_ui(gyc, 0ul);
	loop_scalar = 30;
	generate(gxc, gyc, oxw);
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
			pixel-> red = (int)(255 * display_colors[MAX_SIZE * 3 * x + 3*y]);
			pixel-> green = (int)(255 * display_colors[MAX_SIZE * 3 * x + 3*y + 1]);
			pixel-> blue = (int)(255 * display_colors[MAX_SIZE * 3 * x + 3*y + 2]);
		}
	}
	// defined in png.c
	const char* of = "frac.png";
	save_png_to_file(&fractal,of);
	printf("Image saved to %s\n",of);
	free(fractal.pixels);
	return;
}

void load_loc(const char* filename) {
	FILE* f = fopen(filename,"r");
	if(f==NULL) {
		fprintf(stderr,"Error loading location!\n");
		return;
	}
	char* line = NULL;
	size_t len = 0;
	ssize_t read;

	read = getline(&line, &len, f);
	mpf_set_str(gxc,line,10);
	mpf_set_str(last_gen_xcenter,line,10);
	read = getline(&line, &len, f);
	mpf_set_str(gyc,line,10);
	mpf_set_str(last_gen_ycenter,line,10);
	read = getline(&line, &len, f);
	mpf_set_str(oxw,line,10);
	mpf_set_str(last_gen_xwidth,line,10);
	read = getline(&line, &len, f);
	loop_scalar = atoi(line);
	fclose(f);
}

void save_loc(const char* filename) {
	FILE* f = fopen(filename,"w");
	if(f==NULL) {
		fprintf(stderr,"Error saving location!\n");
		return;
	}
	gmp_fprintf(f,"%.Ff\n",last_gen_xcenter);
	gmp_fprintf(f,"%.Ff\n",last_gen_ycenter);
	gmp_fprintf(f,"%.Ff\n",last_gen_xwidth);
	fprintf(f,"%f\n",loop_scalar);
	fclose(f);
}

void kill_nodes() {
	int node;
	double send[3] = {0};
	for(node=1;node<num_procs;node++) {
		MPI_Send( &send, 3, MPI_DOUBLE, node, kill_tag, MPI_COMM_WORLD );
	}
}

void keyfunc(unsigned char key,int xscr,int yscr) {

	register int i;

	mpf_t xwidth;
	mpf_init(xwidth);

	// CONTROLS
	switch(key) {
		case 'q':
			printf("Exiting\n");
			kill_nodes();
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
			generate(gxc, gyc, oxw);
			glutPostRedisplay();
			printf("Loaded config\n");
			break;
		case 'd': //debug
			printf("Last generation properties:\n");
			gmp_printf("\tx center: %.Ff\n",last_gen_xcenter);
			gmp_printf("\ty center: %.Ff\n",last_gen_ycenter);
			gmp_printf("\tx width:  %.Ff\n",last_gen_xwidth);
			printf("\testimated magnification level: 10^%f\n",(log(4) - log(mpf_get_d(last_gen_xwidth)))/log(10));
			printf("\tloops: %f\n",loops * loop_scalar);
			break;
		case 's':
			printf("Saving config...\n");
			save_loc("save.txt");
			printf("Saved config\n");
			break;
		case 'z':
			printf("Reverting...\n");
			load_loc(".fallback.txt");
			glutPostRedisplay();
			printf("Reverted\n");
			break;
		case 'i':
			printf("Zooming in...\n");
			mpf_div_ui(xwidth, last_gen_xwidth,2ul);
			generate(last_gen_xcenter,last_gen_ycenter,xwidth);
			glutPostRedisplay();
			printf("Zoom finished\n");
			break;
		case 'o':
			printf("Zooming out...\n");
			mpf_mul_ui(xwidth, last_gen_xwidth,2ul);
			generate(last_gen_xcenter,last_gen_ycenter,xwidth);
			glutPostRedisplay();
			printf("Zoom finished\n");
			break;
		case 'f':
			printf("Toggling fullscreen...\n");
			if(fullscreen) {
				glutPositionWindow(120,120);
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
	}
	mpf_clear(xwidth);
}

void displayfunc() {
	if(resized) {
		generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth);
		resized = 0;
	}
	printf("Displaying...\n");
	int x;
	int y;
	double color;
	glBegin(GL_POINTS);
	for(y=0;y<win_height;y++) {
		for(x=0;x<win_width;x++) {
			double red = display_colors[MAX_SIZE*3*x + 3 * y];
			double green = display_colors[MAX_SIZE*3*x + 3 * y + 1];
			double blue = display_colors[MAX_SIZE*3*x + 3 * y + 2];
			glColor3f(red,green,blue);
			glVertex2f(x,y);
		}
	}
	glEnd();
	glFlush();
	printf("Displayed\n");
}

void add_color(int x, int y, double color) {
	
	double red = 0.0;
	double green = 0.0;
	double blue = 0.0;

	if(color != 0.0) {
		color *= PALETTE_SIZE * PALETTE_SCALE;
		double* left_el = palette[(int)(color)%PALETTE_SIZE];
		double* right_el = palette[((int)(color)+1)%PALETTE_SIZE];

		double left;
		double right;
		right = color - (int)color;
		left = 1 - right;

		red = left_el[0] * left + right_el[0] * right;
		green = left_el[1] * left + right_el[1] * right;
		blue = left_el[2] * left + right_el[2] * right;
		if(red < 0) red = 0;
		if(blue < 0) blue = 0;
		if(green < 0) green = 0;
	}
	display_colors[MAX_SIZE*3*x + 3 * y] = red;
	display_colors[MAX_SIZE*3*x + 3 * y + 1] = green;
	display_colors[MAX_SIZE*3*x + 3 * y + 2] = blue;
	if(!x11 && use_glut) {
		glColor3f(red,green,blue);
		glVertex2f(x,y);
	}
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

void mousefunc(int button,int state,int xscr,int yscr)
{
	if(button==GLUT_LEFT_BUTTON) {
		if(state==GLUT_DOWN) {
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
			glVertex2f(x,y);
			glVertex2f(xinit,y);
			glVertex2f(x,y);
			glVertex2f(x,yinit);
			glVertex2f(xinit,yinit);
			glVertex2f(x,yinit);
			glVertex2f(xinit,yinit);
			glVertex2f(xinit,y);
			glEnd();
			glFlush();

			mpf_set_d(oxw, abs(x-xinit));
			mpf_div_ui(oxw, oxw, win_width);
			mpf_mul(oxw, last_gen_xwidth, oxw);

			mpf_set_d(gxc, ((x+xinit)/(2*win_width) - .5));
			mpf_mul(gxc, last_gen_xwidth, gxc);
			mpf_add(gxc, last_gen_xcenter, gxc);
			
			mpf_set_d(gyc, aspect*((y+yinit)/(2*win_height) - .5));
			mpf_mul(gyc, last_gen_xwidth, gyc);
			mpf_add(gyc, last_gen_ycenter, gyc);

			generate(gxc,gyc,oxw);
			glutPostRedisplay();
		}
	}
}

void dragfunc(int x, int y) {
	/*
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
	glFlush();
	glutSwapBuffers();
	*/
}

void manager(int argc, char* argv[]) {
	printf("Allocating...\n");
	colors = (double*)(malloc(sizeof(double) * MAX_SIZE * MAX_SIZE));
	if(colors == NULL) { fprintf(stderr, "Error allocating memory!\n"); goto kill; }
	display_colors = (double*)(malloc(sizeof(double) * MAX_SIZE * MAX_SIZE * 3));
	if(display_colors == NULL)  { fprintf(stderr, "Error allocating memory!\n"); goto kill; }
	printf("Allocated\n");
	aspect = (double)win_height/win_width;
	if(use_glut) {

		glutInit(&argc, argv);
		glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB);
		glutInitWindowSize(win_width,win_height);
		glutInitWindowPosition(100,100);
		glutCreateWindow("");
		glClearColor(0.0,0.0,0.0,0.0);
		glShadeModel(GL_SMOOTH);

	}

	mpf_init(gxc);
	mpf_init(gyc);
	mpf_init(oxw);

	last_gen_xcenter; // = 0.0L;
	last_gen_ycenter; // = 0.0L;
	last_gen_xwidth;  // = 4.0L;

	mpf_init_set_d(last_gen_xcenter,0.0);
	mpf_init_set_d(last_gen_ycenter,0.0);
	mpf_init_set_d(last_gen_xwidth,4.0);

	if(load_on_init) {
		load_loc("save.txt");
	}
	if(use_glut) {

		glutReshapeFunc(reshapefunc);
		glutDisplayFunc(displayfunc);
		glutMouseFunc(mousefunc);
		glutMotionFunc(dragfunc);
		glutKeyboardFunc(keyfunc);
		glutMainLoop();

	} else {
		// Custom instructions
		generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth);
		printf("Saving...\n");
		save_png();
		printf("Saved\n");
	}

	free(display_colors);
	free(colors);

	goto kill;

	kill:
		printf("Killing nodes...\n");
		kill_nodes();

		mpf_clear(gxc);
		mpf_clear(gyc);
		mpf_clear(oxw);
		mpf_clear(last_gen_xwidth);
		mpf_clear(last_gen_xcenter);
		mpf_clear(last_gen_ycenter);

	return;
}

void worker() {
	char* send[5];
	double res[MAX_SIZE + 1];

	mpf_t cx;
	mpf_init(cx);
	mpf_t cy;
	mpf_init(cy);

	mpf_t a;
	mpf_init(a);
	mpf_t b;
	mpf_init(b);

	mpf_t old_a;
	mpf_init(old_a);
	mpf_t old_b;
	mpf_init(old_b);

	mpf_t abs;
	mpf_init(abs);

	mpf_t asq;
	mpf_init(asq);
	mpf_t bsq;
	mpf_init(bsq);

	mpf_t dx;
	mpf_init(dx);

	int recv = 0;

	while(1) {
		char send_str[SEND_STR_SIZE] = {'\0'};
		double send_darr[5];

		double cxd;
		double dxd;
		int xloops;
		double cyd;
		int max_loop;
		double row;

		double color;

		register int currx;

		MPI_Probe(0, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
		if(status.MPI_TAG == kill_tag) { break; } 
		else {
			if(status.MPI_TAG == gmp_tag) {
				MPI_Recv( &send_str, SEND_STR_SIZE, MPI_CHAR, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &status );
				recv++;
				char* delim = send_str;
				char* tmp = delim;
				delim = strchr(delim+1, ':');
				*delim = '\0';
				mpf_set_str(cx, tmp,10);
				tmp = delim+1;
				delim = strchr(delim+1, ':');
				*delim = '\0';
				mpf_set_str(dx, tmp, 10);
				tmp = delim+1;
				delim = strchr(delim+1, ':');
				*delim = '\0';
				xloops = atoi(tmp);
				tmp = delim+1;
				delim = strchr(delim+1, ':');
				*delim = '\0';
				mpf_set_str(cy, tmp, 10);
				send[2] = delim+1;
				delim = strchr(delim+1, ':');
				*delim = '\0';
				send[3] = delim+1;
				delim = strchr(delim+1, ':');
				*delim = '\0';
				res[0] = atof(send[3]);
				// cx, dx, xloops, cy, max_loop, row

				max_loop = atoi(send[2]);
				for(currx = 0; currx < xloops; currx++) {
					color = 0.0;
					mpf_add(cx, cx, dx);

					mpf_set(a, cx);
					mpf_set(b, cy);

					int pseudo = max_loop/2;
					int loop = max_loop;
					while(--pseudo && --loop) {
						mpf_set(old_a,a);
						mpf_set(old_b,b);
						mpf_pow_ui(a,a,2ul);
						mpf_pow_ui(b,b,2ul);
						mpf_sub(a, a, b);
						mpf_add(a, a, cx);
						mpf_mul_ui(b, old_b, 2ul);
						mpf_mul(b, b, old_a);
						mpf_add(b, b, cy);
						mpf_pow_ui(asq, a, 2ul);
						mpf_pow_ui(bsq, b, 2ul);
						mpf_add(abs, asq, bsq);
						if(mpf_get_d(abs) > SQ_ESC_RADIUS) {
							break;
						}
					}
					if(!pseudo && loop) {
						double ad = mpf_get_d(a);
						double bd = mpf_get_d(b);
						double dcx = mpf_get_d(cx);
						double dcy = mpf_get_d(cy);
						double old_ad;
						while(--loop) {
							old_ad = ad;
							ad = ad*ad - bd*bd + dcx;
							bd = 2*old_ad*bd + dcy;
							if(ad*ad + bd*bd > SQ_ESC_RADIUS) {
								break;
							}
						}
						if(loop) {
							register int i;
							for(i=0;i<2;i++) {
								old_ad = ad;
								ad = ad*ad - bd*bd + dcx;
								bd = 2*old_ad*bd + dcy;
							}
							if(smoothing) color = (double)((max_loop - loop - log(log(sqrt(ad*ad + bd*bd))/log(10))/log(ESCAPE))/max_loop);
							else color = (double)loop/max_loop;
						}
					} else {
						if(loop) {
							register int i; // Reduce error factor
							for(i=0;i<2;i++) {
								mpf_set(old_a,a);
								mpf_set(old_b,b);

								mpf_pow_ui(a,a,2ul);
								mpf_pow_ui(b,b,2ul);
								mpf_sub(a, a, b);
								mpf_add(a, a, cx);
								mpf_mul_ui(b, old_b, 2ul);
								mpf_mul(b, b, old_a);
								mpf_add(b, b, cy);
							}
							double ad = mpf_get_d(a);
							double bd = mpf_get_d(b);
							if(smoothing) color = (double)((max_loop - loop - log(log(sqrt(ad*ad + bd*bd))/log(10))/log(ESCAPE))/max_loop);
							else color = (double)loop/max_loop;
						}
					}
					res[currx+1] = color;
				}
				MPI_Send( &res, MAX_SIZE + 1, MPI_DOUBLE, 0, gmp_tag, MPI_COMM_WORLD );
			} else if(status.MPI_TAG == tag) {
				MPI_Recv( &send_darr, 6, MPI_DOUBLE, 0, tag, MPI_COMM_WORLD, &status );
				cxd = send_darr[0];
				dxd = send_darr[1];
				xloops = (int)send_darr[2];
				cyd = send_darr[3];
				max_loop = (int)send_darr[4];
				row = send_darr[5];

				double a;
				double b;
				double old_a;

				int ts = time(NULL);

				for(currx = 0; currx < xloops; currx++) {
					cxd += dxd;
					int loop = max_loop;
					a = cxd;
					b = cyd;
					color = 0.0;
					while(--loop) {
						old_a = a;
						a = a*a - b*b + cxd;
						b = 2*old_a*b + cyd;
						if(a*a + b*b > SQ_ESC_RADIUS) {
							break;
						}
					} if(loop) {
						register int i;
						for(i=0;i<2;i++) {
							old_a = a;
							a = a*a - b*b + cxd;
							b = 2*old_a*b + cyd;
						}
						if(smoothing) color = (double)((max_loop - loop - log(log(sqrt(a*a + b*b))/log(10))/log(ESCAPE))/max_loop);
						else color = (double)loop/max_loop;
					}
					res[currx + 1] = color;
				}
				res[0] = row;
				MPI_Send( &res, MAX_SIZE + 1, MPI_DOUBLE, 0, tag, MPI_COMM_WORLD );
			} else { // Receiving options tag
				MPI_Recv(&smoothing, 1, MPI_INT, 0, options_tag, MPI_COMM_WORLD, &status);
			}
		}
	}
	mpf_clear(a);
	mpf_clear(old_a);
	mpf_clear(b);
	mpf_clear(old_b);
	return;
}

int main(int argc, char* argv[]) {

	MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

	char pname[MPI_MAX_PROCESSOR_NAME];
	int name_len;
	MPI_Get_processor_name(pname, &name_len);
	
	mp_bitcnt_t prec = 256;
	mpf_set_default_prec(prec);

	if(rank == 0) {
		int error = 0;
		register int arg;
		for(arg=1;arg<argc;arg++) {
			if(!strcmp("--no-gl",argv[arg])) use_glut = 0;
			else if(!strcmp("--gmp",argv[arg])) use_gmp = 1;
			else if(!strcmp("--load",argv[arg])) load_on_init = 1;
			else if(!strcmp("--no-smoothing",argv[arg])) {
				smoothing = 0;
				register int nodes;
				for(nodes = 1;nodes<num_procs;nodes++)
					MPI_Send(&smoothing, 1, MPI_INT, nodes, options_tag, MPI_COMM_WORLD);
			}
			else if(!strcmp("-x",argv[arg])) x11 = 1;
			else if(!strcmp("-h",argv[arg])) {
				if (arg+1 < argc && argv[arg+1][0] != '-') {
					win_height = atoi(argv[++arg]);
					if(win_height == 0 || win_height > MAX_SIZE) {
						win_height = MAX_SIZE;
						printf("Defaulting height to %d\n",win_height);
					}
				} else {
					fprintf(stderr,"No argument passed to -h\n");
					error = 1;
				}
			}
			else if(!strcmp("-w",argv[arg])) {
				if (arg+1 < argc && argv[arg+1][0] != '-') {
					win_width = atoi(argv[++arg]);
					if(win_width == 0 || win_width > MAX_SIZE) {
						win_width = MAX_SIZE;
						printf("Defaulting width to %d\n",win_width);
					}
				} else {
					fprintf(stderr,"No argument passed to -w\n");
					error = 1;
				}
			}
			else {
				fprintf(stderr,"Unrecognized argument %s\n",argv[arg]);
				error = 1;
			}
		}
		if(error) {
			kill_nodes();
			MPI_Finalize();
			return 0;
		}

		printf("Options:\n");
		if(!use_glut) printf("\tGL disabled\n");
		if(use_gmp) printf("\tGMP enabled\n");
		if(load_on_init) printf("\tLoading config\n");
		if(x11) printf("\tX11 forwarding mode enabled\n");
		if(!smoothing) printf("\tSmoothing disabled\n");

		manager(argc, argv);
	} else {
		// printf("Worker at %s %d\n",pname,num_procs);
		worker();
	}
	MPI_Finalize();
	return 0;
}
