#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/time.h>
#include <time.h>

#define X 640
#define Y 480

#define YMIN 0
#define YMAX 1
// #define XMAX 1.166
// #define XMIN -0.166
#define XMAX 1.166
#define XMIN -0.166

#define EPSILON 0.00000000001
#define AMBIENT .2
#define REFLECT .4

#define BGR 150
#define BGG 150
#define BGB 255

#define CBR1 255
#define CBB1 0
#define CBG1 150
#define CBR2 150
#define CBB2 255
#define CBG2 0

#define REF_DEPTH_LIMIT 100

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

int num_shapes;
int offset;

double quad[3];

sphere** s;

double xsize = XMAX - XMIN;
double ysize = YMAX - YMIN;

// triple e = { 0.50 , 0.50 , .10 } ; // the eye
triple e = { 0.50 , 0.50 , -1.00 } ; // the eye
double zcam;
triple l = { 0.00 , 1.25 , -.50 } ; // the light
double lmag;
triple lunit;

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

void normalize(triple trip) {
	double magn = mag(trip);
	trip.x /= magn;
	trip.y /= magn;
	trip.z /= magn;
}

triple normal(triple pos, double cx, double cy, double cz, double r) {
	triple ret = {(pos.x-cx)/r,(pos.y-cy)/r,(pos.z-cz)/r};
	// triple ret = {(cx-pos.x)/r,(cy-pos.y)/r,(cz-pos.z)/r};
	/*
	double magn = mag(ret);
	ret.x /= magn;
	ret.y /= magn;
	ret.z /= magn;
	*/
	return ret;
}

triple getUV(triple dir, triple t) {
	triple subt = {dir.x-t.x,dir.y-t.y,dir.z-t.z};
	double magn = mag(subt);
	subt.x /= magn;
	subt.y /= magn;
	subt.z /= magn;
	// normalize(subt);
	return subt;
}

triple add(triple pos1, triple pos2) {
	triple ret = {pos1.x + pos2.x, pos1.y + pos2.y, pos1.z + pos2.z};
	return ret;
}

triple addscaled(triple pos1, triple pos2, double scalar) {
	triple ret = {pos1.x + pos2.x*scalar, pos1.y + pos2.y*scalar, pos1.z + pos2.z*scalar};
	return ret;
}
triple sub(triple pos1, triple pos2) {
	triple ret = {pos1.x - pos2.x, pos1.y - pos2.y, pos1.z-pos2.z};
	return ret;
}

double dotp(triple one, triple two) {
	return one.x * two.x + one.y * two.y + one.z * two.z;
}

color getShadow(color* c, triple vec, int shape, double pmag, triple evec) {
	// triple posne = {vec.x*pmag,vec.y*pmag,vec.z*pmag};
	triple pos = {evec.x + vec.x*pmag, evec.y + vec.y*pmag, evec.z + vec.z*pmag};


	double ocx = s[shape]->x;
	double ocy = s[shape]->y;
	double ocz = s[shape]->z;
	// pos = addscaled(pos,norm,EPSILON);
	
	// Calculate vector to light
	// triple vtl = sub(pos,l);
	triple vtl = sub(l,pos);
	// printf("%f %f %f : %f %f %f\n",pos.x,pos.y,pos.z,vtl.x,vtl.y,vtl.z);
	double magn = mag(vtl);
	double rx = vtl.x/magn;
	double ry = vtl.y/magn;
	double rz = vtl.z/magn;

	triple vtln = {rx,ry,rz};

	register int i;
	double min_t = 1.0/0.0;
	int min_shape = -1; 
	for(i=0;i<num_shapes+offset;i++) {
		if(i == shape) continue;
		double cx = s[i]->x;
		double cy = s[i]->y;
		double cz = s[i]->z;

		quad[0] = 1.0; // rx*rx + ry*ry + rz*rz;
		// quad[1] = 2*(pos.x*rx + pos.y*ry + pos.z*rz - (rx*cx + ry*cy + rz*cz));
		// quad[2] = square(rx-cx) + square(ry-cy) + square(rz-cz) - square(shapes[i]->radius);
		// quad[1] = 2*(e.x*rx + e.y*ry + e.z*rz - (rx*cx + ry*cy + rz*cz));
		// quad[2] = square(e.x-cx) + square(e.y-cy) + square(e.z-cz) - square(shapes[i]->radius);
		quad[1] = 2*(pos.x*rx + pos.y*ry + pos.z*rz - (rx*cx + ry*cy + rz*cz));
		quad[2] = square(pos.x-cx) + square(pos.y-cy) + square(pos.z-cz) - square(s[i]->radius);
		// quad[1] = 2*(l.x*rx + l.y*ry + l.z*rz - (rx*cx + ry*cy + rz*cz));
		// quad[2] = square(l.x-cx) + square(l.y-cy) + square(l.z-cz) - square(shapes[i]->radius);
		if(calcDisc() < 0.0) continue;
		double t = calcT();
		if(t<EPSILON) continue;
		if(t < min_t) {
			min_t = t;
			min_shape = i;
		}
	}
	if(min_shape > -1) {
		int r = c->r*AMBIENT;
		int g = c->g*AMBIENT;
		int b = c->b*AMBIENT;
		return (color){r,g,b};
	}
	triple norm = normal(pos, ocx, ocy, ocz, s[shape]->radius);
	double dp = dotp(norm, vtln);
	// if(shape == 3) printf("%f %f %f : %f %f %f : %f\n",norm.x,norm.y,norm.z,pos.x,pos.y,pos.z,dp);
	if(dp < 0) dp = 0;
	// dp = .5;
	return (color){(int)((AMBIENT + (1- AMBIENT)*dp) * c->r),(int)((AMBIENT + (1-AMBIENT)*dp) * c->g),(int)((AMBIENT + (1-AMBIENT)*dp) * c->b)};
}

