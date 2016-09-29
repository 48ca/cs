#include <stdio.h>
#include <omp.h>

int main()
{
	int k , j , nt ;
	int A[8] = {3,1,4,1,5,9,2,6} ;
	int B[4][8] = { 0 } ;
	omp_set_num_threads( 8 ) ;
	#pragma omp parallel private(j)
	{
		j = omp_get_thread_num() ;
		B[3][j] = A[j] ;
		}
	nt = 4 ;
	for( k = 2 ; k >= 0 ; k-- ) {
		omp_set_num_threads( nt ) ;
		#pragma omp parallel private(j)
		{
		j = omp_get_thread_num() ;
		B[k][j] = B[k+1][2*j] + B[k+1][2*j+1] ;
		}
		nt /= 2 ;
	}
	for( k = 0 ; k <= 3 ; k++ ) {
	for( j = 0 ; j < 8 ; j++ ) {
		printf( "%2d " , B[k][j] ) ;
	}
	printf( "\n" ) ;
	}
}
