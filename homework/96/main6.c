#include <stdio.h>
#include "CommonUtil.h"

char isDaffodil(ull x)
{
    ull t = 0;
    for(int i=1; i<=getDigits(x); i++)
        t += ipow(getNumberAt(x, i), getDigits(x));
    return t == x;
}

int main()
{
    int n;
    scanf("%d", &n);
    
    for(ull i=ipow(10, n-1); i!=ipow(10, n); i++)
        printf(isDaffodil(i) ? "%llu\n" : "", i);
    return 0;
} 
