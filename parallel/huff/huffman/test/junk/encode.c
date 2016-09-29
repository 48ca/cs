#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
	char symbol;
	int frequency;
	struct Node* left;
	struct Node* right;
} TreeNode;

int findSize(TreeNode* nodes[], int length) {
	register int i;
	int num = 0;
	for(i=0;i<length;i++) {
		if(nodes[i]!=NULL) { num++; }
	}
	return num;
}
int removeSpaces(TreeNode* nodes[],int length) {
	int num = findSize(nodes,length), i;
	TreeNode* rt[num];
	int index = 0;
	for(i=0;i<length;i++) {
		if(nodes[i]!=NULL) { rt[index++] = nodes[i]; }
	}
	nodes = rt;
	return num;
}
TreeNode** sort(TreeNode* forest[], int actual, int size) {
	register int i, j;
	TreeNode* nodes[size];
	memcpy(nodes,forest,sizeof(nodes)); //don't overwrite passed array
	TreeNode** sorted = (TreeNode**)malloc(sizeof(TreeNode) * actual);
	for(j=0;j<actual;j++) {
		unsigned int min_freq = -1;
		unsigned int min_loc;
		char l;
		int sum = 0;
		for(i=0;i<size;i++) {
			if(nodes[i] != NULL) {
				sum++;
				int node_freq = nodes[i]->frequency;
				if(node_freq < min_freq) {
					min_freq = node_freq;
					min_loc = i;
					l = nodes[i]->symbol;
				}
			}
		}
		sorted[j] = nodes[min_loc];
		nodes[min_loc] = NULL;
	}
	return sorted;
}
TreeNode** twoSmallest(TreeNode* forest[],int size) {
	int smallest_f = forest[0]->frequency;
	TreeNode* smallest = forest[0];
	int smaller_f;
	TreeNode* smaller;
	if(size > 2) {
		smaller_f = forest[0]->frequency;
		smaller = forest[0];
	}
	register int i;
	for(i=2;i<size;i++) {
		if(forest[i]->frequency < smallest_f) {
			smaller_f = smallest_f;
			smaller = smallest;
			smallest = forest[i];
			smallest_f = forest[i]->frequency;
		}
		else if(forest[i]->frequency < smaller_f) {
			smaller = forest[i];
			smaller_f = forest[i]->frequency;
		}
	}
	TreeNode** two = (TreeNode**)malloc(sizeof(TreeNode*)*2);
	two[0] = smallest;
	two[1] = smaller;
	return two;
}
int compress(TreeNode* forest[],int size) {
	int i, index;
	for(i=0;i<size;i++) {
		if(forest[i] == NULL) {
			int j;
			for(j=i+1;j++;j<size) {
				if(forest[j] != NULL) {
					forest[i] = forest[j];
					index = i;
					break;
				}
			}
		} else {
			index = i;
		}
		printf("%d %d\n",index,i);
	}
	return index;
}
int numNodes(TreeNode** forest) {
	register int i;
	int size = sizeof(forest)/sizeof(TreeNode*);
	int num = 0;
	for(i=0;i<size;i++) {
		if(forest[i] != NULL) num++;
	}
	return num;
}
TreeNode* genTree(TreeNode* forest[], int loc, int size) {
	while(numNodes(forest) > 1) {
		TreeNode** node = twoSmallest(forest,size);
		TreeNode* parent = (TreeNode*)malloc(sizeof(TreeNode*));
		int freq = node[0]->frequency + node[1]->frequency;
		parent->frequency = freq;
		parent->symbol='\0';
		parent->left = node[0];
		parent->right = node[1];
		forest[size--] = parent;
		int i;
		for(i=0;i<2;i++)
			printf("%c %d\n",node[i]->symbol,node[i]->frequency);
		free(node);
	}
	return forest[size];
}
size_t genCode(char** dest,TreeNode* tree,int location, char path[]) {
	if(tree->symbol=='\0') {
		if(tree->left == NULL)
			path[location] = '0';
			genCode(dest,tree,location++,path);
		if(tree->right == NULL)
			path[location] = '1';
			genCode(dest,tree,location++,path);
	}
	else {
		register int i;
		int index;
		for(i=0;i<10000;i++) {
			if(dest[i] != NULL) { index = i; break; }
		}
		char finished[10000] = { '\0' };
		finished[0] = tree->symbol;
		for(i=1;i<10000 && path+i != NULL;i++) {
			finished[i] = path[i];
		}
		finished[i] = '\n';
		dest[index] = finished;
	}
	return sizeof(dest)/sizeof(TreeNode*);
}
void testTree(TreeNode* test) {
	if(test == NULL) return;
	printf("%c %d\n",test->symbol,test->frequency);
	testTree(test->left);
	testTree(test->right);
	return;
}
void genMessage(char* dest, char* codes[], size_t length) {
	register int i;
	for(i=0;i<length;i++) {
		if(codes[i] != NULL) {
			strcat(dest,codes[i]);
		}
	}
	return;
}

int main(int argc, char* argv[]) {

	if(argc<2) { fprintf(stderr, "Usage: encode infile [outfile]\n"); return 1; }
	char* infile = argv[1];
	char* outfile = argc > 2 ? argv[2] : "out.txt";

	FILE* fin = fopen(infile,"r");
	FILE* fout = fopen(outfile,"w");

	char message[10000] = { '\0' };

	int num_bytes = fread(message, sizeof(char), 10000, fin);
	message[num_bytes] = '\0';

	int forestSize = 512;
	TreeNode* forest[512] = { NULL };
	
	int length = strlen(message);
	register int i;
	for(i=0;i<length;i++) {
		char sym = message[i];
		if(sym=='\n') { sym = ' '; }
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
	for(i=0;i<sizeof(forest)/sizeof(TreeNode*);i++) {
	    if(forest[i] != NULL)
			printf("%c -> %d\n",forest[i]->symbol,forest[i]->frequency);
	}
	int loc;
	for(i=0;i<forestSize;i++) {
		if(forest[i] != NULL) {
			loc = i;
			break;
		}
	}
	TreeNode* parent = genTree(forest,loc,forestSize);
	for(i=0;i<forestSize;i++) {
		if(forest[i] != NULL) printf("FOREST: %c %d\n",forest[i]->symbol,forest[i]->frequency);
	}
	printf("STARTED\n");
	testTree(parent);
	printf("FINISHED\n");
	char* encoding[10000];
	size_t length_encoding = genCode(encoding,parent,0,'\0');
	char fullMessage[10000];
	genMessage(fullMessage,encoding,length_encoding);
	printf("%s\n",fullMessage);
	printf("vim help for link\n");
	return 0;
}
