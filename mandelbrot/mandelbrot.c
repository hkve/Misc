#include <stdio.h>
#include <stdlib.h>
#include <complex.h>
#include <math.h>

#define printc(z) printf("%f%+fi\n", creal(z), cimag(z))
#define MAX_ITER 80

int convergence(double complex* c) {
	int iter = 0;
	double complex z = 0;
	while(cabs(z) < 2 && iter <= MAX_ITER) {
		z = z*z + *c;
		iter++;
	}

	return iter;
}

int main(int argc, char* argv[]) {
	double x0 = atoi(argv[1]);
	double x1 = atof(argv[2]);
	int Nx = atoi(argv[3]);

	double y0 = atof(argv[4]);
	double y1 = atof(argv[5]);
	int Ny = atoi(argv[6]);
	char* filename = argv[7];

	double complex dx = (x1-x0)/(Nx-1);
	double complex dy = (y1-y0)/(Ny-1);

	double complex z;
	int iter;
	
	FILE *fp;
	fp = fopen(filename,"w+");
	fprintf(fp, "%f %f %i %f %f %i\n", x0, x1, Nx, y0, y1, Ny);
	for(int i = 0; i < Ny; i++) {
		z = x0 + (y0+i*dy)*I; 
		for(int j = 0; j < Nx; j++) {
			iter = convergence(&z);
			fprintf(fp, "%d\n", iter);	
			z += dx;
		}
	}

	fclose(fp);
}
