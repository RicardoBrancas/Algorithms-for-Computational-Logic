#!/bin/python

from math import *

n = 8

print("p cnf", n*n, int((n-1)*n*(2*n-1)/3 + (n-1)*n*n + n))

for i in range(0, n):
    for j in range(0, n):
        print(i*n+j+1, end=" ")
    print(0)

for i in range(0, n):
    for j in range(0, n):
        for k in range(j+1, n):
            print(-(i*n+j+1), -(i*n+k+1), 0)

for j in range(0, n):
    for i in range(0, n):
        for k in range(i+1, n):
            print(-(i*n+j+1), -(k*n+j+1), 0)

for i in range(0, n):
    for j in range(0, n):
        for k in range(0, min(n-i-1,n-j-1)):
            print(-(i*n+j+1), -((i+k+1)*n+j+k+2),0) 

for i in range(0, n):
    for j in range(0, n):
        for k in range(0, min(n-i-1,j)):
            print(-(i*n+j+1), -((i+k+1)*n+j-k),0) 
