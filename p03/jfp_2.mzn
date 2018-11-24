include "disjunctive_strict.mzn";

int: lower_bound;
int: upper_bound;
int: machines;
int: jobs;
array [1..machines, 1..jobs] of int: tasks;
array [1..jobs] of int: tasks_not_zero;

var lower_bound..upper_bound: c;
array [1..machines, 1..jobs, 0..max(tasks)] of var -1..upper_bound: T;
array [1..machines, 1..jobs, 0..max(tasks)] of var 0..max(tasks): D;

constraint forall(m in 1..machines) (
              forall(j in 1..jobs) (
                forall(t in tasks[m, j]..max(tasks)) (
                  T[m, j, t] = -1
                )
              )
          );
          
constraint forall(m in 1..machines) (
              forall(j in 1..jobs) (
                sum(D[m, j, ..]) = tasks[m, j]
                /\
                forall(t in 0..max(tasks)) (
                  ((D[m, j, t] != 0) <-> (T[m, j, t] != -1))
                  /\
                  T[m, j, t] + D[m, j, t] <= c
                )
                /\
                forall(t in 0..max(tasks)-1) (
                  (((T[m, j, t] != -1) /\ (T[m, j, t+1] != -1)) -> (T[m, j, t] < T[m, j, t+1]))
                  /\
                  ((T[m, j, t] = -1) -> (T[m, j, t+1] = -1))
                )
              )
              /\
              disjunctive_strict(array1d(T[m,..,..]), array1d(D[m,..,..]))
          );
          
constraint forall(m in 2..machines) (
              forall(j in 1..jobs) (
                ((tasks[m,j] = 0) -> (T[m,j,0] = -1))
                /\
                forall (t in 0..max(tasks)) (
                  forall(m1 in 1..m-1) (
                    (tasks[m,j] != 0) -> (T[m,j,0] >= T[m1,j,t] + D[m1,j,t])
                  )
                )
              )
          );

solve minimize c;

output [show(c) ++ "\n"];
output [show(jobs) ++ " " ++ show(machines) ++ "\n"];
output [show(tasks_not_zero[j]) ++ " " ++ concat([ concat([ show(m) ++ ":" ++ show(T[m,j,t]) ++ ":" ++ show(D[m,j,t]) ++ " " | t in 0..max(tasks) where fix(T[m,j,t]) != -1]) | m in 1..machines]) ++ "\n" | j in 1..jobs]