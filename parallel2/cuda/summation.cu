#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// called from host, run on device
__global__ void add_gpu(long *in1,long *out)
{
	long idx=threadIdx.x; // flat model
	// out[idx]=in1[idx]+in2[idx];
	out[idx] = in1[2*idx] + in1[2*idx+1];
}
int main()
{
	// pointers to host memory
	long *a,*c;

	// pointers to device memory
	long *a_d,*b_d,*c_d;
	int exp=15;
	long N = (long)pow(2,exp);
	printf("%ld\n",N);
	printf("%d\n",(int)log2((double)N));
	long i;

	// allocate arrays a, b and c on host
	a=(long*)malloc(N*sizeof(long));
	// b=(float*)malloc(N*sizeof(float));
	c=(long*)malloc(N*sizeof(long));

	// allocate arrays a_d, b_d and c_d on device
	cudaMalloc((void**)&a_d,sizeof(long)*N);
	// cudaMalloc((void**)&b_d,sizeof(float)*N);
	cudaMalloc((void**)&c_d,sizeof(long)*N);

	// initialize arrays a and b
	srand(time(NULL));
	for(i=0;i<N;i++){
		a[i]= rand() % 100;
		// b[i]=-(float) i/2.0f;
	}

	// copy input from host memory to device memory
	cudaMemcpy(a_d,a,sizeof(long)*N,cudaMemcpyHostToDevice);
	// cudaMemcpy(b_d,b,sizeof(float)*N,cudaMemcpyHostToDevice);

	// execution configuration: How the threads are arranged, FLAT and LINEAR.
	int k;
	/*
	for(i=0;i<N;i++)
		printf("a[%d]=%d\n",i,a[i]);
	printf("\n");
	*/
	for(k = exp-1;k>=0;k--) {
		N /= 2;
		// (long)pow(2,k)
		dim3 dimGrid(1),dimBlock(N);
		add_gpu<<<dimGrid,dimBlock>>>(a_d, c_d);
		// float* tmp = b_d;
		/*
		cudaMemcpy(c,c_d,sizeof(int)*N,cudaMemcpyDeviceToHost);
		for(i=0;i<(int)pow(2,k);i++)
			printf("c[%d]=%d\n",i,c[i]);
		printf("\n");
		*/
		if(k) {
			b_d = a_d;
			a_d = c_d;
			c_d = b_d;
		}
	}
	
	// copy result from device memory to host memory
	cudaMemcpy(c,c_d,sizeof(long)*N,cudaMemcpyDeviceToHost);

	printf("%ld\n",c[0]);
	
	free(a);
	// free(b);
	free(c);
	cudaFree(a_d);
	// cudaFree(b_d);
	cudaFree(c_d);
}
