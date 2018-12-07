#!/usr/bin/python2
# File:  chk_jss-p3.py
# Author:  mikolas
# Created on:  Tue Nov 20 18:05:16 DST 2018
# Copyright (C) 2018, Mikolas Janota
import sys

def print_usage():
  print 'USAGE:'
  print ' ', sys.argv[0], 'problem', 'solution'
  print ' ', sys.argv[0], 'problem', '< solution'
  print '   e.g.:', sys.argv[0], 'examples/t.in '
  print '   e.g.: cat examples/t1.sol |', sys.argv[0], 'examples/t.in'

# report an error and exit
def err(msg):
    print >>sys.stderr, 'ERROR:', msg
    print 'status:', 'FAIL'
    exit(1)

# try to convert a string to an int
def num(s):
    try:
        return int(s)
    except ValueError:
        return err('"{}" is supposed to be a number'.format(s))

# read a problem file f
def rd_prob(f):
    jcnt, mcnt = None, None
    for l in f:
        l = l.rstrip()
        els = l.split()
        if not els:                      # skip empty lines
            continue
        if not jcnt:
            if len(els) != 2:
                err('expected header with job and machine count')
            jcnt, mcnt = map(num, els)
            js = dict()
            job_rd = 0
        else:
            ts = num(els[0])
            els = [ s.split(':') for s in els[1:] ]
            if ts != len(els):
                err('fragment count wrong on line "{}"'.format(l.rstrip()))
            if not all(len(s) == 2 for s in els):
                err('wrong line "{}"'.format(l))
            els = [ map(num, e) for e in els ]
            if not all(els[i-1][0] < els[i][0] for i in range(1, len(els))):
                err('tasks not ordered on line "{}"'.format(l))
            if not all(1 <= e[0] and e[0] <= mcnt for e in els):
                err('tasks not in range on line "{}"'.format(l))
            job_rd = job_rd + 1
            js[job_rd] = { e[0] : e[1] for e in els }
    return jcnt, mcnt, js

# read a solution file f
def rd_sol(f):
    jcnt, mcnt, mkspan = None, None, None
    for l in f:
        l = l.rstrip()
        els = l.split()
        if not els:                      # skip empty lines
            continue
        if not mkspan:        # for solutions expect value of makespan first
            mkspan = num(els[0])
        elif not jcnt:
            if len(els) != 2:
                err('expected header with job and machine count')
            jcnt, mcnt = map(num, els)
            js = dict()
            job_rd = 0
        else:
            ts = num(els[0])
            els = [ s.split(':') for s in els[1:] ]
            if not all(len(s) == 3 for s in els):
                err('wrong line "{}"'.format(l))
            els = [ map(num, e) for e in els ]
            for i in range(1, len(els)):
                at, ai = els[i-1][0], els[i-1][1]
                bt, bi = els[i][0], els[i][1]
                if at > bt or (at == bt and ai >= bi):
                    err('fragments not ordered on line "{}"'.format(l))
            if not all(1 <= e[0] and e[0] <= mcnt for e in els):
                err('tasks not in range on line "{}"'.format(l))
            job_rd = job_rd + 1
            js[job_rd] = els
    return jcnt, mcnt, js, mkspan


# print calculated schedule
def prn_sch(ms):
    for m in ms:
        print "M"+str(m), ','.join([ 'J{}@{}-{}'.format(j, ini, ini+dur) for (j, ini, dur) in ms[m]])

# check solution s for problem p
def run(p, s):
    jcnt, mcnt, js_dur = rd_prob(p)                # read problem
    _jcnt, _mcnt, sch, decl_mkspan = rd_sol(s)     # read solution
    if jcnt != _jcnt or mcnt != _mcnt:
        err('solution header does not match the header of the problem')
    for j in sch:                                     # check for overlaps of tasks of each job
        job_sch = sch[j]
        task_duration = dict()
        last_end = None
        for (t, ini, dur) in job_sch:
            if t not in js_dur[j]:
                err('task {} for job {} scheduled but not in input problem'.format(t, j, t))
            task_duration[t] = task_duration.get(t, 0) + dur
            if last_end != None and last_end > ini:
                err('overlap on job {} for fragment {} {}'.format(j, t, ini))
            last_end = ini + dur
        job_durs = js_dur[j]
        for t in job_durs:
            expect = job_durs[t]
            got = task_duration.get(t, 0)
            if expect != got: err('wrong total duration for job {} task {}, expected {}, got {}'.format(j, t, expect, got))

    ms = { m : [] for m in range(1,mcnt+1) }          # map from machines to a list of task fragments
    for j in sch:
        job_sch = sch[j]
        for (t, ini, dur) in job_sch:                             # insert each task fragment of a job into the appropriate machine
            ms[t].append((j, ini, dur))
    for m in ms:                                      # sort task fragments by starting time
        ms[m].sort(key=lambda e: e[1])
    prn_sch(ms)
    mkspan = max(ini+dur for m in ms for (j, ini, dur) in ms[m])
    for m in ms:
        msch = ms[m]
        last_end, last_job = None, None
        for (j, ini, dur) in msch:
            if last_end != None and last_end > ini:
                err('overlap on machine {} for jobs {} and {}'.format(m, last_job, j))
            last_end = ini+dur
            last_job = j

    print 'declared mkspan:', decl_mkspan
    print 'actual mkspan:', mkspan
    if decl_mkspan != mkspan:
        err('declared makespan ({}) does not match the actual one ({})'.format(decl_mkspan, mkspan))
    print 'status:', 'OK'
    return True

# main
if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print_usage()
        exit(100)
    with open(sys.argv[1], 'r') as p:
        with open(sys.argv[2], 'r') if len(sys.argv) == 3 else sys.stdin as s:
            ec = run(p, s)
    exit(0 if ec else 1)
