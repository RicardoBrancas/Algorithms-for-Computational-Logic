#!/bin/python

import fileinput
import argparse
from math import *

parser = argparse.ArgumentParser(description='Convert a graph to CNF')
parser.add_argument('ncolors', metavar='K', type=int,
                    help='number of colors')
parser.add_argument('input', help="Input file.")

args = parser.parse_args()
k = args.ncolors

nodes = None
edges = None

edgeList = []


def varid(v, c):
    return v * k + c + 1


for line in fileinput.input(args.input):
    if line[0] == 'c':
        continue
    
    split = line.split(" ")

    if split[0] == "h":
        
        nodes = int(split[1])
        edges = int(split[2])

    else:

        edgeList.append((int(split[0]), int(split[1])))

print("p cnf", nodes*k, int(nodes + nodes*(factorial(k)/(2*factorial(k-2))) + len(edgeList)*k))

for i in range(nodes):
    for color in range(k):
        print(varid(i, color), end=" ")
    print("0")

for i in range(0, nodes):
    for color1 in range(0, k):
        for color2 in range(color1+1, k):
            print(-varid(i, color1), -varid(i, color2), 0)


for edge in edgeList:
    for color in range(k):
        print(-varid(edge[0], color), -varid(edge[1], color), 0)
