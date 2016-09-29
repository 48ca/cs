#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sys/time.h>
#include <time.h>
#include <mpi.h>

// #define X 1920
// #define Y 1080
#define X 640
#define Y 480

# define INTENS 3.0

double xmax;
double xmin;
double ymax;
double ymin;
double ysize;
double xsize;

const int tag = 0;
const int kill_tag = 1;
const int iter_tag = 2;
int num_procs;
MPI_Status status;
int rank;
char pname[MPI_MAX_PROCESSOR_NAME];

int textwidth;
int textheight;
int* texture;
int* maxt;

#define EPSILON 0.00000000001
#define AMBIENT .1

#define BGR 150
#define BGG 150
#define BGB 255

#define CBR1 255
#define CBB1 0
#define CBG1 150
#define CBR2 150
#define CBB2 255
#define CBG2 0

#define REF_DEPTH_LIMIT 10

#define TEXT_ROT 0

#define MAX_MOVE 2
#define MAX_COUNT 1
#define SCALAR MAX_MOVE/MAX_COUNT

#define NUM_LIGHTS 4

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
	double ref;
} sphere;

int num_shapes;
int offset;

double quad[3];

sphere** s;

triple e = { 0.50 , 0.50 , -1.00 } ; // the eye
double txttheta = 0.0;

double zcam;
triple* lights;

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

void brighten(color* c, triple* cf) {
	c->r = (int)(cf->x * INTENS);
	c->g = (int)(cf->y * INTENS);
	c->b = (int)(cf->z * INTENS);
	if(c->r > 255) c->r = 255;
	if(c->g > 255) c->g = 255;
	if(c->b > 255) c->b = 255;
}

