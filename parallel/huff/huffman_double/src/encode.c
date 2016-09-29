#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
	char symbol;
	int frequency;
	struct Node* left;
	struct Node* right;
} TreeNode;

int* twoSmallest(TreeNode* forest[],int size) {
	register int i;
	unsigned int smallest_f = -1;
	int smallest = -1;
	int smaller = -1;
	unsigned int smaller_f = -1;
	for(i=0;i<size;i++) {
		if(forest[i] == NULL) continue;
		if(forest[i]->frequency < smallest_f) {
			smaller_f = smallest_f;
			smaller = smallest;
			smallest = i;
			smallest_f = forest[i]->frequency;
		}
		else if(forest[i]->frequency < smaller_f) {
			smaller = i;
			smaller_f = forest[i]->frequency;
		}
	}
	static int two[2];
	two[0] = smallest;
	two[1] = smaller;
	return two;
}
int numNodes(TreeNode** forest,int size) {
	register int i;
	int num = 0;
	for(i=0;i<size;i++) {
		if(forest[i] != NULL) num++;
	}
	return num;
}
void genTree(TreeNode* forest[], int size) {
	while(numNodes(forest,size) > 1) {
		int* node = twoSmallest(forest,size);
		TreeNode* parent = (TreeNode*)malloc(sizeof(TreeNode*));
		int freq = forest[node[0]]->frequency + forest[node[1]]->frequency;
		parent->frequency = freq;
		parent->symbol='\0';
		parent->left = forest[node[0]];
		parent->right = forest[node[1]];
		forest[node[0]] = parent;
		forest[node[1]] = NULL;
		int i;
	}
	return;
}
void genCode(char** dest,TreeNode* tree,int location, int place, char path[], FILE* out,FILE* sout) {
	if(tree->symbol=='\0') {
		if(tree->left != NULL)
			path[location] = '0';
			genCode(dest,tree->left,location+1,place*2,path,out,sout);
		if(tree->right != NULL)
			path[location] = '1';
			genCode(dest,tree->right,location+1,place*2+1,path,out,sout);
	} else {
		path[location] = '\0';
		char* save = (char*)malloc(sizeof(path));
		strcpy(save,path);
		fprintf(out,"%c%s.\n",tree->symbol,path);
		fprintf(sout,"%c%s.\n",tree->symbol,path);
		dest[tree->symbol] = save;
	}
	return;
}
void genMessage(char* message, char* scheme[], char* dec) {
	register int i, offset = 0;
	size_t length = strlen(dec);
	for(i=0;i<length;i++) {
		// if(scheme[dec[i]] == NULL) continue;
		// strcat(message,scheme[dec[i]]);
		sprintf(message + offset,"%s",scheme[dec[i]]);
		offset += strlen(scheme[dec[i]]);
	}
	return;
}

int main(int argc, char* argv[]) {

	if(argc<2) { fprintf(stderr, "Usage: encode infile [-o outfile] [-s scheme_file] [-m message_file] [-c]\n"); return 1; }
	char* infile = "/dev/null";
	char* schemefile = "/dev/null";
	char* messagefile = "/dev/null";
	char* outfile = "/dev/null";

	register int i;
	int located = 0;
	int compress = 0;
	for(i=1;i<argc;i++) {
		if(argv[i][0] == '-')
		{
			if((i+1 >= argc || argv[i+1][0] == '-') && (argv[i][1] == 'o' || argv[i][1] == 's' || argv[i][1] == 'm')) {
					fprintf(stderr,"Expected token after -%c\n",argv[i][1]);
			} else {
				switch(argv[i][1]) {
					case 'o':
						outfile = argv[++i];
						break;
					case 's':
						schemefile = argv[++i];
						break;
					case 'm':
						messagefile = argv[++i];
						break;
					case 'c':
						compress = 1;
						break;
					default:
						fprintf(stderr,"Unrecognized flag -%c\n",argv[i][1]);
						break;
						
				}
			}
		} else {
			if(located) {
				fprintf(stderr,"Unrecognized argument '%s'\n",argv[i]);
			} else {
				infile = argv[i];
				located = 1;
			}
		}
	}

	FILE* fin = fopen(infile,"r");
	FILE* sout = fopen(schemefile,"w");
	FILE* mout = fopen(messagefile,"w");
	FILE* out = fopen(outfile,"w");

	char* message = (char*)malloc(sizeof(char) * 10000000);

	int num_bytes = fread(message, sizeof(char), 10000000, fin);
	message[num_bytes] = '\0';

	int forestSize = 256;
	TreeNode* forest[256] = { NULL };
	
	int length = strlen(message);
	for(i=0;i<length;i++) {
		char sym = message[i];
		if(forest[sym]=='\0') {
			TreeNode* tr = (TreeNode*)malloc(sizeof(TreeNode));
			forest[sym] = tr;
			tr -> frequency = 1;
			tr -> symbol = sym;
		}
		else {
			forest[sym] -> frequency++;
		}
	}
	fprintf(out,"%d.\n",numNodes(forest,forestSize));
	fprintf(sout,"%d.\n",numNodes(forest,forestSize));
	genTree(forest,forestSize);
	TreeNode* root = NULL;
	for(i=0;i<forestSize;i++) {
		if(forest[i] != NULL) {
			root = forest[i];
			break;
		}
	}
	if(root == NULL) return 0;
	char* scheme[256];
	char path[1000000] = { '\0' };
	genCode(scheme,root,0,1,path,out,sout);
	char* fullMessage = (char*)malloc(100000000 * sizeof(char));
	genMessage(fullMessage,scheme,message);
	if(compress) {
		register int length = strlen(fullMessage);
		for(i=0;i<length;i+=8) {
			char buff[9] = { '\0' };
			memcpy(buff,fullMessage+i,8);
			char ch = strtol(buff,(char**)NULL,2);
			fprintf(out,"%c",ch);
			fprintf(mout,"%c",ch);
		}
		char over = i-strlen(fullMessage); 
		fprintf(out,"%c",over);
		fprintf(mout,"%c",over);
	} else {
		fprintf(out,"%s",fullMessage);
		fprintf(mout,"%s",fullMessage);
	}
	return 0;
}
