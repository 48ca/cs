(all):
	mpicc ray_parallel.c -lm -Wall -Ofast -fsanitize=address -g
serial:
	gcc ray.c -lm -Wall -fsanitize=address -g # -Ofast 
run:
	mpirun -np 8 -hostfile hosts.txt ./a.out
four:
	mpirun -np 4 -hostfile hosts.txt ./a.out
test:
	mpicc raytrace_Zacharias_4_2017jhoughto.c -lm -Wall -Ofast # -fsanitize=address -g
