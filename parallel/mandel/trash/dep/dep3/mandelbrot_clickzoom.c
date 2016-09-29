#include <stdio.h>
#include <stdlib.h>
#include <GL/glut.h>
#include <math.h>
#include "png.c"

#define LOOPS 50
#define SQ_ESC_RADIUS 4
#define ESCAPE 2

#define MAX_SIZE 5000
// #define MAX_SIZE 10000
// MAX_SIZE 10000 REQUIRES 4GB RAM SPACE

/* Switched to dynamic allocation for larger RAM potential
static double colors[MAX_SIZE][MAX_SIZE];
static double display_colors[MAX_SIZE][MAX_SIZE][3];
*/
double** colors;
double*** display_colors;

double zoom_factor = 1.0;
double zoom_change = 2.0;
double loop_factor = 1.05;
double loop_change = 1.04;
double gxc = 0.0; // global x center
double gyc = 0.0; // global y center

static int win_width = 1200;
static int win_height = 900;
/*
static int win_width = MAX_SIZE;
static int win_height = MAX_SIZE;
*/

static double aspect = .75; // inverted -- 3:4 by default

double last_gen_xcenter;
double last_gen_ycenter;
double last_gen_xwidth;
double last_gen_loop_factor;

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

void generate(double xcenter, double ycenter, double xwidth, int int_max_loop) {
	printf("Regenerating...\n");
	int x;
	int y;
	double ywidth = aspect * xwidth;
	double xscalar = win_width / xwidth;
	double yscalar = win_height / ywidth;
	double hwidth = win_width/2.0;
	double hheight = win_height/2.0;

	if(xwidth < .0000000000005) {
		printf("\x1B[31mWARNING:\x1B[0m Approaching double precision barrier!\n");
	}

	last_gen_xcenter = xcenter;
	last_gen_ycenter = ycenter;
	last_gen_xwidth = xwidth;
	last_gen_loop_factor = loop_factor;

	for(y=0;y<win_height;y++) {
		for(x=0;x<win_width;x++) {
			double cx = xcenter + (x - hwidth) / xscalar;
			double cy = ycenter + (y - hheight) / yscalar;

			double a = cx;
			double b = cy;

			double max_loop = (double)int_max_loop;
			int loop = int_max_loop;
			while(--loop) {
				double tmp = a;
				a = a*a - b*b + cx;
				b = 2*tmp*b + cy;
				if(a*a + b*b > SQ_ESC_RADIUS) {
					break;
				}
			}
			double color = 0.0;
			if(loop) {
				color = (max_loop - loop - log(log(sqrt(a*a + b*b)))/log(ESCAPE))/max_loop;
			}
			colors[x][y] = color;
		}
	}
	printf("Generated\n",zoom_factor);
}


void reset() {
	zoom_factor = 1.0;
	loop_factor = 1.02;
	generate(0,0,4,LOOPS);
	gxc = 0.0;
	gyc = 0.0;
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

	double xwidth;

	read = getline(&line, &len, f);
	gxc = atof(line);
	read = getline(&line, &len, f);
	gyc = atof(line);
	read = getline(&line, &len, f);
	xwidth = atof(line);
	read = getline(&line, &len, f);
	loop_factor = atof(line);
	read = getline(&line, &len, f);
	fclose(f);
	zoom_factor = 2 * atof(line);
	generate(gxc,gyc,xwidth,LOOPS * loop_factor);
	glutPostRedisplay();
}

void save_loc(const char* filename) {
	FILE* f = fopen(filename,"w");
	if(f==NULL) {
		printf("Error saving location!\n");
		return;
	}
	fprintf(f,"%20.16f\n",last_gen_xcenter);
	fprintf(f,"%20.16f\n",last_gen_ycenter);
	fprintf(f,"%20.16f\n",last_gen_xwidth);
	fprintf(f,"%20.16f\n",loop_factor / loop_change);
	fprintf(f,"%20.16f\n",zoom_factor);
	fclose(f);
}

