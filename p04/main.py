#!/usr/bin/python3
import subprocess
import argparse
import numpy as np
import sys
import ast
import re

debug = False
printClauses = False


class JobFlowProblem:

    def __init__(self, m, j, tasks):
        self.machines = m
        self.jobs = j
        self.tasks = tasks
        self.min_timestep, self.max_timestep = self.greedy_span()
        self.next = self.compute_next();


    def greedy_span(self):
        if debug:
            print("Computing greedy solution...")

        jobs = sorted(np.copy(self.tasks).T, key = lambda task: np.sum(task))
        jobs.reverse()
        minimum = max(np.sum(jobs[0]), np.max(np.sum(jobs, axis=0)))
        lst = [0 for i in range(self.machines)]
        who_lst = [0 for i in range(self.machines)]
        count = 0

        while True:
            if np.sum(jobs) + sum(lst) == 0:
                if debug:
                    print("Bounds found: [", minimum, ",", count, "]")
                return minimum, count

            count += 1
            for i in range(len(lst)):
                if lst[i] > 0:
                    lst[i] = max(0, lst[i]-1)
                    jobs[who_lst[i]][i] = max(0, jobs[who_lst[i]][i]-1)
                
                for job_index in range(len(jobs)):
                    if lst[i] == 0 and (jobs[job_index][i] > 0) and np.sum(jobs[job_index][:i]) == 0:
                        lst[i] = jobs[job_index][i]
                        who_lst[i] = job_index

    def compute_next(self): 
        X = np.zeros((self.machines-1, self.jobs), dtype=int)

        for j in range(self.jobs):
            for m in range(self.machines-1):
                m1 = m + 1

                while m1 < self.machines and self.tasks[m1, j] == 0:
                    m1 += 1
                X[m,j] = m1

        return X

    
    def generate_formula(self):
        data = ''
        
        data += 'timestep(1..' + str(self.max_timestep-1) + ').'

        data += '#const lowerbound = ' + str(self.min_timestep) + '.'
        data += '#const upperbound = ' + str(self.max_timestep) + '.'
        data += '#const maxdur = ' + str(np.max(self.tasks)) + '.'
        #data += 'upper_bound=' + str(self.max_timestep) + ';'
        #data += 'machines=' + str(self.machines) + ';'
        #data += 'jobs=' + str(self.jobs) + ';'
        
        data += 'dur('
        for m in range(self.machines):
            for j in range(self.jobs):
                data += str(j+1) + ',' + str(m+1) + ',' + str(self.tasks[m,j]) + ';'
        data += ').'


        data += 'next('
        for m in range(self.machines-1):
            for j in range(self.jobs):
                data += str(j+1) + ',' + str(m+1) + ',' + str(self.next[m,j]+1) + ';'
        data += ').'

        if debug:
            print(data)
        
        ps = subprocess.Popen(('clingo', '--outf=1', '--configuration=trendy', '--heuristic=Domain', 'model.lp', '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        output, _ = ps.communicate(data)
        
        if debug and printClauses:
            print(output)

        self.parse_it(output)
        return


    def makespan(self, parsed_model):
        max_t = 0
        for m in range(self.machines):
            for t in range(self.max_timestep):
                if parsed_model[m,t] != 0:
                    max_t = max(max_t, t+1)
        return max_t


    def parse_it(self, string):
        tmp = string.split("\n")
        
        sch = np.full((self.jobs, self.machines, np.max(self.tasks)), -1, dtype=int)

        for line in tmp:
            if not line.startswith('%') and not line.startswith('ANSWER'):
                execs = re.findall(r"exec\((\d+),(\d+),(\d+),(\d+)\)\.", line)

                for exe in execs:
                    sch[int(exe[0]) - 1, int(exe[1]) - 1, int(exe[2]) - 1] = int(exe[3]) - 1
        
        print(np.max(sch) + 1)
        print(self.jobs, self.machines)
       
        if debug:
            print(sch)

        for j in range(self.jobs):
            print(self.machines, end=' ')
            for m in range(self.machines):
                if self.tasks[m,j] == 0:
                    continue
                last = -1
                count = 0
                start = 0
                for t in range(self.tasks[m,j]):
                    if last != sch[j,m,t] - 1:
                        if last != -1:
                            print(m+1, start, count, sep=':', end=' ')
                        start = sch[j,m,t]
                        count = 1
                        last = sch[j,m,t]
                    else:
                        count += 1
                        last = sch[j,m,t]
                print(m+1, start, count, sep=':', end=' ')

            print()

parser = argparse.ArgumentParser(description='A ASP based solver for the Job Flow Scheduling Problem.')
parser.add_argument('--verbose', '-v', action='count')

args = parser.parse_args()

if args.verbose:
    debug = args.verbose >= 1
    printClauses = args.verbose >= 2

data = sys.stdin.readlines()

j, m = map(int, data[0].split())
tasks = np.zeros((m, j), dtype=int)

for job in range(0, j):
    parts = data[job + 1].split()
    k = int(parts[0])

    for i in range(0, k):
        machine, duration = map(int, parts[i + 1].split(":"))
        tasks[machine - 1, job] = duration

problem = JobFlowProblem(m, j, tasks)
problem.generate_formula()
