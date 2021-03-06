#!/usr/bin/python3
import subprocess
import argparse
import numpy as np
import sys
import ast

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
        
        data += 'lower_bound=' + str(self.min_timestep) + ';'
        data += 'upper_bound=' + str(self.max_timestep) + ';'
        data += 'machines=' + str(self.machines) + ';'
        data += 'jobs=' + str(self.jobs) + ';'
        
        data += 'tasks=['
        for m in range(self.machines):
            data += '|'
            for j in range(self.jobs):
                data += str(self.tasks[m,j]) + ','

        data += '|];'

        data += 'next=['
        for m in range(self.machines-1):
            data += '|'
            for j in range(self.jobs):
                data += str(self.next[m,j]+1) + ','
        data += '|];'

        if debug:
            print(data)
        
        if debug: 
            ps = subprocess.Popen(('minizinc', '--search-complete-msg', '', '--soln-sep', '', '--verbose-solving', 'jfp_3.mzn', '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        else:
            ps = subprocess.Popen(('minizinc', '--search-complete-msg', '', '--soln-sep', '', 'jfp_3.mzn', '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
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
        print(tmp[0])
        print(tmp[1])

        tmp = tmp[2:]

        concat = {}
        for j in range(self.jobs):
            concat[j] = {}
            for m in range(self.machines):
                cur = tmp[m][1:len(tmp[m])-1].replace(" ", "").split(",")  
                concat[j][m] = {}
                for el in cur:
                    done = False
                    if int(el) == 0:
                        continue

                    for key in concat[j][m].keys():
                        if int(el) == concat[j][m][key] + key:
                            concat[j][m][key] += 1
                            done = True

                    if not done:
                        concat[j][m][int(el)] = 1

            tmp = tmp[self.machines+1:]
        
        for j in range(self.jobs):
            print(len(concat[j].keys()),end=" ")
            for m in range(self.machines):
                for key in sorted(list(concat[j][m].keys())):
                    print(str(m+1) + ":" + str(key-1) + ":" + str(concat[j][m][key]), end = " ")
            print()
        return



parser = argparse.ArgumentParser(description='A CSP based solver for the Job Flow Scheduling Problem.')
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
