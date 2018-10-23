#!/bin/python

def var(i):
    return "x" + str(i)


def weighted(weight, var):
    return "{:+}".format(weight) + " " + var

def clause(weighteds, _type=None, k=None):
    s = ""
    for weighted in weighteds:
        s += weighted + " "
    if _type != None:
        s += _type + " " + str(k)
    
    s += ";"

    return s


import argparse

parser = argparse.ArgumentParser(description='Creates a formulation for the vertex cover problem from a graph.')
parser.add_argument('input', metavar='INPUT', help='the input file')

args = parser.parse_args()

inf = open(args.input)


n = 0
e = 0

edges = []

for line in inf:
    if line.startswith('c'):
        continue

    if line.startswith('h'):
        parts = line.split(" ")
        n = int(parts[1])
        e = int(parts[2])
        continue
    
    parts = line.split(" ")

    v1 = int(parts[0])
    v2 = int(parts[1])

    edges.append((v1, v2))

min_f = [weighted(1,var(x)) for x in range(n)]
print("min:", clause(min_f))

for v1, v2 in edges:
    print(clause([weighted(1, var(v1)), weighted(1, var(v2))], '>=', 1))

present = {}
for i in range(n):
    present[i] = False


for v1, v2 in edges:
    present[v1] = True
    present[v2] = True

for key in present:
    if not present[key]:
        print(clause([weighted(1, var(key))], ">=", 1))

