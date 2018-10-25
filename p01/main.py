#!/bin/python3
from pysat.solvers import Glucose4
from pysat.card import *
import numpy as np
import sys

debug = True

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
        jobs.reverse()
        lst = [0 for i in range(self.machines)]
        who_lst = [0 for i in range(self.machines)]
        count = 0

        while True:
            if np.sum(jobs) + sum(lst) == 0:
                return count

            count += 1
            for i in range(len(lst)):
                if lst[i] > 0:
                    lst[i] = max(0, lst[i]-1)
                    jobs[who_lst[i]][i] = max(0, jobs[who_lst[i]][i]-1)
                
                for job_index in range(len(jobs)):
                    if lst[i] == 0 and (jobs[job_index][i] > 0) and np.sum(jobs[job_index][:i]) == 0:
                        lst[i] = jobs[job_index][i]
                        who_lst[i] = job_index

            #print(jobs, lst)


    def solve(self):
        self.max_timestep = self.greedy_span()
        print(self.max_timestep)
        print("Generating clauses...")
        jobs = range(self.jobs)
        machines = range(self.machines)
        times = range(self.max_timestep)


        g = Glucose4()
        # TAREFAS SÃO SEQUENCIAIS
        for m in machines:
            for j in jobs:
                if self.tasks[m, j] != 0:  # task doesn't have duration 0
                    for t in times:
                        self.useless += [(m,j,t)]
                        for other_t in range(0, t + self.tasks[m, j]):
                            for other_m in range(m + 1, self.machines):
                                if self.tasks[other_m, j] != 0:  #other task doesn't have duration 0
                                    g.add_clause([-self.var_id(m, j, t), -self.var_id(other_m, j, other_t)])
        

        # DUAS TAREFAS NÃO SE PODEM SOBREPOR NA MESMA MAQUINA
        for m in machines:
            for t in times:
                lits = []
                for j in jobs:
                    lits.append(self.var_id(m, j, t))

                card_cnf = CardEnc.atmost(lits=lits, top_id=max(self.var_id(self.machines-1,self.jobs-1,self.max_timestep), g.nof_vars()), encoding=6)
                g.append_formula(card_cnf.clauses)



        # TODAS AS TAREFAS TÊM DE SER EXECUTADAS
        for m in machines:
            for j in jobs:
                if self.tasks[m, j] != 0:  # task doesn't have duration 0
                    lst = []
                    for t in times:
                        if t + self.tasks[m, j] < self.max_timestep:
                            lst += [self.var_id(m, j, t)]

                    card_cnf = CardEnc.equals(lits=lst, top_id=max(self.var_id(self.machines-1,self.jobs-1,self.max_timestep), g.nof_vars()), encoding=6)
                    g.append_formula(card_cnf.clauses)

                else:  # task has duration 0. Don't execute
                    for t in times:
                        g.add_clause([-self.var_id(m, j, t)])

        print("Solving...")
        model = None
        sat = True
        t = self.max_timestep
        while sat and t >= 0:
            asmpt = []
            for m in range(self.machines):
                for j in range(self.jobs):
                    for t1 in range(t, self.max_timestep):
                        asmpt.append(-self.var_id(m, j, t1))
            print("Running iteration...")
            sat = g.solve(asmpt)
            if sat:
                model = g.get_model()
                t = min(self.makespan(self.parse_model(model)) - 1, t) - 1

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
            m, j, t = self.id_var(abs(var))

            if (m,j,t) not in self.useless:
                continue

            if t < self.max_timestep and j < self.jobs and m < self.machines:
                if var > 0:
                    result[m][j] = t

        return result


    def makespan(self, parsed_model):
        max_t = 0
        for m in range(self.machines):
            for j in range(self.jobs):
                max_t = max(max_t, parsed_model[m][j] + self.tasks[m, j])
        return max_t


    def print_model(self, model):
        if not model:
            print("No solution!")
            return

        out = np.zeros((self.machines, self.max_timestep), dtype=int)

        for var in model:
            sign = var > 0

            m, j, t = self.id_var(abs(var))
            if sign:
                out[m][t] = j + 1
                for t1 in range(t, t + self.tasks[m, j]):
                    out[m][t1] = j + 1

        for m in range(self.machines):
            print("m" + '{0:01d}'.format(m + 1) + " ", end='')
            for t in range(self.max_timestep):
                if out[m][t] != 0:
                    print('j' + str(out[m][t]), end=' ')
                else:
                    print("   ", end='')
            print()

        print("t  ", end='')
        for t in range(self.max_timestep):
            print('{0:02d} '.format(t), end='')
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
