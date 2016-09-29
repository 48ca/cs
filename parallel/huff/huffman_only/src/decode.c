#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

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
	
	char *files[] = {NULL,NULL};
	int stats = 0;
	int located = 0;
	register int i,j,k;
	int compress = 1;
	for(j=1;j<argc;j++) {
		if(*(argv[j])=='-') {
			if((j+1 >= argc || argv[j+1][0] == '-') && (argv[j][1] == 'o')) {
				fprintf(stderr,"Expected token after -%c\n",argv[j][1]);
			} else {
				switch(argv[j][1]) {
					case 's':
						stats = 1;
						break;
					case 'o':
						files[1] = argv[++j];
						break;
					default:
						fprintf(stderr,"Unrecognized option -%c\n",argv[j][1]);
						break;
				}
			}
		} else {
			if(located) {
				fprintf(stderr,"Unrecognized argument '%s'\n",argv[j]);
			} else {
				files[0] = argv[j];
				located = 1;
			}
		}
	}
	if(files[0] == NULL) {
		fprintf(stderr,"Usage: decode infile [-o outfile] [-s]\n");
		return 1;
	}
	char* infname = files[0];

	char keyin[50000];
	char* valin = (char*)malloc(500000000*sizeof(char));
	FILE* fkeys;
	FILE* fvals;
	FILE* infile;

	int key_size;
	int val_size;
	
	const char delim[3] = ".\n";

	char* tree = malloc(sizeof(char) * 10000000) ;
	register int flush;
	for(flush = 0;flush<10000000;flush++) { tree[flush] = '\0'; } // Clear array

	infile = fopen(infname,"r");
	
	val_size = fread(valin, sizeof(char), 500000000, infile);
	char* orig = valin;
	valin[val_size] = '\0';
	
	char* keys = strstr(valin,delim);
	*keys = '\0';
	*(keys + 1) = '\0';
	int number = atoi(valin);
	valin = keys+2;
	for(i=0;i<number;i++) {
		char* tmp = strstr(valin,delim);
		register int j;
		int index = 1;
		for(j=1;(char*)valin+j<tmp;j++) {
			index = valin[j]=='0' ? 2*index : 2*index + 1;
		}
		tree[index] = valin[0];
		valin = tmp + 2;
	}
	val_size -= (valin - orig);

	char* message = (char*)malloc(sizeof(char) * 100000000);
	
	char* m = { '\0' };
	i = 0;
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
	size_t enb = val_size; //encoded (after compression) bits
	if(compress) enb *= 8;
	size_t mb = strlen(message)*8; //message bits
	int shan = calcShan(message); //shannon number

	if(files[1] != NULL) {
		fprintf(fopen(files[1],"w"), "%s",message);
	}
	//else {
		// fprintf(stdout, "%s",message);
	//}

	// Time
	
	struct timeval finished;
	gettimeofday(&finished,NULL);
	long long elapsed = (finished.tv_sec-started.tv_sec)*1000000LL + finished.tv_usec-started.tv_usec;
	
	// Printing statistics

	if(stats) {
		printf("Encoded bits:        %d\n",(int)enb);
		printf("Message bits:        %d\n",(int)mb);
		printf("Shannon number:      %d\n",shan);
		printf("Compression ratio:   %f%c\n",100*(mb-enb)/(float)mb,'%');
		printf("Scheme efficiency:   %f%c\n",100*shan/(double)enb,'%');
		printf("Performed in:        %lld μs\n",elapsed);
	}
	return 0;
}
