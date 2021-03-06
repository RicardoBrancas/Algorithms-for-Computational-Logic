#!/bin/python3
import argparse
import numpy as np
import sys
from z3 import *

debug = False
printClauses = False


class JobFlowProblem:

    def __init__(self, m, j, tasks):
        self.machines = m
        self.jobs = j
        self.tasks = tasks
        self.min_timestep, self.max_timestep = self.greedy_span()
        self.top = self.var_id(self.machines-1, self.jobs-1, self.max_timestep) + 1


    def __str__(self):
        sm = ""
        for j in range(self.jobs):
            for i in range(self.machines):
                sm += " " + str(self.tasks[i, j])
            sm += "\n"
        return sm


    def var_id(self, m, job, time):
        return m * self.jobs * self.max_timestep + job * self.max_timestep + time + 1


    def id_var(self, var_id):
        var_id = var_id - 1
        t = var_id % self.max_timestep
        var_id -= t
        j = (var_id % (self.jobs * self.max_timestep)) // self.max_timestep
        var_id -= j * self.max_timestep
        m = var_id // (self.jobs * self.max_timestep)
        return m, j, t


    def update_top(self, cnf):
        max_lit = 0
        for clause in cnf.clauses:
            for lit in clause:
                max_lit = max(max_lit, abs(lit))
        self.top = max(self.top, max_lit)


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
    
    def generate_formula(self):

        if debug:
            print("Generating formulation...")

        variables = []

        s = Optimize()
        s_add = s.add
   
        # CREATE VARIABLES
        for m in range(self.machines):
            variables.append([])
            for j in range(self.jobs):
                variables[m].append(Int('t' + str(j+1) + ',' + str(m+1)))
        
        for j in range(self.jobs):

            # OS TEMPOS TẼM DE SER POSITIVOS 
            m = 0
            while m < self.machines and self.tasks[m,j] == 0:
                m += 1
            if m >= self.machines:
                continue
            s_add(variables[m][j] >= 0)
            if debug and printClauses:
                print(variables[m][j], '>= 0')

            # AS TAREFAS DE UM JOB TÊM DE SER EXECUTADAS POR ORDEM
            for m in range(self.machines): 
                while m < self.machines and self.tasks[m, j] == 0:
                    m += 1
                if m >= self.machines:
                    break

                other_m = m + 1
                while other_m < self.machines and self.tasks[other_m, j] == 0:
                    other_m += 1
                if other_m >= self.machines:
                    break

                s_add(variables[m][j] + int(self.tasks[m, j]) <= variables[other_m][j])

                if debug and printClauses:
                    print(variables[m][j] + int(self.tasks[m, j]), '<=', variables[m + 1][j])

            # PARA CADA PARA DE TAREFAS OU UMA ACONTECE ANTES OU A OUTRA
            for m in range(self.machines):
                for other_j in range(j+1, self.jobs):
                    if self.tasks[m,j] == 0 or self.tasks[m,other_j] == 0:
                        continue
                    s_add(Xor(variables[m][j] + int(self.tasks[m,j]) <= variables[m][other_j], variables[m][other_j] + int(self.tasks[m,other_j]) <= variables[m][j]))

                    if debug and printClauses:
                        print(Or(variables[m][j] + int(self.tasks[m,j]) <= variables[m][other_j], variables[m][other_j] + int(self.tasks[m,other_j]) <= variables[m][j]))

        c = Int('c')
        for j in range(self.jobs):
            for m in range(self.machines):
                s_add(variables[m][j] + int(self.tasks[m,j]) <= c)
                if debug and printClauses:
                    print(variables[m][j] + int(self.tasks[m,j]) <= c)

        s.add(int(self.min_timestep) <= c)
        s.add(int(self.max_timestep) >= c)
        if debug and printClauses:
            print(self.min_timestep, '<=', c, '<=', self.max_timestep)

        s.minimize(c)

        if debug:
            print("Solving...")
        s.check()
        model = s.model()

        self.parse_model(model)
        self.output(model)

        if debug and printClauses:
            print(s.statistics())


    def output(self, model):
        if model == None:
            print("UNSAT")

        result = self.parse_model(model)

        if debug and printClauses:
            self.print_model(result)

        print(self.makespan(result))
        print(self.jobs, self.machines)

        for j in range(self.jobs):
            print((result[:, j] >= 0).sum(), end=' ')
            for m in range(self.machines):
                if self.tasks[m,j] != 0 and result[m][j] != -1:
                    print(str(m + 1) + ':' + str(result[m][j]), end=' ')
            print()


    def parse_model(self, model):
        result = np.full((self.machines, self.jobs), -1, dtype=int)
        
        for var in model:
            if str(var) == 'c':
                continue
            j, m = map(int, str(var)[1:].split(','))
            if self.tasks[m-1, j-1] != 0:
                result[m-1][j-1] = model[var].as_long()
            else:
                result[m-1][j-1] = -1

        return result


    def makespan(self, parsed_model):
        max_t = 0
        for m in range(self.machines):
            for j in range(self.jobs):
                if self.tasks[m,j] != 0:
                    max_t = max(max_t, parsed_model[m][j] + self.tasks[m,j])
        return max_t


    def print_model(self, parsed_model):
        out = np.zeros((self.machines, self.max_timestep), dtype=int)

        for m in range(self.machines):
            for j in range(self.jobs):
                for t in range(parsed_model[m][j], parsed_model[m][j] + self.tasks[m][j]):
                    out[m][t] = j + 1

        for m in range(self.machines):
            print("m" + '{0:02d}'.format(m + 1) + " ", end='')
            for t in range(self.max_timestep):
                if out[m][t] != 0:
                    print('j' + '{0:02d}'.format(out[m][t]), end=' ')
                else:
                    print("    ", end='')
            print()

        print("t   ", end='')
        for t in range(self.max_timestep):
            print('{0:03d} '.format(t), end='')
        print()


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
