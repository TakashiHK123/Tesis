#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <fcntl.h>
#include <time.h>
#include <sys/stat.h>
#include <linux/types.h>
#include <wiringPi.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/mman.h>

#define SCLK  25
#define MISO  22
#define MOSI  23
#define DRDY  20
#define CS2  19

void pulsePin(){
	digitalWrite(SCLK, 1);
	digitalWrite(SCLK, 0);}

void enviar(int bit){
	digitalWrite(MOSI, bit);
	pulsePin();}
	
int recivir(){
	pulsePin();
	return digitalRead(MISO);}

void pruebaVel(){
	int rep=10000000;
	long comienzo=micros();
	for (int i=0;i<rep;i++){
		recivir();}
	long tiempo=micros()-comienzo;
	printf("\nfrec: MHz%f\n%f us por escritura\ntiempo: %f s\n",rep/((float)(tiempo)),tiempo/((float)(rep)),(float)tiempo/1000000);

	comienzo=micros();
	for (int i=0;i<rep;i++){
		enviar(0);}
	tiempo=micros()-comienzo;
	printf("\nfrec: MHz%f\n%f us por escritura\ntiempo: %f s\n",rep/((float)(tiempo)),tiempo/((float)(rep)),(float)tiempo/1000000);
	
	
	/*
	    frec: MHz0.321776
		3.107751 us por lectura
		tiempo: 31.077509 s

		frec: MHz0.240714
		4.154307 us por escritura
		tiempo: 41.543076 s

	 */
	
}
	
void defFrecuencia(){
	//SPS
	//long msg=0x5300E0 ;//11100000 = 15,000SPS
	//long msg=0x5300D0 ;//11010000 = 7,500SPS
	//long msg=0x5300A1 ;//10100001 = 1,000SPS
	//long msg=0x5300B0 ;//2k sps
	long msg=0x5300C0; //3.75k sps
	//long msg =0x530023; //00100011 = 10SPS
	for (int i=0;i<24;i++){
		enviar(msg & 0x800000);
		msg = msg << 1;}
	delayMicroseconds(10);
}

void lecturaContinua(){
	//RDATAC
	int msg = 0x03;
	for (int i=0;i<8;i++){
		enviar(msg & 0x80);
		msg = msg << 1;}
	delayMicroseconds(10);
}

void pararLecCon(){
	//SDATAC: Stop Read Data Continuous
	int msg = 0x0F;
	while(digitalRead(DRDY)){}
	for (int i=0;i<8;i++){
		enviar(msg & 0x80);
		msg = msg << 1;}
	delayMicroseconds(10);
}

void seleccionADC(){
	//seleccion de ADC
	//0x01   76 o 01
	long msg=0x510076 ;//7 positivo y 6 negativo
	//long msg=0x510001; //default 0 positivo y 1 negativo
	for (int i=0;i<24;i++){
		enviar(msg & 0x800000);
		msg = msg << 1;}
	delayMicroseconds(10);
}


double leerADC(){
	long aux,out=0,signo;
	for (int j=0;j<24;j++){
		aux = recivir() & 0x000001;
		aux = aux <<(23-j);
		out += aux;}
	signo=out & 0x800000;
	out= out  & 0x7FFFFF;
	if (signo!=0){
		out = -(((~out) & 0x7FFFFF )+1);}
	return (double)out/8388608.0*5.0;
}

int main(int argc, char *argv[])
{
	
	wiringPiSetup();
	
	pinMode(SCLK, OUTPUT);
	pinMode(MOSI, OUTPUT);
	pinMode(CS2, OUTPUT);

	pinMode(MISO, INPUT);
	pinMode(DRDY, INPUT);
	
	//digitalWrite(CS2, 1);
	//pruebaVel();
	digitalWrite(CS2, 0);
	pararLecCon();
	seleccionADC();
	defFrecuencia();
	lecturaContinua();
	
	int n=37500;
	double datos[n];
	long tiempo=millis();
	
	for (int i=0;i<n;i++){
		while(digitalRead(DRDY)){}
		datos[i]=leerADC();
		while(!digitalRead(DRDY)){}
	
	}
	
	tiempo=millis()-tiempo;
	pararLecCon();
	digitalWrite(CS2, 1);
	printf("\nfrec: %f Hz\ntiempo: %f s\n",n*1000/((float)(tiempo)),tiempo/1000.0);
	
	pinMode(SCLK, INPUT);
	pinMode(MOSI, INPUT);
	pinMode(CS2, INPUT);
	
	FILE *f = fopen("datosADCinterfaz.txt", "w");
	if (f == NULL)
	{
		printf("Error opening file!\n");
		exit(1);
	}
	fprintf(f, "%f\n", tiempo/1000.0);
	for (int i=0;i<n;i++){
		fprintf(f, "%f\n", datos[i]);
		}

	fclose(f);
	
	//system("python3 graficar.py");
	return 0;
}