color getShadow(color* c, triple vec, int shape, double pmag, triple evec) {
	triple pos = {evec.x + vec.x*pmag, evec.y + vec.y*pmag, evec.z + vec.z*pmag};


	double ocx = s[shape]->x;
	double ocy = s[shape]->y;
	double ocz = s[shape]->z;
	color fc = {0,0,0};
	triple fcf = {0.0,0.0,0.0}; // more precise colors -- needed for lots of lights
	register int lc;
	for(lc = 0;lc<NUM_LIGHTS;lc++) {

		// Calculate vector to light
		triple l = lights[lc];
		triple vtl = sub(l,pos);
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
			quad[1] = 2*(pos.x*rx + pos.y*ry + pos.z*rz - (rx*cx + ry*cy + rz*cz));
			quad[2] = square(pos.x-cx) + square(pos.y-cy) + square(pos.z-cz) - square(s[i]->radius);
			if(calcDisc() < 0.0) continue;
			double t = calcT();
			if(t<EPSILON) continue;
			if(t < min_t) {
				min_t = t;
				min_shape = i;
			}
		}
		if(min_shape > -1) {
			double r = c->r*AMBIENT;
			double g = c->g*AMBIENT;
			double b = c->b*AMBIENT;
			fcf.x += r/NUM_LIGHTS;
			fcf.y += g/NUM_LIGHTS;
			fcf.z += b/NUM_LIGHTS;
			continue;
		}
		triple norm = normal(pos, ocx, ocy, ocz, s[shape]->radius);
		double dp = dotp(norm, vtln);
		if(dp < 0) dp = 0;
		fcf.x += (((AMBIENT + (1-AMBIENT)*dp) * c->r)/NUM_LIGHTS);
		fcf.y += (((AMBIENT + (1-AMBIENT)*dp) * c->g)/NUM_LIGHTS);
		fcf.z += (((AMBIENT + (1-AMBIENT)*dp) * c->b)/NUM_LIGHTS);
	}
	brighten(&fc,&fcf);
	// printf("%d %d %d : %f %f %f\n",fc.r, fc.g, fc.b, fcf.x, fcf.y, fcf.z);
	return fc;
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

		if(calcDisc() < 0.0) continue;

		t = calcT();
		if(t < 0) continue;
		if(t < min_t) {
			min_t = t;
			min_shape = i;
		}
	}
	if(min_shape > -1) {
		sphere* mins = s[min_shape];
		int freec = 0;
		color* c;
		triple nv = {dir.x*min_t, dir.y*min_t, dir.z*min_t};
		triple rvp = {nv.x + trip.x, nv.y + trip.y, nv.z + trip.z};
		if(min_shape > 0) c = mins->c;
		// if(min_shape > 1) c = mins->c;
		else {
			freec = 1;
			if(0) { // min_shape
				/*************
				 * TEXTURING
				double r = s[min_shape]->radius;
				c = (color*)malloc(sizeof(color));
				double dy = (rvp.y - s[min_shape]->y)/r;
				double dx = (rvp.x - s[min_shape]->x)/r;
				double dz = (rvp.z - s[min_shape]->z)/r;
				double xang = dz > TEXT_ROT ? acos(dx) : M_PI/2 - acos(dx);
				if(dx == 0.0) dx = EPSILON;
				double xr = textwidth / (M_PI);
				int yc = (int)((1 + dy) * textheight/2);
				int xc = (int)(xang * xr);
				if(xc >= textwidth) {
					printf("%f | %f %f %d\n",dy,xang,xr,xc);
					printf("%s %d: %p\n",pname,rank,maxt);
					xc = 0;
				}
				int* tc = texture + textwidth * 3 * (textheight - yc - 1) + 3*xc;
				c->r = *(tc);
				c->g = *(tc+1);
				c->b = *(tc+2);
				*/
			} else {
				c = (color*)malloc(sizeof(color));
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
			s.r = s.r*(1-mins->ref) + r->r*(mins->ref);
			s.g = s.g*(1-mins->ref) + r->g*(mins->ref);
			s.b = s.b*(1-mins->ref) + r->b*(mins->ref);
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

void init(sphere** s, double mod) {
	s[0]->c = (color*)malloc(sizeof(color)); // Floor
	s[0]->c->r = 205;
	s[0]->c->g = 133;
	s[0]->c->b = 63;
	s[0]->radius = 20000.25;
	s[0]->x = 0.5;
	s[0]->y = -20000.0;
	s[0]->z = 0.5;
	s[0]->ref = .5;

	s[1]->c = (color*)malloc(sizeof(color)); // Blue
	s[1]->c->r = 0;
	s[1]->c->g = 0;
	s[1]->c->b = 255;
	s[1]->radius = .25;
	s[1]->x = mod*SCALAR + 1;
	s[1]->y = 0.5;
	s[1]->z = 0.5;
	s[1]->ref = .3;

	s[2]->c = (color*)malloc(sizeof(color)); // Green
	s[2]->c->r = 0;
	s[2]->c->g = 255;
	s[2]->c->b = 0;
	s[2]->radius = .25;
	s[2]->x = 0.65;
	s[2]->y = 0.50;
	s[2]->z = 1.00; //2
	s[2]->ref = .5;

	s[3]->c = (color*)malloc(sizeof(color)); // Red
	s[3]->c->r = 255;
	s[3]->c->g = 0;
	s[3]->c->b = 0;
	s[3]->radius = .50;
	s[3]->x = 0.00;
	s[3]->y = 0.75;
	s[3]->z = 1.25;
	s[3]->ref = .4;
}

double gettime() {
	struct timeval tv;
	gettimeofday(&tv,NULL);
	return tv.tv_sec + tv.tv_usec*1000000.0;
}

int render(const char* filename, int modifier) {
	color** rgb = malloc(sizeof(color*)*X*Y);
	long total = Y;
	FILE* fout;
	int* res = (int*)malloc(sizeof(int)*(3*X+1));
	int node = 1;
	int sent = 0;
	int recv = 0;
	int y, x;
	for( y = 0 ; y < Y ; y++ ) {
		if(node >= num_procs) goto done;
		MPI_Send(&modifier, 1, MPI_INT, node, iter_tag, MPI_COMM_WORLD);
		MPI_Send(&y, 1, MPI_INT, node++, tag, MPI_COMM_WORLD);
		sent++;
	}
	done:;
	for(;y<Y;y++) {
		MPI_Recv(res, 3*X+1, MPI_INT, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status);
		node = status.MPI_SOURCE;
		MPI_Send(&y, 1, MPI_INT, node, tag, MPI_COMM_WORLD);
		sent++;
		printf("Progress: %f%c                    \r",100.0*(++recv)/total,'%');
		fflush(stdout);
		for(x=0;x<X;x++) {
			color* c = (color*)malloc(sizeof(color));
			c->r = res[3*x+1];
			c->g = res[3*x+2];
			c->b = res[3*x+3];
			rgb[res[0]*X+x] = c;
		}
	}
	while(recv<sent) {
		MPI_Recv(res, 3*X+1, MPI_INT, MPI_ANY_SOURCE, tag, MPI_COMM_WORLD, &status);
		printf("Progress: %f%c                    \r",100.0*(++recv)/total,'%');
		for(x=0;x<X;x++) {
			color* c = (color*)malloc(sizeof(color));
			c->r = res[3*x+1];
			c->g = res[3*x+2];
			c->b = res[3*x+3];
			rgb[res[0]*X+x] = c;
		}
	}

	int yi;
	printf("Progress: Writing                 \r");
	fflush(stdout);
	fout = fopen( filename , "w" ) ;
	fprintf( fout , "P3\n" ) ;
	fprintf( fout , "%d %d\n" , X , Y ) ;
	fprintf( fout , "255\n" ) ;
	for( y = 0 ; y < Y ; y++ ) {
		for( x = 0 ; x < X ; x++) {
			yi = Y - y - 1;
			fprintf( fout , "%d %d %d\n" ,
			rgb[yi*X+x]->r , rgb[yi*X+x]->g, rgb[yi*X+x]->b ) ;
			free(rgb[yi*X+x]);
		}
	}
	printf("Progress: Closing                 \r");
	fflush(stdout);
	fclose( fout ) ;
	free(rgb);
	free(res);
	printf("Progress: Done                    \n");
	return 0 ;
}

int main(int argc, char* argv[]) {
	MPI_Init(&argc, &argv);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

	int name_len;
	MPI_Get_processor_name(pname, &name_len);

	register int res;
	register int count;
	num_shapes = 0;

	const char* filename = "SAVE.ppm";

	FILE* fin = NULL;
	register int j,k;
	offset = 4;

	// num_shapes = 6000;
	// fin=fopen("wire.txt","r");
	
	num_shapes = 12350;
	fin=fopen("tree.txt","r");
	/*
	FILE* tin = fopen("mercator82.ppm","r");
	char fc;
	int fd;
	res = fscanf(tin,"%c%d",&fc,&fd); // remove the ones we don't need
	res = fscanf(tin,"%d %d",&textwidth,&textheight);
	res = fscanf(tin,"%d",&fd); // remove the ones we don't need
	// printf("%d %d\n",textwidth,textheight);
	texture = (int*)malloc(sizeof(int) * textwidth * textheight * 3);
	maxt = texture + textwidth*textheight*3;
	register int tx;
	register int ty;
	int* pnt;
	for(ty=0;ty<textheight;ty++) {
		for(tx=0;tx<textwidth;tx++) {
			pnt = texture+ty*3*textwidth+tx*3;
			res = fscanf(tin,"%d %d %d",pnt,pnt+1,pnt+2);
			if(!res) {
				fprintf(stderr,"Error reading texture\n");
				return 1;
			}
		}
	}
	// printf("%d %d %d\n",*(pnt),*(pnt+1),*(pnt+2));
	fclose(tin);
	*/


	s = (sphere**)malloc(sizeof(sphere*) * (num_shapes+offset));
	s[0] = (sphere*)malloc(sizeof(sphere));
	s[1] = (sphere*)malloc(sizeof(sphere));
	s[2] = (sphere*)malloc(sizeof(sphere));
	s[3] = (sphere*)malloc(sizeof(sphere));

	double x,y,z,r;
	fflush(stdout);
	for(j=0;j<num_shapes;j++) {
		k = j + offset;
		res = fscanf(fin,"%lf %lf %lf %lf",&x,&y,&z,&r);
		if(!res) {
			fprintf(stderr,"Error reading coordinates on %s\n",pname);
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
		s[k]->ref = .95;
	}
	if(fin != NULL) fclose(fin);
	if(rank == 0) {
		printf("Rendering %d frames\nSaving temporary frames to %s\nSaving final output to directory 'output'\n",MAX_COUNT,filename);
		int res = system("mkdir output");
		if(!res)
			printf("Creating directory 'output'\n");
		for(count=0;count<MAX_COUNT;count++) {
			int st = time(NULL);
			printf("Rendering frame %d...\n",count);
			fflush(stdout);
			render(filename,count);
			printf("Rendered in %d seconds\n",(int)(time(NULL)-st));
			char cmd[100];
			sprintf(cmd,"convert %s output/frame%03d.png",filename,count);
			printf("Running `%s`\n",cmd);
			if( system(cmd) ) {
				fprintf(stderr,"!!! Error writing image!\n!!! Command: `%s`\n",cmd);
				return 1;
			}
		}
		printf("To convert to gif: convert -loop 0 -delay 5 output/* movies/movie00.gif\n");
	} else {
		int y , x;
		double xs;
		double ys;
		int send[3*X+1];
		int res;
		int count;
		// printf("%s responding as worker %d\n",pname,rank);

		lights = (triple*)malloc(sizeof(triple) * NUM_LIGHTS);
		lights[0] = (triple){-3,1.25,3};
		lights[1] = (triple){3,1.25,3};
		lights[2] = (triple){-3,1.25,-3};
		lights[3] = (triple){3,1.25,-3};
		color* c = (color*)malloc(sizeof(color));
		while(1) {
			MPI_Probe(0, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
			if(status.MPI_TAG == tag) {
				MPI_Recv(&res, 1, MPI_INT, 0, tag, MPI_COMM_WORLD, &status);
				// printf("%03d: RECEIVING\n",rank);
				y = res;
				send[0] = y;
				for(x=0;x<X;x++) {
					xs = xmin + (double)x/X*xsize;
					ys = ymin + (double)y/Y*ysize;
					triple dir = {xs,ys,zcam};
					triple uv = getUV(dir,e);
					getColor(c, e, uv, 0);
					send[3*x+1] = c->r;
					send[3*x+2] = c->g;
					send[3*x+3] = c->b;
				}
				// printf("%03d: SENDING (%d, %d) | %d %d %d\n",rank,send[1],send[0],send[2],send[3],send[4]);
				MPI_Send(send, 3*X+1, MPI_INT, 0, tag, MPI_COMM_WORLD);
			} else if(status.MPI_TAG == iter_tag) {
				MPI_Recv(&count, 1, MPI_INT, 0, iter_tag, MPI_COMM_WORLD, &status);

				double dcount = (double)count;

				ymin = 0;
				ymax = 1;
				xmin = -.1666666666666666;
				xmax = xmin + ((double)X/Y)*(ymax-ymin);

				e.x = (xmin + xmax)/2;

				xsize = xmax - xmin;
				ysize = ymax - ymin;

				// lights[0] = (triple){-1,1.25,-.5};
				/*
				e.z = dcount*SCALAR - 4.0;
				zcam = e.z + .5;
				*/
				// e.z = -2.0;
				/*
				etheta = M_PI - count*SCALAR;
				zcam = e.z + cos(etheta);
				e.x = (xmin + xmax)/2 + sin(etheta);
				*/
				// zcam = e.z + count*SCALAR + .05;
				init(s,dcount);
				// if(rank == 1) { printf("BROADCAST (1): %f %f\n",e.z,zcam); }
			} else if(status.MPI_TAG == kill_tag) {
				for(j=0;j<num_shapes+offset;j++) {
					free(s[j]->c);
					free(s[j]);
				}
				break;
			}
			/*
			char cmd[100];
			sprintf(cmd,"display %s",filename);
			res = system(cmd);
			if(es) {
				fprintf(stderr,"Error displaying image\n");
			}
			*/
		}
		free(c);
	}
	free(s);
	if(rank == 0) {
		int node = 1;
		while(node < num_procs)
			MPI_Send(NULL, 0, MPI_INT, node++, kill_tag, MPI_COMM_WORLD);
	}
	MPI_Finalize();
	return 0;
}
