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

        data += 'tasks_not_zero=['
        for j in range(self.jobs):
            data += str((self.tasks[:,j] > 0).sum()) + ','
        data += '];'


        data += 'next=['
        for m in range(self.machines-1):
            data += '|'
            for j in range(self.jobs):
                data += str(self.next[m,j]+1) + ','
        data += '|];'


        if debug:
            print(data)
        
        if debug: 
            ps = subprocess.Popen(('/Applications/MiniZincIDE.app/Contents/Resources/minizinc', '--search-complete-msg', '', '--soln-sep', '', '--verbose-solving', 'jfp_3.mzn', '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        else:
            ps = subprocess.Popen(('/Applications/MiniZincIDE.app/Contents/Resources/minizinc', '--search-complete-msg', '', '--soln-sep', '', 'jfp_3.mzn', '-'), stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        output, _ = ps.communicate(data)
            
        self.parse_it(output)
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


    def parse_it(self, string):
        tmp = string.split("\n")
        print(tmp[0])
        print(tmp[1])

        tmp = tmp[2:]
        #print(len(tmp))

        concat = {}
        for j in range(self.jobs):
            concat[j] = {}
            for m in range(self.machines):
                cur = tmp[m][1:len(tmp[m])-1].replace(" ", "").split(",")  
                concat[j][m] = {}
                #print(cur)
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
                        
                #for t in range(len(cur)-1):
                #    if int(cur[t]) + 1 == int(cur[t+1]):
                #        acc += 1
                #        if start == 0:
                #            start = cur[t]

                #       # if int(cur[t+2]) != int(cur[t+1]) + 1

                #    elif not start == 0:
                #        concat += str(m+1) + ":" + str(start) + ":" + str(acc)
                #        start = cur[t]
                    
                    
                   

           # print(concat[j])


            tmp = tmp[self.machines+1:]
        #for j in range(len(tmp)-2):
        #    lst = tmp[0][1:len(tmp[0])-1].replace(" ", "").split(",")
            # print(lst)
        #    for i in range(len(lst)):
        #        out = str(i+1) + ":" + str(lst[i]) 
        #        if int(lst[i]) > 0:
        #            print(out, end=" ")
        #    tmp = tmp[1:]
        #    print()
        
        for j in range(self.jobs):
            for m in range(self.machines):
                for key in concat[j][m].keys():
                    print(str(m+1) + ":" + str(key) + ":" + str(concat[j][m][key]), end = " ")
            print()
        return



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
