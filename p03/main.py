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
        self.next = self.baguette();


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

    def baguette(self): 
        for j in range(self.jobs):
            for m in range(self.machines):
                m1 = m + 1

                while m1 < self.machines and self.tasks[m1, j] == 0:
                    m1 += 1
                if m1 >= self.machines:
                    break

                other_m = m + 1
                while other_m < self.machines and self.tasks[other_m, j] == 0:
                    other_m += 1
                if other_m >= self.machines:
                    break

    
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

        data += 'tasks_not_zero=['
        for j in range(self.jobs):
            data += str((self.tasks[:,j] > 0).sum()) + ','
        data += '];'


        data += 'next=['
        for m in range(self.machines):
            data += '|'
            for j in range(self.jobs):
                data += str(self.next[m,j]) + ','
        data += '|];'


        if debug:
            print(data)
        
        if debug: 
            ps = subprocess.Popen(('minizinc', '--search-complete-msg', '', '--soln-sep', '', '--verbose-solving', 'jfp_2.mzn', '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        else:
            ps = subprocess.Popen(('minizinc', '--search-complete-msg', '', '--soln-sep', '', 'jfp_2.mzn', '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        output, _ = ps.communicate(data)
            
        print(output)
        return

        result = []
        for line in output.split('\n'):
            if len(line) > 0 and line[0] == '[':
                result.append(ast.literal_eval(line))

        result = np.array(result)

        self.output(result)


    def output(self, model):
        result = model

        print(self.makespan(result))
        print(self.jobs, self.machines)

        for j in range(self.jobs):
            print((self.tasks[:,j] > 0).sum(), end=' ')
            for m in range(self.machines):
                last_was_j = False
                count = 0
                for t in range(self.max_timestep):
                    if not last_was_j and result[m,t]-1 == j:
                        print(str(m+1) + ':' + str(t) + ':',end='')
                        last_was_j = True
                        count += 1
                    elif last_was_j and result[m,t]-1 == j:
                        count += 1
                    elif last_was_j and result[m,t]-1 != j:
                        print(str(count),end=' ')
                        last_was_j = False
                        count = 0
                if last_was_j == True:
                    print(str(count),end=' ')

            print()



    def makespan(self, parsed_model):
        max_t = 0
        for m in range(self.machines):
            for t in range(self.max_timestep):
                if parsed_model[m,t] != 0:
                    max_t = max(max_t, t+1)
        return max_t


parser = argparse.ArgumentParser(description='A SAT based solver for the Job Flow Scheduling Problem.')
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
