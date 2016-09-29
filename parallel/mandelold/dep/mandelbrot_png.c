#include <stdio.h>
#include <stdlib.h>
#include <GL/glut.h>
#include <math.h>
#include <png.h>

#define LOOPS 50
// initial loop orig 50
#define SQ_ESC_RADIUS 4
#define ESCAPE 2

#define PALETTE_SIZE 5
#define MAX_SIZE 5000
// BEGIN PNG

typedef struct {
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} pixel_t;
    
typedef struct  {
    pixel_t *pixels;
    size_t width;
    size_t height;
} bitmap_t;

static pixel_t * pixel_at (bitmap_t * bitmap, int x, int y) {
    return bitmap->pixels + bitmap->width * y + x;
}

static int save_png_to_file (bitmap_t *bitmap, const char *path)
{
    FILE * fp;
    png_structp png_ptr = NULL;
    png_infop info_ptr = NULL;
    size_t x, y;
    png_byte ** row_pointers = NULL;
    /* "status" contains the return value of this function. At first
       it is set to a value which means 'failure'. When the routine
       has finished its work, it is set to a value which means
       'success'. */
    int status = -1;
    /* The following number is set by trial and error only. I cannot
       see where it it is documented in the libpng manual.
    */
    int pixel_size = 3;
    int depth = 8;
    
    fp = fopen (path, "wb");
    if (! fp) {
        goto fopen_failed;
    }

    png_ptr = png_create_write_struct (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    if (png_ptr == NULL) {
        goto png_create_write_struct_failed;
    }
    
    info_ptr = png_create_info_struct (png_ptr);
    if (info_ptr == NULL) {
        goto png_create_info_struct_failed;
    }
    
    /* Set up error handling. */

    if (setjmp (png_jmpbuf (png_ptr))) {
        goto png_failure;
    }
    
    /* Set image attributes. */

    png_set_IHDR (png_ptr,
                  info_ptr,
                  bitmap->width,
                  bitmap->height,
                  depth,
                  PNG_COLOR_TYPE_RGB,
                  PNG_INTERLACE_NONE,
                  PNG_COMPRESSION_TYPE_DEFAULT,
                  PNG_FILTER_TYPE_DEFAULT);
    
    /* Initialize rows of PNG. */

    row_pointers = png_malloc (png_ptr, bitmap->height * sizeof (png_byte *));
    for (y = 0; y < bitmap->height; ++y) {
        png_byte *row = 
            png_malloc (png_ptr, sizeof (uint8_t) * bitmap->width * pixel_size);
        row_pointers[y] = row;
        for (x = 0; x < bitmap->width; ++x) {
            pixel_t * pixel = pixel_at (bitmap, x, y);
            *row++ = pixel->red;
            *row++ = pixel->green;
            *row++ = pixel->blue;
        }
    }
    
    /* Write the image data to "fp". */

    png_init_io (png_ptr, fp);
    png_set_rows (png_ptr, info_ptr, row_pointers);
    png_write_png (png_ptr, info_ptr, PNG_TRANSFORM_IDENTITY, NULL);

    /* The routine has successfully written the file, so we set
       "status" to a value which indicates success. */

    status = 0;
    
    for (y = 0; y < bitmap->height; y++) {
        png_free (png_ptr, row_pointers[y]);
    }
    png_free (png_ptr, row_pointers);
    
	png_failure:
	png_create_info_struct_failed:
		png_destroy_write_struct (&png_ptr, &info_ptr);
	png_create_write_struct_failed:
		fclose (fp);
	fopen_failed:
		return status;
}

// END PNG

static double colors[MAX_SIZE][MAX_SIZE]; // 10000x10000 max height and width
static double display_colors[MAX_SIZE][MAX_SIZE][3];

double zoom_factor = 1.0;
double zoom_change = 2.0;
double loop_factor = 1.05; // 1/.95
double loop_change = 1.04; // 1.02
double gxc = 0.0;
double gyc = 0.0;

static int width = 1200;
static int height = 900;
static double aspect = .75;

double last_gen_xcenter;
double last_gen_ycenter;
double last_gen_xwidth;
double last_gen_max_loop;

double palette[PALETTE_SIZE][3] = {
		{0,7.0/255,100.0/255},
		{32.0/255,107.0/255,203.0/255},
		{237.0/255,1.0,1.0},
		{1.0,170.0/255,0.0},
		{0.0,2.0/255,0.0}
};

int resized = 0;

void generate(double xcenter, double ycenter, double xwidth, int int_max_loop) {
	printf("Regenerating\n");
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
				color = (max_loop - loop + 1 - log(log(sqrt(a*a + b*b)))/log(ESCAPE))/max_loop;
			}
			// colors_w[x][y] = int_max_loop - loop;
			colors[x][y] = color;
		}
	}
	printf("Generated with zoom factor %f\n",zoom_factor);
}

void reset() {
	printf("Reseting\n");
	zoom_factor = 1.0;
	loop_factor = 1.02;
	generate(0,0,4,LOOPS);
	gxc = 0.0;
	gyc = 0.0;
	glutPostRedisplay();
}

void save() {
	printf("Saving\n");
	bitmap_t fractal;
	int x;
	int y;
	fractal.height = height;
	fractal.width = width;
	
	fractal.pixels = calloc(sizeof(pixel_t),fractal.width*fractal.height);

	for(y=0;y<fractal.height;y++) {
		for(x=0;x<fractal.width;x++) {
			pixel_t *pixel = pixel_at(&fractal,x,fractal.height-y-1);
			pixel-> red = (int)(255 * display_colors[x][y][0]);
			pixel-> green = (int)(255 * display_colors[x][y][1]);
			pixel-> blue = (int)(255 * display_colors[x][y][2]);
		}
	}
	printf("Saved\n");
	save_png_to_file(&fractal,"frac.png");
	return;
}

void keyfunc(unsigned char key,int xscr,int yscr)
{
	if( key == 'q' ) {
		exit( 0 ) ;
	}
	else if (key == 'r') {
		reset();
	}
	else if (key == 's') {
		save();
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
			color = colors[x][y]*PALETTE_SIZE;
			double left;
			double right;
			right = color - (int)color;
			left = 1 - right;
			// printf("%d %d %d\n",color,x,y);

			// COLORS
			
			if(color == 0.0) {
				glColor3f(0.0,0.0,0.0); // black
				// glColor3f(1.0,1.0,1.0); // white
				display_colors[x][y][0] = 0.0;
				display_colors[x][y][1] = 0.0;
				display_colors[x][y][2] = 0.0;
			} else {
				/*
				double red = color / 1.5;
				double blue = color;
				double green = 0.0;
				*/
				
				/*
				double red = palette[colors_w[x][y]%5][0];
				double green = palette[colors_w[x][y]%5][1];
				double blue = palette[colors_w[x][y]%5][2];
				*/

				/* UNSMOOTHED

				double red = palette[(int)(color)%PALETTE_SIZE][0];
				double green = palette[(int)(color)%PALETTE_SIZE][1];
				double blue = palette[(int)(color)%PALETTE_SIZE][2];

				*/

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
				// glColor3f(1.0, 0.0, 0.0);
			}
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
			// printf("%d %d\n",xscr,yscr);
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
