#include <stdio.h>
#include <stdlib.h>

void multi_add(int a, int b, int d, int c, int *e);

int main(int argc, char ** argv) {
   int result; 
   int args[4];
   for( int i = 0; i < 4; i++) {
      args[i] = atoi(argv[i+1]);
   }
   multi_add(args[0],args[1],args[2],args[3],&result);
   printf("Ran function with args: %d %d %d %d \n",args[0],args[1],args[2],args[3]);
   printf("The result was: %d \n",result);
   return 0;
}
