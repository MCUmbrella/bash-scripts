#include <stdio.h>
#include "CommonUtil.h"

double f(int x)
{
    double s = 1;
    for(int i=1; ; i++)
    {
        double t = fpow(x, i) / ffact(i);
        if(abs(t) < 0.00001) return s;
        else s += t;
    }
}

int main()
{
    int x;
    scanf("%d", &x);
    
    printf("%.4lf\n", f(x));
    return 0;
} 