void getColor(color* loc, triple trip, triple dir, int depth) {
	loc->r = BGR*AMBIENT;
	loc->g = BGG*AMBIENT;
	loc->b = BGB*AMBIENT;

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

	double min_t = 1.0/0.0;
	int min_shape = -1;

	double rx = dir.x;
	double ry = dir.y;
	double rz = dir.z;

	for(i=0;i<num_shapes+offset;i++) {
		cx = s[i]->x;
		cy = s[i]->y;
		cz = s[i]->z;

		quad[0] = 1.0; // rx*rx + ry*ry + rz*rz;
		quad[1] = 2*(trip.x*rx + trip.y*ry + trip.z*rz - (rx*cx + ry*cy + rz*cz));
		quad[2] = square(trip.x-cx) + square(trip.y-cy) + square(trip.z-cz) - square(s[i]->radius);
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
	sphere* mins = s[min_shape];
	if(min_shape > -1) {
		int freec = 0;
		color* c;
		triple nv = {dir.x*min_t, dir.y*min_t, dir.z*min_t};
		triple rvp = {nv.x + trip.x, nv.y + trip.y, nv.z + trip.z};
		if(min_shape) c = mins->c;
		else {
			c = (color*)malloc(sizeof(color));
			freec = 1;
			int nx = rvp.x < 0 ? (int)(rvp.x*10) : (int)(rvp.x*10)+1;
			int nz = rvp.z < 0 ? (int)(rvp.z*10) : (int)(rvp.z*10)+1;
			int booly = nx + nz;
			if(booly % 2) {
				c->r = CBR1;
				c->b = CBB1;
				c->g = CBG1;
			} else {
				c->r = CBR2;
				c->b = CBB2;
				c->g = CBG2;
			}
		}
		color s;
		if(depth < REF_DEPTH_LIMIT) {
			color* r = (color*)malloc(sizeof(color));

			triple norm = normal(rvp, mins->x, mins->y, mins->z, mins->radius);
			double dp = dotp(dir,norm);
			triple n2 = (triple){2*dp*norm.x, 2*dp*norm.y, 2*dp*norm.z};
			triple nvd = sub(dir,n2); //rvp
			double nmag = mag(nvd);
			nvd = (triple){nvd.x/nmag,nvd.y/nmag,nvd.z/nmag};
			getColor(r,rvp,nvd,depth+1);
			s = getShadow(c,dir,min_shape,min_t,trip);
			s.r = s.r*(1-REFLECT) + r->r*(REFLECT);
			s.g = s.g*(1-REFLECT) + r->g*(REFLECT);
			s.b = s.b*(1-REFLECT) + r->b*(REFLECT);
			free(r);
		} else {
			s = getShadow(c,dir,min_shape,min_t,trip);
		}
		loc->r = s.r;
		loc->g = s.g;
		loc->b = s.b;
		if(freec) free(c);
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
	s[1]->x = 1.0;
	s[1]->y = 0.5;
	s[1]->z = 0.5;

	s[2]->c = (color*)malloc(sizeof(color)); // Green
	s[2]->c->r = 0;
	s[2]->c->g = 255;
	s[2]->c->b = 0;
	s[2]->radius = .25;
	s[2]->x = 0.65;
	s[2]->y = 0.50;
	s[2]->z = 2.00;

	s[3]->c = (color*)malloc(sizeof(color)); // Red
	s[3]->c->r = 255;
	s[3]->c->g = 0;
	s[3]->c->b = 0;
	s[3]->radius = .50;
	s[3]->x = 0.00;
	s[3]->y = 0.75;
	s[3]->z = 1.25;
}

double gettime() {
	struct timeval tv;
	gettimeofday(&tv,NULL);
	return tv.tv_sec + tv.tv_usec*1000000.0;
}

int saveppm(const char* filename) {
	// shapes = (sphere**)malloc(sizeof(sphere*) * num_shapes);
	// init(shapes);

	color* rgb[Y][X]; // red-green-blue for each pixel
	int y , x , iy;
	double xs;
	double ys;
	FILE* fout ;
	register int iter = 0;
	int total = Y*X;
	/*
	double it = gettime();
	double dt = 1/30.0; // 30 FPS
	double ct;
	*/
	for( y = 0 ; y < Y ; y++ ) {
		for( x = 0 ; x < X ; x++) {
			iy = Y-y-1;
			rgb[iy][x] = (color*)malloc(sizeof(color));
			xs = XMIN + (double)x/X*xsize;
			ys = YMIN + (double)y/Y*ysize;
			// printf("%d %d : %f %f\n",x,y,xs,ys);
			triple dir = {xs,ys,zcam};
			triple uv = getUV(dir,e);
			getColor(rgb[iy][x],e,uv,0);
			printf("Progress: %f%c                    \r",100.0*(++iter)/total,'%');
			fflush(stdout);
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
	printf("Progress: Done                    \n");
	fclose( fout ) ;
	return 0 ;
}

int main(int argc, char* argv[]) {
	lmag = mag(l);
	lunit = (triple){l.x/lmag,l.y/lmag,l.z/lmag};
	zcam = e.z + 1.0; //z location of the "image" layer
	num_shapes = 0;

	const char* filename = "SAVE.ppm";
	FILE* fin = NULL;
	register int j,k;
	offset = 4;

	// num_shapes = 6000;
	// fin=fopen("wire.txt","r");
	
	// num_shapes = 12350;
	// fin=fopen("tree.txt","r");

	s = (sphere**)malloc(sizeof(sphere*) * (num_shapes+offset));
	init(s);
	double x,y,z,r;
	int totalbytes = (num_shapes+offset) * (sizeof(sphere*) + sizeof(color) + sizeof(sphere)) + Y*X*sizeof(color);
	register int res;
	printf("Allocating and populating %d bytes (%f MB)... ",totalbytes,totalbytes/1024.0/1024.0);
	fflush(stdout);
	for(j=0;j<num_shapes;j++) {
		k = j + offset;
		res = fscanf(fin,"%lf %lf %lf %lf",&x,&y,&z,&r);
		if(!res) {
			fprintf(stderr,"Error reading coordinatesn\n");
		}
		s[k] = (sphere*)malloc(sizeof(sphere));
		s[k]->c=(color*)malloc(sizeof(color));
		s[k]->c->r = 255;
		s[k]->c->g = 0;
		s[k]->c->b = 255;
		s[k]->radius = r;
		s[k]->x=x;
		s[k]->y=y - .1;
		s[k]->z=z;
	}
	printf("Done\n");
	if(fin != NULL) fclose(fin);
	int st = time(NULL);
	printf("Rendering...\n");
	fflush(stdout);
	saveppm(filename);
	printf("Rendered in %d seconds\n",(int)(time(NULL)-st));

	char cmd[100];
	sprintf(cmd,"display %s",filename);
	res = system(cmd);
	if(res) {
		fprintf(stderr,"Error displaying image\n");
	}

	return 0;
}
