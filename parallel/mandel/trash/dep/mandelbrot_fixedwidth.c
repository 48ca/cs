#include <stdio.h>
#include <stdlib.h>
#include <GL/glut.h>
#include <math.h>

#define HEIGHT 900
#define WIDTH 1200

#define LOOPS 50

static double colors[WIDTH][HEIGHT];
double zoom_factor = 1.0;
double zoom_change = 2.0;
double loop_factor = .9;
double loop_change = 1.05;
double gxc = 0.0;
double gyc = 0.0;

static int width = 900;
static int height = 1200;

void generate(double xcenter, double ycenter, double xwidth, int int_max_loop) {
	int x;
	int y;
	double ywidth = 3 * xwidth / 4;
	double xdenom = WIDTH / xwidth;
	double ydenom = HEIGHT / ywidth;
	double hwidth = WIDTH/2.0;
	double hheight = HEIGHT/2.0;
	printf("%d\n",int_max_loop);
	for(y=0;y<HEIGHT;y++) {
		for(x=0;x<WIDTH;x++) {
			double cx = xcenter + (x - hwidth) / xdenom;
			double cy = ycenter + (y - hheight) / ydenom;

			double a = cx;
			double b = cy;

			double max_loop = (double)int_max_loop;
			int loop = (int)max_loop;
			while(loop--) {
				double tmp = a;
				a = a*a - b*b + cx;
				b = 2*tmp*b + cy;
				if(a*a + b*b > 4) {
					break;
				}
			}
			double color = 0.0;
			if(loop) {
				color = (double)(loop)/max_loop;
			}
			colors[x][y] = color;
		}
	}
	printf("generated\n");
}

void reset() {
	zoom_factor = 1.0;
	loop_factor = .9;
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
	glClear(GL_COLOR_BUFFER_BIT);
	int x;
	int y;
	double color;
	for(y=0;y<HEIGHT;y++) {
		for(x=0;x<WIDTH;x++) {
			color = colors[x][y];
			// printf("%d %d %d\n",color,x,y);
			glColor3f(color,color/2,1-color);
			// glColor3f(1.0, 0.0, 0.0);
			glBegin(GL_POINTS);
			glVertex2f(x,y);
			glEnd();
		}
	}
	printf("displayed\n");
	zoom_factor /= zoom_change;
	loop_factor /= loop_change;
	glutSwapBuffers();
}

void reshapefunc(int wscr,int hscr)
{
	width = wscr;
	height = hscr;
	glViewport(0,0,(GLsizei)WIDTH,(GLsizei)HEIGHT);
	glMatrixMode(GL_PROJECTION);
	glLoadIdentity();
	gluOrtho2D(0.0,1.0*WIDTH,0.0,1.0*HEIGHT);
	glMatrixMode(GL_MODELVIEW);
}
void mousefunc(int button,int state,int xscr,int yscr)
{
	if(button==GLUT_LEFT_BUTTON) {
		if(state==GLUT_DOWN) {
			printf("%d %d\n",xscr,yscr);
			double gfx = 4 * zoom_factor;
			double gfy = 3 * gfx / 4;
			gxc += gfx * (xscr - WIDTH/2) / WIDTH;
			gyc += gfy * (HEIGHT/2 - yscr) / HEIGHT;
			generate(gxc,gyc,gfx,LOOPS/(loop_factor));
			glutPostRedisplay();
		}
	}
}
int main(int argc, char* argv[]) {

	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
	glutInitWindowSize(WIDTH,HEIGHT);
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
