#!/bin/python3
import argparse
from pysat.solvers import Glucose4
from pysat.card import *
import numpy as np
import sys

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


    def output(self, model):
        if model == None:
            print("UNSAT")

        if debug and printClauses:
            self.print_model(model)
        
        result = self.parse_model(model)

        print(self.makespan(result))
        print(self.jobs, self.machines)

        for j in range(self.jobs):
            print((result[:, j] >= 0).sum(), end=' ')
            for m in range(self.machines):
                if result[m][j] != -1:
                    print(str(m + 1) + ':' + str(result[m][j]), end=' ')
            print()


    def solve_bin_search(self):
        formula = self.formula()

        g = Glucose4(incr=True)
        g.append_formula(formula)

        if debug:
            print("Solving...")
            print(g.nof_clauses(), "clauses")
            print(g.nof_vars(), "variables")
        
        t_min = self.min_timestep
        t_max = self.max_timestep
        model = None
        while True:
            t = (t_min + t_max) // 2
            if debug:
                print("Solving for t =", t, ". With t_min =", t_min, "and t_max =", t_max)

            assumptions = []
            append = assumptions.append
            for t1 in range(t, self.max_timestep):
                for j in range(self.jobs):
                    for m in range(self.machines):
                        append(-self.var_id(m,j,t1))

            if g.solve(assumptions):
                model = g.get_model()
                t_max = t - 1
            else:
                t_min = t + 1
            
            if t_max - t_min < 0:
                break
        
        self.output(model)

       
    def solve_unsatsat(self):
        formula = self.formula()
        
        g = Glucose4(incr=True)
        g.append_formula(formula)

        if debug:
            print("Solving...")
            print(g.nof_clauses(), "clauses")
            print(g.nof_vars(), "variables")

        model = None
        t = self.min_timestep
        while t <= self.max_timestep:
            if debug:
                print("Solving for t =", t)

            assumptions = []
            append = assumptions.append
            for t1 in range(t, self.max_timestep):
                for j in range(self.jobs):
                    for m in range(self.machines):
                        append(-self.var_id(m,j,t1))

            if g.solve(assumptions):
                model = g.get_model()
                break

            t += 1
        
        self.output(model)


    def formula(self):
        if debug:
            print("Generating clauses...")

        jobs = range(self.jobs)
        machines = range(self.machines)
        times = range(self.max_timestep)
        times_minus_last = range(self.max_timestep - 1)
        
        formula = []
        f_append = formula.append
        
        for m in machines:

            # DUAS TAREFAS NÃO SE PODEM SOBREPOR NA MESMA MAQUINA

            for t in times:
                lits = []
                append = lits.append
                for j in jobs:
                    append(self.var_id(m, j, t))

                if debug and printClauses:
                    print(list(map(self.id_var, lits)), "<=1")
                cnf = CardEnc.atmost(lits=lits, top_id=self.top, encoding=EncType.cardnetwrk)
                self.update_top(cnf)
                formula += cnf.clauses

            for j in jobs:

                # TODAS AS TAREFAS DE DURAÇÃO NÃO NULA TÊM DE SER EXECUTADAS

                if self.tasks[m,j] != 0:
                    lits = []
                    append = lits.append
                    for t in times:
                        append(self.var_id(m, j, t))

                    if debug and printClauses: 
                        print(list(map(self.id_var, lits)))

                    f_append(lits)

                # UMA TAREFA NÃO PODE SER INTERROMPIDA

                for d in range(1, self.tasks[m,j]): #caso especial do primeiro timestep
                    if d < self.max_timestep:
                        f_append([-self.var_id(m,j,0), self.var_id(m,j,d)])

                        if debug and printClauses:
                            print((m,j,0), '=>', (m,j,d))

                for t in range(1,self.max_timestep):
                    for d in range(t+1, t + self.tasks[m,j]):
                        if d < self.max_timestep:
                            f_append([self.var_id(m,j,t-1), -self.var_id(m,j,t), self.var_id(m,j,d)])

                            if debug and printClauses:
                                print('-', (m,j,t-1), 'and', (m,j,t), '=>', (m,j,d))

                # TAREFAS SÃO EXECUTADAS POR ORDEM

                for other_m in range(m + 1, self.machines):
                    for t in times_minus_last:
                        for other_t in range(0,t+1):
                            if self.tasks[m, j] != 0 and self.tasks[other_m, j] != 0:  #tasks don't have duration 0
                                f_append([-self.var_id(m, j, t), -self.var_id(other_m, j, other_t)])
                                if debug and printClauses:
                                    print((m,j,t), "=> -", (other_m, j, other_t))

        return formula
        

    def parse_model(self, model):
        result = np.full((self.machines, self.jobs), -1, dtype=int)
        
        for var in model:
            if var > 0:
                if abs(var) > self.var_id(self.machines-1,self.jobs-1,self.max_timestep):
                    continue

                m, j, t = self.id_var(abs(var))

                if result[m][j] == -1 or t < result[m][j]:
                    result[m][j] = t

        return result


    def makespan(self, parsed_model):
        max_t = 0
        for m in range(self.machines):
            for j in range(self.jobs):
                max_t = max(max_t, parsed_model[m][j] + self.tasks[m,j])
        return max_t


    def print_model(self, model):
        out = np.zeros((self.machines, self.max_timestep), dtype=int)

        for var in model:
            if var > 0:
                if abs(var) > self.var_id(self.machines-1,self.jobs-1,self.max_timestep):
                    continue

                m, j, t = self.id_var(abs(var))
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
parser.add_argument('--method', '-m', choices=['binary', 'unsatsat'], default='binary')

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

if args.method == 'binary':
    problem.solve_bin_search()

elif args.method == 'unsatsat':
    problem.solve_unsatsat()
