#include <stdio.h>

int main(void) {
	FILE* fin;
	char c[10240];
	int n;
	fin = fopen("decodeME.txt","r");
	n = fread(&c, sizeof(char), 10000, fin);
	c[n] = '\0';
	printf("%s",c);
	printf("%d\n",n);

	return 0;
}
