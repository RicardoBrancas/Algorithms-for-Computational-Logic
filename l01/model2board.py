#!/usr/bin/python2
# File:  model2board.py
# Author:  mikolas
# Created on:  Tue, Sep 19, 2017 11:53:56
# Copyright (C) 2017, Mikolas Janota
import sys

def err(m):
    print m
    exit(100)

def run(f, N):
    m = dict()
    for l in f:
        l = l.strip()
        if not l or l[0] != 'v':
            continue
        ns = map(int, l.split()[1:])
        for n in ns:
            if n == 0: break
            m[abs(n)] = n
    print 'MODEL: ', m
    for i in range(N):
        for j in range(N):
            v = i*N + j + 1
            if v not in m: c = '?'
            else: c = '*' if m[v] > 0 else '_'
            sys.stdout.write(c)
            sys.stdout.write(' ')
        sys.stdout.write('\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        err('USAGE: '+sys.argv[0]+' board_size <model')
    run(sys.stdin, int(sys.argv[1]))
