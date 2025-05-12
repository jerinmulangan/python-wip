#include <stdio.h>
#include <stdlib.h>
int main() {
int SMALLER = 0;
int BIGGER = 0;
int TEMP = 0;
if (scanf("%d", &BIGGER) != 1) { fprintf(stderr, "type mismatch error: non-integer input for BIGGER.\n"); exit(1); }
if (scanf("%d", &SMALLER) != 1) { fprintf(stderr, "type mismatch error: non-integer input for SMALLER.\n"); exit(1); }
if (SMALLER > BIGGER) {
TEMP = SMALLER;
SMALLER = BIGGER;
BIGGER = TEMP;
}
while (SMALLER > 0) {
BIGGER = BIGGER - SMALLER;
if (SMALLER > BIGGER) {
TEMP = SMALLER;
SMALLER = BIGGER;
BIGGER = TEMP;
}
}
printf("%d\n", BIGGER);
return 0;
}
