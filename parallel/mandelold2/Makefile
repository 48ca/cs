(all):
	mpicc -lGL -lGLU -lglut -lpng -lgmp -lm -O2 mandelbrot.c -o mandelexec
run:
	make
	mpirun -np 16 -hostfile hosts.txt mandelexec --load
gmp:
	make
	mpirun -np 16 -hostfile hosts.txt mandelexec --load --gmp
copy:
	make
	mpirun -np 16 -hostfile hosts.txt mandelexec --no-gl -h max -w max --load
	# cp frac.png ~/web-docs/
	# display frac.png
