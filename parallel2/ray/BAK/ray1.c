#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define X 640
#define Y 480

#define YMAX 1
#define YMIN 0
#define XMAX 1.166
#define XMIN -0.166

#define NUM_SHAPES 4

typedef struct {
	double x;
	double y;
	double z;
} triple;
typedef struct {
	int r;
	int g;
	int b;
} color;
typedef struct {
	color* c;
	double x;
	double y;
	double z;
	double radius;
} sphere;

double quad[3];

sphere** shapes;

double xsize = XMAX - XMIN;
double ysize = YMAX - YMIN;

triple e = { 0.50 , 0.50 , -1.0 } ; // the eye
double zcam = 0.0; //z location of the "image" layer
triple l = { 0.00 , 1.25 , -0.50 } ; // the light

double square(double d) { return d*d; }

double calcDisc() {
	return square(quad[1]) - 4*quad[0]*quad[2];
}

double calcT() {
	return (-1 * quad[1] - sqrt(square(quad[1]) - 4 * quad[0]*quad[2])) / (2 * quad[0]);
}

double mag(triple v) {
	return sqrt(square(v.x) + square(v.y) + square(v.z));
}

triple getUV(double x, double y) {
	triple sub = {x-e.x,y-e.y,zcam-e.z};
	double magnitude = mag(sub);
	sub.x /= magnitude;
	sub.y /= magnitude;
	sub.z /= magnitude;
	return sub;
}

void getColor(color* loc, double x, double y) {
	loc->r = 0;
	loc->g = 0;
	loc->b = 0;

	double cx;
	double cy;
	double cz;

	register int i;
	double t;

	/*

	double tx;
	double ty;
	double mag;

	tx = (x-X/2)*xscale;
	ty = (y-Y/2)*yscale;

	rx = tx / mag;
	ry = ty / mag;
	rz = Z / mag;

	*/

	triple uv;
	uv = getUV(x,y);

	double min_t = 1.0/0.0;
	int min_shape = -1;

	double rx = uv.x;
	double ry = uv.y;
	double rz = uv.z;

	for(i=0;i<NUM_SHAPES;i++) {
		cx = shapes[i]->x;
		cy = shapes[i]->y;
		cz = shapes[i]->z;

		quad[0] = 1.0; // rx*rx + ry*ry + rz*rz;
		quad[1] = 2*(e.x*rx + e.y*ry + e.z*rz - (rx*cx + ry*cy + rz*cz));
		quad[2] = square(e.x-cx) + square(e.y-cy) + square(e.z-cz) - square(shapes[i]->radius);
		// quad[1] = -2*cx*rx + 2*e.x*rx - 2*cy*ry + 2*e.y*ry - 2*cz*rz + 2*e.z*rz;
		// quad[2] = cx*cx + cy*cy + cz*cz - 2*cx*e.x + e.x*e.x - 2*cy*e.y + e.y*e.y -2*cz*e.z + square(e.z) - square(shapes[i]->radius);

		if(calcDisc() < 0.0) continue;

		t = calcT();
		if(t < 0) continue;
		// if(y > .48 && y < .49) printf("%f %f %f : %f %f : %d :::: %f\n",quad[0],quad[1],quad[2],x,y,i,t);
		if(t < min_t) {
			// if(y > .48 && y < .49) printf("!! %f %f %f : %f %f : %d :::: %f\n",quad[0],quad[1],quad[2],x,y,i,t);
			min_t = t;
			min_shape = i;
			// printf("\tShaped\n");
			// printf("\t%d %f %f %f %f %f\n",min_shape,x,y,quad[0],quad[1],quad[2]);
		}
	}
	if(min_shape > -1) {
		loc->r = shapes[min_shape]->c->r;
		loc->g = shapes[min_shape]->c->g;
		loc->b = shapes[min_shape]->c->b;
	}
}

void init(sphere** s) {

	s[0] = (sphere*)malloc(sizeof(sphere));
	s[1] = (sphere*)malloc(sizeof(sphere));
	s[2] = (sphere*)malloc(sizeof(sphere));
	s[3] = (sphere*)malloc(sizeof(sphere));

	s[0]->c = (color*)malloc(sizeof(color)); // Floor
	s[0]->c->r = 205;
	s[0]->c->g = 133;
	s[0]->c->b = 63;
	s[0]->radius = 20000.25;
	s[0]->x = 0.5;
	s[0]->y = -20000.0;
	s[0]->z = 0.5;

	s[1]->c = (color*)malloc(sizeof(color)); // Blue
	s[1]->c->r = 0;
	s[1]->c->g = 0;
	s[1]->c->b = 255;
	s[1]->radius = .25;
	s[1]->x = 0.5;
	s[1]->y = 0.5;
	s[1]->z = 0.5;

	s[2]->c = (color*)malloc(sizeof(color)); // Green
	s[2]->c->r = 0;
	s[2]->c->g = 255;
	s[2]->c->b = 0;
	s[2]->radius = .25;
	s[2]->x = 1.00;
	s[2]->y = 0.50;
	s[2]->z = .75;

	s[3]->c = (color*)malloc(sizeof(color)); // Red
	s[3]->c->r = 255;
	s[3]->c->g = 0;
	s[3]->c->b = 0;
	s[3]->radius = .50;
	s[3]->x = 0.00;
	s[3]->y = 0.75;
	s[3]->z = 1.25;
}

triple normal(triple pos, double cx, double cy, double cz, double r) {
	triple ret = {(pos.x-cx)/r,(pos.y-cy)/r,(pos.z-cz)/r};
	return ret;
}

int saveppm(const char* filename) {
	shapes = (sphere**)malloc(sizeof(sphere*) * NUM_SHAPES);
	init(shapes);

	color* rgb[Y][X]; // red-green-blue for each pixel
	int y , x , rx, ry, iy;
	double xs;
	double ys;
	FILE* fout ;
	for( y = 0 ; y < Y ; y++ ) {
		for( x = 0 ; x < X ; x++) {
			iy = Y-y-1;
			rgb[iy][x] = (color*)malloc(sizeof(color));
			xs = XMIN + (double)x/X*xsize;
			ys = YMIN + (double)y/Y*ysize;
			// printf("%d %d : %f %f\n",x,y,xs,ys);
			getColor(rgb[iy][x],xs,ys);
		}
	}

	fout = fopen( filename , "w" ) ;
	fprintf( fout , "P3\n" ) ;
	fprintf( fout , "%d %d\n" , X , Y ) ;
	fprintf( fout , "255\n" ) ;
	for( y = 0 ; y < Y ; y++ ) {
		for( x = 0 ; x < X ; x++) {
			fprintf( fout , "%d %d %d\n" ,
			rgb[y][x]->r , rgb[y][x]->g , rgb[y][x]->b ) ;
		}
	}
	close( fout ) ;
	return 0 ;
}

int main(int argc, char* argv[]) {
	saveppm("SAVE.ppm");
	return 0;
}
