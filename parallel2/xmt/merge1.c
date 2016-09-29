#include <stdio.h>
#include <omp.h>
#include <math.h>

int bs(int* a, int s, int len, int offset) { // offset should be 0 to start
	if(!len) return offset;
	if(s > a[offset+len-1]) return offset+len;
	if(s < a[offset+len/2])	return bs(a,s,len/2,offset);
	return bs(a,s,len/2,offset+len/2);
}

void printarr(int* arr, int len) {
	printf("%2d",*arr);
	if(len>1) {
		register int k;
		for(k=1;k<len;k++) {
			printf(", %2d",arr[k]);
		}
	}
	printf("\n");
}

int main(int argc, char* argv[])
{
	#define N 32
	#define HN 16
	#define LN 5
	#define HNM 15

	int k;
	int big[N] = {1,2,4,5,8,10,13,14,16,18,19,22,25,27,29,30,/**/3,6,7,9,11,12,15,17,20,21,23,24,26,28,31,32};
	int* A = big;
	int* B = &(big[HN]);
	int C[N];
	register int i;
	for(i=0;i<N;i++)C[i]=-1;

	int ln = LN;
	int x = N/LN;

	printf("Source array 1:  ");
	printarr(A,HN);
	printf("Source array 2:  ");
	printarr(B,HN);

	int ind;
	int inds[x];

	#pragma omp parallel for private(ind)
	for(k=0;k<N;k+=x) {
		ind = k > HNM ? bs(A,big[k],HN,0) + k-HN : bs(B,big[k],HN,0) + k;
		C[ind] = big[k];
		inds[k/x] = ind;
	}
	printf("Result (seg'd):  ");
	printarr(C,N);

	int a;
	int b;
	#pragma omp parallel for private(a,b)
	for(k=0;k<x;k++) {
		int ind = inds[k];
		a = bs(A,C[ind],HN,0);
		b = bs(B,C[ind],HN,0);
		if(A[a] == C[ind]) a++;
		if(B[b] == C[ind]) b++;
		ind++;

		while(C[ind] < 0) {
			if(a > HNM && b < HN) C[ind++] = B[b++];
			else if(b > HNM && a < HN) C[ind++] = A[a++];
			else C[ind++] = A[a] < B[b] ? A[a++] : B[b++];
		}
	}
	printf("Final result:    ");
	printarr(C,N);
}
