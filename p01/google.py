from __future__ import print_function

# Import Python wrapper for or-tools constraint solver.
from ortools.constraint_solver import pywrapcp

def main():
  # Create the solver.
  solver = pywrapcp.Solver('jobshop')

  machines_count = 40
  jobs_count = 20
  all_machines = range(0, machines_count)
  all_jobs = range(0, jobs_count)
  # Define data.
  machines = [[0, 1, 2, 4, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 20, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 36, 37, 39], [8, 14, 18, 19, 20, 24, 29, 30, 36, 38, 39], [1, 3, 5, 11, 13, 17, 20, 24, 26, 33, 38], [0, 1, 2, 4, 5, 6, 8, 10, 11, 13, 14, 15, 17, 18, 19, 20, 22, 24, 25, 26, 27, 28, 31, 32, 33, 37, 39], [0, 2, 3, 5, 7, 8, 9, 12, 13, 20, 21, 22, 23, 25, 27, 29, 30, 35], [0, 3, 5, 6, 7, 8, 11, 14, 16, 19, 20, 21, 22, 23, 24, 26, 27, 30, 33, 34, 35, 36, 39], [0, 1, 3, 4, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31, 32, 36, 37, 39], [10, 20], [1, 2, 3, 5, 6, 8, 9, 16, 17, 19, 22, 25, 27, 29, 33, 35, 37, 39], [3, 7, 9, 10, 20, 30, 31], [3, 9, 10, 16, 20, 24, 26, 27, 29, 32, 33, 34, 36, 37, 39], [23, 35, 39], [1, 3, 9, 22], [0, 3, 5, 8, 9, 10, 11, 14, 15, 16, 19, 21, 25, 26, 28, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39], [0, 1, 3, 6, 8, 9, 12, 13, 14, 15, 16, 18, 21, 22, 23, 24, 25, 26, 29, 31, 35, 36, 37], [2, 29, 33], [0, 1, 2, 6, 8, 9, 15, 16, 21, 22, 25, 27, 35, 37, 38], [3, 5, 6, 11, 15, 20, 27, 32, 35, 36, 37, 38], [1, 2, 5, 9, 13, 16, 17, 19, 20, 22, 24, 25, 27, 28, 29, 33, 34, 39], [0, 2, 5, 10, 14, 15, 18, 23, 31, 37]] 
  
  processing_times = [[1, 2, 1, 2, 1, 2, 1, 2, 2, 3, 2, 3, 2, 3, 1, 2, 3, 2, 2, 2, 3, 1, 1, 3, 2, 1, 1, 2, 3, 1], [2, 3, 2, 1, 2, 3, 2, 2, 2, 1, 3], [2, 2, 3, 2, 2, 1, 2, 1, 3, 3, 2], [3, 2, 1, 1, 1, 1, 2, 1, 3, 3, 1, 1, 2, 2, 3, 1, 3, 3, 3, 3, 2, 1, 2, 2, 3, 2, 1], [3, 1, 3, 3, 1, 2, 1, 3, 2, 2, 3, 3, 2, 2, 1, 1, 2, 2], [1, 3, 1, 2, 3, 1, 2, 2, 1, 2, 3, 2, 1, 1, 2, 1, 1, 3, 3, 1, 3, 1, 1], [2, 2, 1, 3, 3, 1, 3, 2, 2, 2, 2, 1, 2, 2, 3, 3, 3, 2, 2, 3, 3, 1, 1, 1, 2, 1, 3, 2, 2], [2, 2], [3, 1, 2, 3, 1, 2, 3, 3, 3, 3, 3, 1, 1, 3, 3, 1, 2, 1], [2, 3, 2, 1, 1, 3, 1], [2, 1, 2, 3, 1, 3, 1, 3, 2, 2, 3, 2, 1, 1, 1], [3, 1, 1], [3, 1, 3, 1], [3, 1, 1, 1, 1, 3, 2, 3, 3, 1, 3, 1, 3, 2, 2, 1, 1, 3, 3, 1, 2, 3, 1, 3, 3], [1, 3, 3, 3, 2, 2, 2, 3, 3, 3, 1, 2, 3, 2, 2, 2, 2, 2, 1, 3, 2, 3, 3], [3, 3, 3], [1, 1, 3, 1, 3, 2, 3, 3, 3, 1, 1, 3, 2, 1, 2], [3, 1, 3, 3, 1, 2, 2, 1, 3, 3, 3, 3], [1, 3, 3, 3, 2, 3, 3, 2, 1, 2, 2, 2, 2, 2, 2, 3, 2, 3], [1, 3, 2, 2, 1, 2, 1, 1, 1, 3]] 
 
  # Computes horizon.
  horizon = 0
  for i in all_jobs:
    horizon += sum(processing_times[i])
  # Creates jobs.
  all_tasks = {}
  for i in all_jobs:
    for j in range(0, len(machines[i])):
      all_tasks[(i, j)] = solver.FixedDurationIntervalVar(0,
                                                          horizon,
                                                          processing_times[i][j],
                                                          False,
                                                          'Job_%i_%i' % (i, j))

  # Creates sequence variables and add disjunctive constraints.
  all_sequences = []
  all_machines_jobs = []
  for i in all_machines:

    machines_jobs = []
    for j in all_jobs:
      for k in range(0, len(machines[j])):
        if machines[j][k] == i:
          machines_jobs.append(all_tasks[(j, k)])
    disj = solver.DisjunctiveConstraint(machines_jobs, 'machine %i' % i)
    all_sequences.append(disj.SequenceVar())
    solver.Add(disj)

  # Add conjunctive contraints.
  for i in all_jobs:
    for j in range(0, len(machines[i]) - 1):
      solver.Add(all_tasks[(i, j + 1)].StartsAfterEnd(all_tasks[(i, j)]))

  # Set the objective.
  obj_var = solver.Max([all_tasks[(i, len(machines[i])-1)].EndExpr()
                        for i in all_jobs])
  objective_monitor = solver.Minimize(obj_var, 1)
  # Create search phases.
  sequence_phase = solver.Phase([all_sequences[i] for i in all_machines],
                                solver.SEQUENCE_DEFAULT)
  vars_phase = solver.Phase([obj_var],
                            solver.CHOOSE_FIRST_UNBOUND,
                            solver.ASSIGN_MIN_VALUE)
  main_phase = solver.Compose([sequence_phase, vars_phase])
  # Create the solution collector.
  collector = solver.LastSolutionCollector()

  # Add the interesting variables to the SolutionCollector.
  collector.Add(all_sequences)
  collector.AddObjective(obj_var)

  for i in all_machines:
    sequence = all_sequences[i];
    sequence_count = sequence.Size();
    for j in range(0, sequence_count):
      t = sequence.Interval(j)
      collector.Add(t.StartExpr().Var())
      collector.Add(t.EndExpr().Var())
  # Solve the problem.
  disp_col_width = 10
  if solver.Solve(main_phase, [objective_monitor, collector]):
    print("\nOptimal Schedule Length:", collector.ObjectiveValue(0), "\n")
    sol_line = ""
    sol_line_tasks = ""
    print("Optimal Schedule", "\n")

    for i in all_machines:
      seq = all_sequences[i]
      sol_line += "Machine " + str(i) + ": "
      sol_line_tasks += "Machine " + str(i) + ": "
      sequence = collector.ForwardSequence(0, seq)
      seq_size = len(sequence)

      for j in range(0, seq_size):
        t = seq.Interval(sequence[j]);
         # Add spaces to output to align columns.
        sol_line_tasks +=  t.Name() + " " * (disp_col_width - len(t.Name()))

      for j in range(0, seq_size):
        t = seq.Interval(sequence[j]);
        sol_tmp = "[" + str(collector.Value(0, t.StartExpr().Var())) + ","
        sol_tmp += str(collector.Value(0, t.EndExpr().Var())) + "] "
        # Add spaces to output to align columns.
        sol_line += sol_tmp + " " * (disp_col_width - len(sol_tmp))

      sol_line += "\n"
      sol_line_tasks += "\n"

    print(sol_line_tasks)
    print("Time Intervals for Tasks\n")
    print(sol_line)

if __name__ == '__main__':
  main()
