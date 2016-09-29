#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// called from host, run on device
__global__ void add_gpu(long *in1,long *out)
{
	long idx=threadIdx.x; // flat model
	out[idx] = in1[2*idx] + in1[2*idx+1];
}
int main()
{
	long *a,*c;
	long *a_d,*b_d,*c_d;
	int exp=15;
	long N = (long)pow(2,exp);
	printf("%ld\n",N);
	printf("%d\n",(int)log2((double)N));
	long i;
	a=(long*)malloc(N*sizeof(long));
	c=(long*)malloc(N*sizeof(long));
	cudaMalloc((void**)&a_d,sizeof(long)*N);
	cudaMalloc((void**)&c_d,sizeof(long)*N);
	srand(time(NULL));
	for(i=0;i<N;i++){
		a[i]= rand() % 100;
	}
	cudaMemcpy(a_d,a,sizeof(long)*N,cudaMemcpyHostToDevice);
	int k;
	for(k = exp-1;k>=0;k--) {
		N /= 2;
		dim3 dimGrid(1),dimBlock(N);
		add_gpu<<<dimGrid,dimBlock>>>(a_d, c_d);
		if(k) {
			b_d = a_d;
			a_d = c_d;
			c_d = b_d;
		}
	}
	cudaMemcpy(c,c_d,sizeof(long)*N,cudaMemcpyDeviceToHost);
	printf("%ld\n",c[0]);
	free(a);
	free(c);
	cudaFree(a_d);
	cudaFree(c_d);
}
