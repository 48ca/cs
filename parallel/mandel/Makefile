(all):
	mpicc -Ofast mandelbrot.c -o mandelexec `pkg-config --cflags --libs gl glu ompi libpng` -lglut -lgmp -lm
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
