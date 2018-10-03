#!/usr/bin/python
# File:  model2graph.py
# Author:  mikolas
# Created on:  Mon, Sep 25, 2017 13:43:31
# Copyright (C) 2017, Mikolas Janota
import sys

def warning(m):
    print '// WARNING:', m

def err(m):
    print 'ERROR:', m
    exit(100)

def rd_model(f):
    m = dict()
    for l in f:
        l = l.strip()
        if not l or l[0] != 'v': continue
        ns = map(int, l.split()[1:])
        for n in ns:
            if n == 0: break
            m[abs(n)] = n
    return m

def prn_graph_header(): print 'graph G {'
def prn_graph_close(): print '}'
def node2str(n): return 'N'+str(n)
def prn_edge(s,t): print ' ', node2str(s), '--', node2str(t), ';' 
def prn_node(n, sel_col):
    cols=['blue','red','green','cyan','white','pink','indigo', 'gold', 'olive', 'black']
    print ' ', node2str(n), '[', 'shape=box, style=filled, fillcolor='+cols[sel_col], '];'

def chk_node(s,vs):
    if s<0 or s>=vs: err('expecting nodes in range 0..vs-1')

def chk_edge(s,t,vs,coloring):
    chk_node(s,vs)
    chk_node(t,vs)
    if coloring[s] == coloring[t]: warning(str(s)+' and '+str(t)+' are colored the same')


def col2var(cols, node, col): return node*cols+col+1

def make_coloring(vs, cols, model):
    coloring = dict()
    for n in range(vs):
        sel_col = None
        for col in range(cols): # look for selected color
            var = col2var(cols, n, col)
            if var not in model or model[var] <= 0:
                continue
            if sel_col != None: err("two selected colors in model for node {}".format(n))
            sel_col = col
        if sel_col == None: err("no selected colors for node:" + str(n) + " looking for vars " + str(col2var(cols, n, 0))+'..'+str(col2var(cols,n, cols-1)))
        coloring[n]=sel_col
    return coloring

def prn_nodes(vs,  coloring):
    for n in range(vs):
        prn_node(n, coloring[n])

def rd_graph(f, cols, model):
    m = dict()
    has_header=False
    prn_graph_header()
    for l in f:
        l = l.strip()
        if not l or l[0] == 'c': continue
        spl = l.split()
        if not has_header: # reading header
            if spl[0] != 'h': err("header expected")
            vs, es = map(int, spl[1:])
            has_header = True
            coloring = make_coloring(vs, cols, model)
            prn_nodes(vs, coloring)
        else: # reading edges
            if len(spl) != 2: err("2 vertices expected for each edge")
            s,t = int(spl[0]), int(spl[1])
            chk_edge(s,t,vs,coloring)
            prn_edge(s,t)
    prn_graph_close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        err('USAGE: '+sys.argv[0]+' num_colors graph_file <model')
    model = rd_model(sys.stdin)
    cols = int(sys.argv[1])
    graph_file = open(sys.argv[2])
    rd_graph(graph_file, cols, model)
