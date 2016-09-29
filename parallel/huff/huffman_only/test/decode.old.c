#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

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
	
	char *files[] = {NULL,NULL,NULL,NULL};
	int stats = 0;
	int located = 0;
	register int j,k;
	int compress = 0;
	for(j=1;j<argc;j++) {
		if(*(argv[j])=='-') {
			for(k=1;k<strlen(argv[j]);k++) {
				switch(argv[j][k]) {
					case 'S':
						stats = 1;
						break;
					case 'c':
						compress = 1;
						break;
					case 's':
						files[1] = argv[++j];
						break;
					case 'm':
						files[2] = argv[++j];
						break;
					case 'u':
						files[0] = argv[++j];
						break;
					case 'o':
						files[3] = argv[++j];
						break;
					default:
						fprintf(stderr,"Unrecognized option -%c\n",argv[j][1]);
						break;
				}
			}
		}
	}
	if(files[0] == NULL && (files[1] == NULL || files[2] == NULL)) {
		fprintf(stderr,"Usage: decode [-u infile] [-s scheme_file] [-m message_file] [-o outfile] [-Sc]\n");
		return 1;
	}
	if(files[0] != NULL && (files[1] != NULL || files[2] != NULL)) {
		fprintf(stderr,"WARNING: Decoding ONLY input specified by -u\n");
		return 1;
	}
	char *keyfile = files[1];
	char *valfile = files[2];
	char* tree = malloc(sizeof(char) * 10000000) ;
	register int flush;
	for(flush = 0;flush<10000000;flush++) { tree[flush] = '\0'; } // Clear array
	char keyin[50000];
	char* valin = (char*)malloc(500000000*sizeof(char));
	FILE* fkeys;
	FILE* fvals;
	
	fkeys = fopen(keyfile,"r");
	fvals = fopen(valfile,"r");
	
	int key_size = fread(keyin, sizeof(char), 50000, fkeys);
	int val_size = fread(valin, sizeof(char), 500000000, fvals);
	
	valin[val_size] = '\0';

	char* keys;
	const char delim[3] = ".\n";
	keys = strstr(keyin,delim)+2;
	while(strlen(keys)>0) {
		register int i;
		int index=1;
		for(i=1;(char*)keys+i<strstr(keys,delim);i++) {
			index = keys[i]=='0' ? 2*index : 2*index+1;
		}
		tree[index] = keys[0];
		char* pch = strstr(keys,delim);
		keys = (char*)(strstr(keys,delim)+2);
	}
	char* message = (char*)malloc(sizeof(char) * 100000000);
	
	char* m = { '\0' };
	register int i=0;
	register int cml = 0; //current message location (cml)
	if(compress) {
		char* ma = (char*)malloc(sizeof(char) * 100000000);
		while(i<val_size-1) {
			register int j;
			unsigned short c = valin[i++];
		    for (j = 7; j >= 0; --j) {
				char tmp = ((c & (1 << j)) ? '1' : '0' );
				ma[cml++] = tmp;
			}
		}
		int over = valin[i];
		ma[cml] = '\0';
		if(over > 0) {
			for(i=0;i<8;i++)
				ma[cml-8+i] = ma[cml-8+over+i];
		}
		m = ma;
	} else {
		m = valin;
	}
	i=0;
	cml = 0;
	register int length = strlen(m);
	while(i<length) {
		register int index = 1;
		while(tree[index]=='\0') {
			index = m[i++]=='0' ? 2*index : 2*index+1;
		}
		// printf("%c",tree[index]);
		message[cml++] = tree[index];
	}
	// message[cml-1] = '\0';
	size_t enb = cml; //encoded (after compression) bits
	size_t mb = strlen(message)*8; //message bits
	int shan = calcShan(message); //shannon number

	if(files[3] == NULL) {
		fprintf(stdout, "%s",message);
	} else {
		fprintf(files[3], files[3], "%s",message);
	}


	// Time
	
	struct timeval finished;
	gettimeofday(&finished,NULL);
	long long elapsed = (finished.tv_sec-started.tv_sec)*1000000LL + finished.tv_usec-started.tv_usec;
	
	// Printing statistics

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
