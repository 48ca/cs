#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static char** grids;

void notInSquare(char* grid, char* pos, char* pull) {
	unsigned int diff = (unsigned int)(pos-grid);
	int x;
	int y;
	char* loc;
	diff = diff - diff%3;
	diff = 27*(diff/27) + diff%9;
	for(y=diff;y<diff+27;y+=9) {
		for(x=0;x<3;x++) {
			if(loc = strchr(pull,grid[x+y])) {
				memmove(loc,loc+1,strlen(loc));
			}
		}
	}
	return;
}

void notInRow(char* grid, char* pos, char* pull) {
	unsigned int diff = (unsigned int)(pos-grid);
	int x;
	int y = diff/9;
	char* loc;
	for(x=0;x<9;x++) {
		if(loc = strchr(pull,grid[x+y*9])) {
			memmove(loc,loc+1,strlen(loc));
		}
	}
	return;
}

void notInCol(char* grid, char* pos, char* pull) {
	unsigned int diff = (unsigned int)(pos-grid);
	int x = diff%9;
	int y;
	char* loc;
	for(y=0;y<9;y++) {
		if(loc = strchr(pull,grid[x+y*9])) {
			memmove(loc,loc+1,strlen(loc));
		}
	}
	return;
}

char* validNext(char* grid, char* pos) {
	char* rt = (char*)malloc(10 * sizeof(char));
	register int i;
	for(i=0;i<9;i++) {
		rt[i]=i+49;
	}
	rt[i]='\0';
	notInCol(grid,pos,rt);
	notInRow(grid,pos,rt);
	notInSquare(grid,pos,rt);
	return rt;
}

char* solveBoard(char* grid) {
	char* n;
	char* bf;
	char* pos;
	int ml;
	int i;
	char old;


	pos = strchr(grid,'.');
	if(!pos) return grid;

	n = validNext(grid,pos);
	ml = strlen(n);
	old = *pos;

	for(i=0;i<ml;i++) {
		*(pos) = n[i];
		bf = solveBoard(grid);
		if(strcmp(bf,"")) return bf;
		*(pos) = old;
	}
	free(n);
	return "";

}

int main(int argc, char* argv[]) {

	char* tgs = (char*)malloc(128 * 82 * sizeof(char));
	char** grids = (char**)malloc(128 * 81 * sizeof(char));
	FILE* gf = fopen("sudoku128.txt","r");
	fread(tgs,10000000,sizeof(char),gf);

	int index = 0;

	// Read in boards

	char* token;
	char* delim = "\n";
	token = strtok(tgs,delim);

	while(token) {
		grids[index++] = token;
		token = strtok(NULL,delim);
	}

	// Find solved boards

	struct timeval to;
	struct timeval tn;

	if(argc > 1) {
		int board = atoi(argv[1])-1;
		gettimeofday(&to,NULL);
		printf("%s\n",grids[board]);
		printf("%s\n",solveBoard(grids[board]));
		gettimeofday(&tn,NULL);
		printf("Time: %d usec\n",(int)((tn.tv_sec - to.tv_sec)*1000000 + tn.tv_usec - to.tv_usec));

	} else {
		int i;
		for(i=0;i<128;i++) {
			gettimeofday(&to,NULL);
			printf("%03d %s ",i,grids[i]);
			printf("%s ",solveBoard(grids[i]));
			gettimeofday(&tn,NULL);
			printf("%10.6f\n",((double)(tn.tv_sec - to.tv_sec) + (tn.tv_usec - to.tv_usec)/1000000.0));
		}
	}
	return 0;
}
