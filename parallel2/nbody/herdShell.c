// 
// herd
// 
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <GL/glut.h>
// 
#define Z 800
#define N 100
#define DT 0.01 
#define R 0.010
// 
typedef struct
{
   double x ;
   double y ;
   //
   double v ;
   double t ;
   //
   double dv ;
   double dt ;
   //
} Node ; 
// 
Node arr[N] ; 
// 
int  nbr[N] ; 
// 
double myrand()
{
   return ( 1.0 * rand() ) / RAND_MAX ;
} 
// 
double mydist( double x1 , double y1 , double x2 , double y2 )
{
   double dx = x2 - x1 ;
   double dy = y2 - y1 ;
   //
   return sqrt( dx*dx + dy*dy ) ;
} 
// 
void idlefunc(void)
{
   int j , k , kmin ;
   //
   double d , dmin ;
   //
   for( j = 0 ; j < N ; j++ )
   {
      arr[j].x += ( arr[j].v * cos( arr[j].t ) * DT ) ;
      arr[j].y += ( arr[j].v * sin( arr[j].t ) * DT ) ;
      //
      // bounce
      //
      if( arr[j].y - R < 0.0 )
      {
         arr[j].y = R ;
         //
         arr[j].t *= -1.0        ;
         arr[j].t +=  2.0 * M_PI ;
      }
      else if( arr[j].y + R > 1.0 )
      {
         arr[j].y = 1.0 - R ;
         //
         arr[j].t *= -1.0        ;
         arr[j].t +=  2.0 * M_PI ;
      }
      //
      if( arr[j].x - R < 0.0 )
      {
         arr[j].x = R ;
         //
         arr[j].t *= -1.0        ;
         arr[j].t +=  1.0 * M_PI ;
      }
      else if( arr[j].x + R > 1.0 )
      {
         arr[j].x = 1.0 - R ;
         //
         arr[j].t *= -1.0        ;
         arr[j].t +=  1.0 * M_PI ;
      }
   }
   //
   //
   //
   for( j = 0 ; j < N ; j++ )
   {
      kmin = j ;
      //
      for( k = 0 ; k < N ; k++ )
      {
         if( k != j )
         {
            d = mydist( arr[j].x , arr[j].y , arr[k].x , arr[k].y ) ;
            //
            if( kmin == j || d < dmin )
            {
               kmin = k ;
               dmin = d ;
            }
         }
      }
      //
      nbr[j] = kmin ;
   }
   //
   //
   //
   for( j = 0 ; j < N ; j++ )
   {
      k = nbr[j] ;
      //
      if( k == j ) // no nbr
      {
         arr[j].dv = 0.0 ;
         arr[j].dt = 0.0 ;
      }
      else
      {
         arr[j].dv = 0.002 *myrand();
		 if(arr[j].v > arr[k].v) {
		 	arr[j].dv *= -1 ;
		 }
		 arr[j].dt = -0.05 *myrand();
		 if(arr[j].t > arr[k].t) {
			 if(!( (arr[j].t) - (arr[k].t) < M_PI)){
			 	arr[j].dt *= -1 ;
			 }
		 } else {
			 if((arr[k].t) - (arr[j].t) < M_PI) {
			 	arr[j].dt *= -1 ;
			 }
		 }
		 if(sqrt(pow(arr[j].x - arr[k].x*arr[k].x,2) + pow(arr[j].y - arr[k].y,2)) > 2*R) {
			;
		 }
         //
         // TO DO ... move more like nbr
         //
      }
   }
   //
   for( j = 0 ; j < N ; j++ )
   {
      arr[j].v += arr[j].dv ;
      if( arr[j].v > 0.15 ) arr[j].v = 0.15 ;
      if( arr[j].v < 0.05 ) arr[j].v = 0.05 ;
      //
      arr[j].t += arr[j].dt ;
      if( arr[j].t > 2.0 * M_PI ) arr[j].t -= ( 2.0 * M_PI ) ;
      if( arr[j].t < 0.0        ) arr[j].t += ( 2.0 * M_PI ) ;
   }
   //
   glutPostRedisplay() ;
}
//
void displayfunc(void)
{
   int j , k ;
   //
   double x  , y  ;
   //
   double x1 , y1 ;
   double x2 , y2 ;
   double x3 , y3 ;
   //
   double t  , dt = 0.01 ;
   //
   glClear(GL_COLOR_BUFFER_BIT);
   //
   //
   //
   glColor3f( 1.0 , 1.0 , 0.0 ) ; // nbr ... edge
   //
   glBegin( GL_LINES ) ;
   //
   for( j = 0 ; j < N ; j++ )
   {
      k = nbr[j] ;
      //
      glVertex2f( arr[j].x , arr[j].y ) ;
      glVertex2f( arr[k].x , arr[k].y ) ;
   }
   //
   glEnd() ;
   //
   //
   //
   for( j = 0 ; j < N ; j++ )
   {
      glColor3f( 1.0 , 1.0 , 1.0 ) ; // circle
      //
      t = 0.0 ;
      while( t < 2.0 * M_PI )
      {
         x1 = arr[j].x                     ;
         y1 = arr[j].y                     ;
         //
         x2 = arr[j].x + R * cos( t )      ;
         y2 = arr[j].y + R * sin( t )      ;
         //
         x3 = arr[j].x + R * cos( t + dt ) ;
         y3 = arr[j].y + R * sin( t + dt ) ;
         //
         glBegin( GL_TRIANGLES ) ;
         glVertex2f( x1 , y1 ) ;
         glVertex2f( x2 , y2 ) ;
         glVertex2f( x3 , y3 ) ;
         glEnd() ;
         //
         t += dt ;
      }
      //
      //
      //
      glColor3f( 1.0 , 0.0 , 0.0 ) ; // red arrow
      //
      x = arr[j].x ;
      y = arr[j].y ;
      t = arr[j].t ;
      //
	   x1 = x + R * cos( t + 0.5 * M_PI ) ;
	   y1 = y + R * sin( t + 0.5 * M_PI ) ;
	   //
	   x2 = x + R * cos( t              ) ;
	   y2 = y + R * sin( t              ) ;
	   //
	   x3 = x + R * cos( t - 0.5 * M_PI ) ;
	   y3 = y + R * sin( t - 0.5 * M_PI ) ;
	   //
      glBegin(GL_TRIANGLES);
      	glVertex2f( x1 , y1 );
      	glVertex2f( x2 , y2 );
      	glVertex2f( x3 , y3 );
      glEnd();
	   //
	   x1 = x + 0.4 * R * cos( t - 0.5 * M_PI )                             ;
	   y1 = y + 0.4 * R * sin( t - 0.5 * M_PI )                             ;
	   //
	   x2 = x + 0.4 * R * cos( t + 0.5 * M_PI ) + 0.8 * R * cos( t + M_PI ) ;
	   y2 = y + 0.4 * R * sin( t + 0.5 * M_PI ) + 0.8 * R * sin( t + M_PI ) ;
	   //
	   x3 = x + 0.4 * R * cos( t + 0.5 * M_PI )                             ;
	   y3 = y + 0.4 * R * sin( t + 0.5 * M_PI )                             ;
	   //
      glBegin(GL_TRIANGLES);
      	glVertex2f( x1 , y1 );
      	glVertex2f( x2 , y2 );
      	glVertex2f( x3 , y3 );
      glEnd();
	   //
	   x3 = x + 0.4 * R * cos( t - 0.5 * M_PI ) + 0.8 * R * cos( t + M_PI ) ;
	   y3 = y + 0.4 * R * sin( t - 0.5 * M_PI ) + 0.8 * R * sin( t + M_PI ) ;
	   //
      glBegin(GL_TRIANGLES);
      	glVertex2f( x1 , y1 );
      	glVertex2f( x2 , y2 );
      	glVertex2f( x3 , y3 );
      glEnd();
   }
   //
   //
   //
   glutSwapBuffers() ;
}
int main(int argc,char* argv[])
{  
   int j ;
   //
   glutInit(&argc,argv);
   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
   glutInitWindowSize(Z,Z);
   glutInitWindowPosition(100,50);
   glutCreateWindow("");
   glClearColor(0.0,0.0,0.0,0.0);
   glShadeModel(GL_SMOOTH);
   //
   glViewport(0,0,(GLsizei)Z,(GLsizei)Z); // reshape
   glMatrixMode(GL_PROJECTION);
   glLoadIdentity();
   gluOrtho2D(0.0,1.0,0.0,1.0);
   glMatrixMode(GL_MODELVIEW);
   //
   for( j = 0 ; j < N ; j++ )
   {
      nbr[j] = j ; // no nbr ... default motion
      //
      arr[j].x = myrand() ;
      arr[j].y = myrand() ;
      //
      arr[j].v = myrand() * 0.1 + 0.05 ;
      arr[j].t = myrand() * 2.0 * M_PI ;
   }
   //
   glutIdleFunc(idlefunc);
   glutDisplayFunc(displayfunc);
   //
   glutMainLoop();
   //
   return 0;
}
// 
// end of file
// 
