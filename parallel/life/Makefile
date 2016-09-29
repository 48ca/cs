(all):
	mpicc -lGL -lGLU -lglut -lm lifeparallel.c -o lifegl -Ofast
gl:
	mpicc -lGL -lGLU -lglut -lm lifegl.c -o lifegl -Ofast
run:
	mpirun -np 4 lifegl
