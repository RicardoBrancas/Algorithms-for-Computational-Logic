#!/usr/bin/python2
# File:  gen-jss.py
# Author:  mikolas
# Created on:  Fri, Sep 14, 2018 18:50:11
# Copyright (C) 2018, Mikolas Janota
import sys,random

def print_usage():
  print 'USAGE:'
  print ' ', sys.argv[0], '<#jobs>', '<#machines>', '<#min_tasks>','<#max_tasks>', '<min_duration>', '<max_duration>'
  print ' e.g. ./gen-jss.py 2 3 1 3 10 20'


def run(jobs, machines, min_tasks, max_tasks, min_duration, max_duration):
     print jobs, machines
     for j in range(jobs):
         n = random.randint(min_tasks, max_tasks)
         ts = random.sample(range(1, machines + 1), n)
         ts.sort()
         print n, ' '.join(['{}:{}'.format(t, random.randint(min_duration, max_duration)) for t in ts])




if __name__ == "__main__":
    if len(sys.argv) != 7:
        print_usage()
        exit(100)
    jobs, machines, min_tasks, max_tasks, min_duration, max_duration = map(int, sys.argv[1:])
    if min_tasks > max_tasks or min_duration > max_duration or max_tasks > machines:
        print 'invalid values of arguments'
        exit(100)
    run(jobs, machines, min_tasks, max_tasks, min_duration, max_duration)
