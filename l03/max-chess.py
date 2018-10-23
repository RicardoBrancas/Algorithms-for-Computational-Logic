#!/bin/python

import argparse

parser = argparse.ArgumentParser(description='Compute the CNF formula dor the chessboard problem.')
parser.add_argument('size', metavar='N', type=int, help='size of the board')

args = parser.parse_args()

n = args.size
top = n*n + 2

clauses = []


def h_clause(*terms):
    s = str(top) + " "
    for term in terms:
        s += str(term) + " "
    s += "0"
    clauses.append(s)

def s_clause(*terms):
    s = str(1) + " "
    for term in terms:
        s += str(term) + " "
    s += "0"
    clauses.append(s)


def varid(i, j):
    return i * n + j + 1


def neg(i):
    return -i


def inrange(i, j):
    return i >= 0 and i < n and j >= 0 and j < n


for i in range(n):
    for j in range(n):
        s_clause(varid(i, j))
        for delta in [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, 2], [1, -2], [2, 1], [2, -1]]:
            if inrange(i + delta[0], j + delta[1]):
                h_clause(neg(varid(i, j)), neg(varid(i + delta[0], j + delta[1])))

print("p wcnf ", n*n, len(clauses), top)

for clause in clauses:
    print(clause)
