// 
// Torbert, 27 October 2014
// 
// MPI Demo
//    mpicc mpiDemo.c
//    mpirun -np 4 a.out
// 
// Manager-Worker model for parallel processing.
// 
// time ... real ... user 
// 
// htop 
// 
#include <stdio.h>
// 
#include "mpi.h"
// 
int main( int argc , char* argv[] )
{
   //
   // MPI variables
   //
   int        rank   ;
   int        size   ;
   MPI_Status status ;
   int        tag    ;
   //
   // other variables
   //
   int        k , j  ;
   double     result ;
   //
   // boilerplate
   //
   MPI_Init(      &argc          , &argv ) ;
   MPI_Comm_size( MPI_COMM_WORLD , &size ) ; // same
   MPI_Comm_rank( MPI_COMM_WORLD , &rank ) ; // different
   //
   // manager has rank = 0
   //
   if( rank == 0 )
   {
      printf( "\n" ) ;
      //
      result = 3.141 ; // bogus
      //
      for( j = 1 ; j < size ; j++ )
      {
         MPI_Send( &result , 1 , MPI_DOUBLE , j , tag , MPI_COMM_WORLD ) ;
      }
      //
      for( k = 1 ; k < size ; k++ )
      {
         MPI_Recv( &result , 1 , MPI_DOUBLE , MPI_ANY_SOURCE , tag , MPI_COMM_WORLD , &status ) ;
         //
         j = status.MPI_SOURCE ;
         //
         printf( "%d %d %20.16f\n" , j , size , result ) ;
      }
      //
      printf( "\n" );
   }
   //
   // workers have rank > 0
   //
   else
   {
      MPI_Recv( &result , 1 , MPI_DOUBLE , 0 , tag , MPI_COMM_WORLD , &status ) ;
      //
      result *= 2.0 ;
      //
      MPI_Send( &result , 1 , MPI_DOUBLE , 0 , tag , MPI_COMM_WORLD ) ;
   }
   //
   // boilerplate
   //
   MPI_Finalize() ;
   //
   return 0;
}
// 
// end of file
// 
