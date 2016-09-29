#include <stdio.h>

int main(void) {
	char arr[100000];
	register int i;
	for(i=0;i<100000;i++)
		if( arr[i] != 'a') printf("%d\n",i);
	return 0;
}
