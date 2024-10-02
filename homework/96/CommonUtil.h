#ifndef COMMON_UTIL_H
#define COMMON_UTIL_H
#define ull unsigned long long

double ffact(int x)
{
    double a=1;
    for(int b=1; b<x;) a*=++b;
    return a;
}

ull ifact(int x)
{
    ull a=1;
    for(int b=1; b<x;) a*=++b;
    return a;
}

double fpow(double x, int n)
{
    double y = 1;
    for(int i=0; i!=n; i++)
        y *= x;
    return y;
}

ull ipow(double x, int n)
{
    ull y = 1;
    for(int i=0; i!=n; i++)
        y *= x;
    return y;
}

double abs(double x)
{
    return x < 0 ? -x : x;
}

int getNumberAt(ull x, int n)
{
    return x % ipow(10, n) / ipow(10, n-1);
}

int getDigits(ull n)
{
    if(n < 0) n = -n;
    for(int i = 10; i != 0; i--)
        if(n >= ipow(10, i-1)) return i;
    return 1;
}

int gcd(int n, int m)
{
    int a = n >= m ? n : m;
    int b = n <= m ? n : m;
    int t = a % b;
    if(t==0) return b;
    return gcd(b, t);
}

int lcm(int n, int m)
{
    return n * m / gcd(n, m);
}

#endif
