#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define ANSI_COLOR_RED "\x1b[31m"
#define ANSI_COLOR_CYAN "\x1b[36m"
#define ANSI_COLOR_RESET "\x1b[0m"

int calcShan(char *message) {
	int freq[256];
	double prob[256];
	register int i;
	for(i=0;i<256;i++) { freq[i] = 0; }
	i = 0;
	int total = strlen(message);
	while(i<total) {
		freq[message[i++]] += 1;
	}
	for(i=0;i<256;i++) { prob[i] = freq[i] / (double)total; }
	double sum = 0;
	for(i=0;i<256;i++) {
		if(freq[i] > 0) 
			sum += freq[i] * (-1 * log2(prob[i]));
	}
	return (int)sum;
}
int main( int argc, char *argv[] ) {
	
	struct timeval started;
	gettimeofday(&started,NULL);
	
	char *files[] = {"decodeMe/scheme.txt","decodeMe/values.txt"};
	int stats = 0;
	int located = 0;
	register int j,k;
	int compress = 0;
	for(j=1;j<argc;j++) {
		if(*(argv[j])=='-') {
			for(k=1;k<strlen(argv[j]);k++) {
				switch(argv[j][k]) {
					case 's':
						stats = 1;
						break;
					case 'c':
						compress = 1;
						break;
				}
			}
		}
		else {
			if(located<2) { files[located++] = argv[j]; }
		}
	}
	if(located<2) {
		fprintf(stderr,ANSI_COLOR_RED "Usage: decode scheme_file message_file [-s]\n");
		fprintf(stderr,ANSI_COLOR_RESET "\n");
	}
	char *keyfile = files[0];
	char *valfile = files[1];
	char tree[10000] = { '\0' };
	register int flush;
	for(flush = 0;flush<10000;flush++) { tree[flush] = '\0'; } // Clear array
	char keyin[10000];
	char valin[10000];
	FILE* fkeys;
	FILE* fvals;
	
	fkeys = fopen(keyfile,"r");
	fvals = fopen(valfile,"r");
	
	int key_size = fread(keyin, sizeof(char), 10000, fkeys);
	int val_size = fread(valin, sizeof(char), 10000, fvals);
	
	valin[val_size] = '\0';

	char* keys;
	keys = strtok(keyin,"\n");
	keys = strtok(NULL, "\n"); //skip key count
	while(keys) {
		register int i;
		int index=1;
		for(i=1;i<strlen(keys);i++) {
			index = keys[i]=='0' ? 2*index : 2*index+1;
		}
		tree[index] = keys[0];
		keys = strtok(NULL, "\n");
	}
	char message[10000];
	char* m = { '\0' };
	register int i=0;
	register int cml = 0; //current message location (cml)
	if(compress) {
		char ma[10000] = { '\0' };
		while(i<strlen(valin)) {
			register int j;
			unsigned short c = valin[i++];
		    for (j = 7; j >= 0; --j) {
				char tmp = ((c & (1 << j)) ? '1' : '0' );
				ma[cml++] = tmp;
			}
		}
		ma[cml] = '\0';
		m = ma;
	} else {
		m = valin;
	}
	i=0;
	cml = 0;
	while(i<strlen(m)) {
		register int index = 1;
		while(tree[index]=='\0') {
			index = m[i++]=='0' ? 2*index : 2*index+1;
		}
		message[cml++] = tree[index];
	}
	message[cml-1] = '\0';
	size_t enb = strlen(m); //encoded (after compression) bits
	size_t mb = strlen(message)*8; //message bits
	int shan = calcShan(message); //shannon number


	// Time
	
	struct timeval finished;
	gettimeofday(&finished,NULL);
	long long elapsed = (finished.tv_sec-started.tv_sec)*1000000LL + finished.tv_usec-started.tv_usec;
	
	// Printing statistics

	printf("%s\n",message);
	if(stats) {
		printf(ANSI_COLOR_CYAN "\n\nCompression statistics:\n" ANSI_COLOR_RESET);
		printf("Encoded bits:        %d\n",(int)enb);
		printf("Message bits:        %d\n",(int)mb);
		printf("Shannon number:      %d\n",shan);
		printf("Compression ratio:   %f%c\n",100*(mb-enb)/(float)mb,'%');
		printf("Scheme efficiency:   %f%c\n",100*shan/(double)enb,'%');
		printf("Performed in:        %lld μs\n",elapsed);
	}
	return 0;
}
