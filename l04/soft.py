#!/bin/python

def var(i):
    return "x" + str(i)

def var_weighted(i):
    return weighted(1, var(i))


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

packages = []

for line in inf:
    parts = line.strip().split(";")

    package = int(parts[0])

    depends_raw = parts[1].split("*") if parts[1] != '' else []
    depends = []
    for dr in depends_raw:
        depends.append(list(map(int,dr.split("+"))))

    conflicts = list(map(int, parts[2].split("*"))) if parts[2] != '' else []

    packages.append((package, depends, conflicts))

print("min:", clause([weighted(-1,var(x)) for x in range(len(packages))]))

for package, depends, conflicts in packages:
    for depend in depends:
        print(clause(list(map(var_weighted, depend)) + [weighted(-1,var(package))], "<=", 1))

    
    for conflict in conflicts:
        print(clause([var_weighted(package), var_weighted(conflict)], "<=", 1))
