#!/bin/python3
from pysat.solvers import Glucose4
from pysat.card import *
import numpy as np
import sys

debug = False

data = sys.stdin.readlines()


class JobFlowProblem:

    def __init__(self, m, j):
        self.machines = m
        self.jobs = j
        self.tasks = np.zeros((m, j), dtype=int)
        self.useless = []


    def __str__(self):
        sm = ""
        for j in range(self.jobs):
            for i in range(self.machines):
                sm += " " + str(self.tasks[i, j])
            sm += "\n"
        return sm


    def set_task(self, m, j, d):
        self.tasks[m, j] = d


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


    def greedy_span(self):
        jobs = sorted(np.copy(self.tasks).T,key=lambda task: np.sum(task))
        minimum = np.sum(jobs[0])
        jobs.reverse()
        lst = [0 for i in range(self.machines)]
        who_lst = [0 for i in range(self.machines)]
        count = 0

        while True:
            if np.sum(jobs) + sum(lst) == 0:
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


    def solve(self):
        if debug:
            print("Calculating greedy solution...")

        self.min_timestep, self.max_timestep = self.greedy_span()
        
        if debug:
            print("Bounds found:[", self.min_timestep, ",", self.max_timestep, "]")
            print("Generating clauses...")

        jobs = range(self.jobs)
        machines = range(self.machines)
        times = range(self.max_timestep)

        g = Glucose4()


        # UMA TAREFA DE DURAÇÃO K TEM DE SER EXECUTADA DURANTE K TIMESTEPS
        for m in machines:
            for j in jobs:
                lits = []
                for t in times:
                    lits.append(self.var_id(m, j, t))
                if debug: 
                    print(list(map(self.id_var, lits)), "=", self.tasks[m,j])
                cnf = CardEnc.equals(lits=lits, bound=self.tasks[m,j], top_id=max(self.var_id(self.machines-1,self.jobs-1,self.max_timestep), g.nof_vars()), encoding=6)
                g.append_formula(cnf.clauses)
        

        # UMA TAREFA NÃO PODE SER INTERROMPIDA
        for m in machines:
            for j in jobs:
                for t in range(0,self.max_timestep - 1):
                    for t1 in range(t+1, self.max_timestep):
                        g.add_clause([-self.var_id(m,j,t), self.var_id(m,j,t+1), -self.var_id(m,j,t1)])
                        if debug:
                            print((m,j,t), 'and -', (m,j,t+1), "=> -", (m,j,t1))
                for t in range(1,self.max_timestep):
                    for t1 in range(0, t):
                        g.add_clause([self.var_id(m,j,t-1), -self.var_id(m,j,t), -self.var_id(m,j,t1)])
                        if debug:
                            print('-', (m,j,t-1), 'and ', (m,j,t), "=> -", (m,j,t1))



        # TAREFAS SÃO EXECUTADAS POR ORDEM
        for j in jobs:
            for m in machines:
                for other_m in range(m + 1, self.machines):
                    for t in times:
                        for other_t in range(0,t+1):
                            if self.tasks[m, j] != 0:  # task doesn't have duration 0
                                if self.tasks[other_m, j] != 0:  #other task doesn't have duration 0
                                    if other_t < self.max_timestep:
                                        g.add_clause([-self.var_id(m, j, t), -self.var_id(other_m, j, other_t)])
                                        if debug:
                                            print((m,j,t), "=> -", (other_m, j, other_t))
        

        # DUAS TAREFAS NÃO SE PODEM SOBREPOR NA MESMA MAQUINA
        for m in machines:
            for t in times:
                lits = []
                for j in jobs:
                    lits.append(self.var_id(m, j, t))

                if debug:
                    print(list(map(self.id_var, lits)), "<=1")
                cnf = CardEnc.atmost(lits=lits, top_id=max(self.var_id(self.machines-1,self.jobs-1,self.max_timestep), g.nof_vars()), encoding=6)
                g.append_formula(cnf.clauses)


        #print("Solving...")
        model = None
        sat = True
        t_max = self.max_timestep
        t_min = self.min_timestep
        while True:
            t = int(np.floor((t_max + t_min) / 2))
            asmpt = []
            for m in range(self.machines):
                for j in range(self.jobs):
                    for t1 in range(t, self.max_timestep):
                        asmpt.append(-self.var_id(m, j, t1))
            if debug:
                print("Running iteration for t =", t)

            sat = g.solve(asmpt)
            if sat:
                model = g.get_model()
                t_max = t
            else:
                t_min = t

            if abs(t_min - t_max) <= 1:
                break
        
        if model == None:
            if debug:
                print("UNSAT")
            return
        if debug:
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


    def parse_model(self, model):
        result = np.full((self.machines, self.jobs), -1, dtype=int)
        
        for var in model:
            if abs(var) > self.var_id(self.machines-1,self.jobs-1,self.max_timestep):
                continue

            m, j, t = self.id_var(abs(var))

            if var > 0:
                if result[m][j] == -1 or result[m][j] > t:
                    result[m][j] = t

        return result


    def makespan(self, parsed_model):
        max_t = 0
        for m in range(self.machines):
            for j in range(self.jobs):
                max_t = max(max_t, parsed_model[m][j] + self.tasks[m,j])
        return max_t


    def print_model(self, model):
        if not model:
            print("No solution!")
            return

        out = np.zeros((self.machines, self.max_timestep), dtype=int)

        for var in model:
            if abs(var) >= self.var_id(self.machines-1,self.jobs-1,self.max_timestep):
                continue

            sign = var > 0
            m, j, t = self.id_var(abs(var))
            if sign:
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


n, m = map(int, data[0].split())

problem = JobFlowProblem(m, n)

for job in range(0, n):
    parts = data[job + 1].split()
    k = int(parts[0])

    for i in range(0, k):
        machine, duration = map(int, parts[i + 1].split(":"))
        problem.set_task(machine - 1, job, duration)

problem.solve()
