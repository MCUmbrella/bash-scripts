#include<stdio.h>
#include "TriangleUtil.h"

int main(int argc, char** argv)
{
    double x1=0, y1=0, x2=0, y2=0, x3=0, y3=0;
    scanf("%lf%lf%lf%lf%lf%lf", &x1, &y1, &x2, &y2, &x3, &y3);
    triangle* t = parseTriangle(x1, y1, x2, y2, x3, y3);
    if(isValidTriangle(t))
    {
        double* sl = sideLength(t);    
        printf("%.2lf\n", sl[0] + sl[1] + sl[2]);
        printf("%.2lf\n", area(t));
    }
    else puts("Impossible");
    return 0;
}
