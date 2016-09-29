#include <stdio.h>
#include <stdlib.h>
#include <GL/glut.h>
#include <math.h>

#define LOOPS 38
#define SQ_ESC_RADIUS 4

// initial loop orig 50

static double colors[10000][10000]; // 10000x10000 max height and width

double zoom_factor = 1.0;
double zoom_change = 2.0;
double loop_factor = 1.05; // 1/.95
double loop_change = 1.04; //1.02
double gxc = 0.0;
double gyc = 0.0;

static int width = 1200;
static int height = 900;
static double aspect = .75;

double last_gen_xcenter;
double last_gen_ycenter;
double last_gen_xwidth;
double last_gen_max_loop;


int resized = 0;

void generate(double xcenter, double ycenter, double xwidth, int int_max_loop) {
	int x;
	int y;
	double ywidth = aspect * xwidth;
	double xdenom = width / xwidth;
	double ydenom = height / ywidth;
	double hwidth = width/2.0;
	double hheight = height/2.0;

	last_gen_xcenter = xcenter;
	last_gen_ycenter = ycenter;
	last_gen_xwidth = xwidth;
	last_gen_max_loop = int_max_loop;

	for(y=0;y<height;y++) {
		for(x=0;x<width;x++) {
			double cx = xcenter + (x - hwidth) / xdenom;
			double cy = ycenter + (y - hheight) / ydenom;

			double a = cx;
			double b = cy;

			double max_loop = (double)int_max_loop;
			int loop = (int)max_loop;
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
				// color = -log(-log((double)(loop)/max_loop));
				color = 1 - log(log(sqrt(a*a + b*b))) / log(2);
			}
			colors[x][y] = color;
		}
	}
	printf("generated with zoom factor %d\n",(int)(1/zoom_factor));
}

void reset() {
	zoom_factor = 1.0;
	loop_factor = 1.02;
	generate(0,0,4,LOOPS);
	gxc = 0.0;
	gyc = 0.0;
	glutPostRedisplay();
}

void keyfunc(unsigned char key,int xscr,int yscr)
{
	if( key == 'q' ) {
		exit( 0 ) ;
	}
	else if (key == 'r') {
		reset();
	}
}

void displayfunc() {
	if(resized) {
		generate(last_gen_xcenter,last_gen_ycenter,last_gen_xwidth,last_gen_max_loop);
		resized = 0;
	}
	glClear(GL_COLOR_BUFFER_BIT);
	int x;
	int y;
	double color;
	for(y=0;y<height;y++) {
		for(x=0;x<width;x++) {
			color = colors[x][y];
			// printf("%d %d %d\n",color,x,y);

			// COLORS
			
			double red = 1 - color/2;
			double blue = 1 - color/4;
			double green = 1 - color;

			glColor3f(red,green,blue);
			// glColor3f(1.0, 0.0, 0.0);
			glBegin(GL_POINTS);
			glVertex2f(x,y);
			glEnd();
		}
	}
	printf("Displayed\n");
	zoom_factor /= zoom_change;
	loop_factor *= loop_change;
	glutSwapBuffers();
}

void reshapefunc(int wscr,int hscr)
{
	width = wscr;
	height = hscr;
	aspect = (double)(height) / width;
	glViewport(0,0,(GLsizei)width,(GLsizei)height);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluOrtho2D(0.0,1.0*width,0.0,1.0*height);
	glMatrixMode(GL_MODELVIEW);
	resized = 1;
	glutPostRedisplay();
}
void mousefunc(int button,int state,int xscr,int yscr)
{
	if(button==GLUT_LEFT_BUTTON) {
		if(state==GLUT_DOWN) {
			printf("%d %d\n",xscr,yscr);
			double gfx = 4 * zoom_factor;
			double gfy = aspect * gfx;
			gxc += gfx * (xscr - width/2) / width;
			gyc += gfy * (height/2 - yscr) / height;
			generate(gxc,gyc,gfx,LOOPS*(loop_factor));
			glutPostRedisplay();
		}
	}
}
int main(int argc, char* argv[]) {

	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
	glutInitWindowSize(width,height);
	glutInitWindowPosition(100,LOOPS);
	glutCreateWindow("");
	glClearColor(1.0,1.0,1.0,0.0);
	glShadeModel(GL_SMOOTH);
	generate(0.0,0.0,4.0,LOOPS);
	// glutIdleFunc(generate);
	glutDisplayFunc(displayfunc);
	glutReshapeFunc(reshapefunc);
	glutMouseFunc(mousefunc);
	glutKeyboardFunc(keyfunc);
	glutMainLoop();
	return 0;

}
