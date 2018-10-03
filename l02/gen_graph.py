#!/usr/bin/python
# File:  gen_graph.py
# Author:  mikolas
# Created on:  26 Sep 2017 12:26:01
# Copyright (C) 2017, Mikolas Janota
import sys,random

def err(m):
    print 'ERROR:', m
    exit(100)

def run(vs, p):
    es = []
    for i in range(vs):
        for j in range(i+1, vs):
            if random.random() < p:
                es.append((i,j))
    print 'c Erdos-Renyi graph with', vs, 'nodes and p =', p
    print 'h', vs, len(es)
    for e in es:
        print e[0], e[1]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        err('USAGE: '+sys.argv[0]+' num_vertices edge_probability')
    run(int(sys.argv[1]), float(sys.argv[2]))