void keyfunc(unsigned char key,int xscr,int yscr)
{
	if( key == 'q' ) {
		exit( 0 ) ;
	}
	else if (key == 'r') {
		printf("Reseting...\n");
		reset();
		printf("Reset\n");
	}
	else if (key == 'p') {
		printf("Saving PNG...\n");
		save_png();
		printf("Saved PNG\n");
	}
	else if (key == 'l') {
		printf("Loading config...\n");
		load_loc("save.txt");
		printf("Loaded config\n");
	}
	else if (key == 'd' ) { //debug
		printf("Last generation properties:\n");
		printf("\tx center: %20.16f\n",last_gen_xcenter);
		printf("\ty center: %20.16f\n",last_gen_ycenter);
		printf("\tx width:  %20.16f\n",last_gen_xwidth);
		printf("\tloop factor: %20.16f\n",last_gen_loop_factor);
		printf("\tcalculated zoom levels: %d\n",(int)(log(4/last_gen_xwidth)/log(zoom_change)));
	}
	else if (key == 's') {
		printf("Saving config...\n");
		save_loc("save.txt");
		printf("Saved config\n");
	}
	else if (key == 'z') {
		printf("Reverting...\n");
		load_loc(".fallback.txt");
		printf("Reverted\n");
	}
}

void displayfunc() {
	if(resized) {

		/**************
		!!!! Zoom bug when zooming immediately after resizing
		**************/

		/* This didn't fix it :/
		save_loc(".reshape.txt");
		reset();
		load_loc(".reshape.txt");
		*/

		// Original behavior
		generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth,LOOPS * last_gen_loop_factor);
		resized = 0;
	}
	printf("Displaying...\n");
	glClear(GL_COLOR_BUFFER_BIT);
	int x;
	int y;
	double color;
	for(y=0;y<win_height;y++) {
		for(x=0;x<win_width;x++) {
			color = colors[x][y]*PALETTE_SIZE;
			double left;
			double right;
			right = color - (int)color;
			left = 1 - right;

			// COLOR RENDERER
			
			if(color == 0.0) {
				glColor3f(0.0,0.0,0.0); // black
				display_colors[x][y][0] = 0.0;
				display_colors[x][y][1] = 0.0;
				display_colors[x][y][2] = 0.0;
			} else {
				/* SMOOTHING */
				double red;
				double blue;
				double green;

				double* left_el = palette[(int)(color)%PALETTE_SIZE];
				double* right_el = palette[((int)(color)+1)%PALETTE_SIZE];

				red = left_el[0] * left + right_el[0] * right;
				green = left_el[1] * left + right_el[1] * right;
				blue = left_el[2] * left + right_el[2] * right;

				display_colors[x][y][0] = red;
				display_colors[x][y][1] = green;
				display_colors[x][y][2] = blue;

				glColor3f(red,green,blue);
			}
			glBegin(GL_POINTS);
			glVertex2f(x,y);
			glEnd();
		}
	}
	zoom_factor /= zoom_change;
	loop_factor *= loop_change;
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
void mousefunc(int button,int state,int xscr,int yscr)
{
	if(button==GLUT_LEFT_BUTTON) {
		if(state==GLUT_DOWN) {
			save_loc(".fallback.txt");
			double gfx = 4 * zoom_factor;
			double gfy = aspect * gfx;
			gxc += gfx * (xscr - win_width/2) / win_width;
			gyc += gfy * (win_height/2 - yscr) / win_height;
			generate(gxc,gyc,gfx,LOOPS*(loop_factor));
			glutPostRedisplay();
		}
	}
}

int main(int argc, char* argv[]) {
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
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
	glutInitWindowSize(win_width,win_height);
	glutInitWindowPosition(100,LOOPS);
	glutCreateWindow("");
	glClearColor(1.0,1.0,1.0,0.0);
	glShadeModel(GL_SMOOTH);

	generate(0.0,0.0,4.0,LOOPS);

	glutDisplayFunc(displayfunc);
	glutReshapeFunc(reshapefunc);
	glutMouseFunc(mousefunc);
	glutKeyboardFunc(keyfunc);
	glutMainLoop();

	return 0;

}
