(all):
	mpicc -lGL -lGLU -lglut -lpng -lgmp -lm -Ofast mandelbrot.c -o mandelexec
run:
	make
	mpirun -np 3 -hostfile hosts.txt mandelexec --load
gmp:
	make
	mpirun -np 3 -hostfile hosts.txt mandelexec --load --gmp
copy:
	make
	mpirun -np 8 -hostfile hosts.txt mandelexec --no-gl -h 10000 -w 10000 --load --force-no-gmp
	# cp frac.png ~/web-docs/
	# display frac.png
