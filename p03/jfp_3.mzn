include "disjunctive_strict.mzn";
include "alldifferent_except_0.mzn";

int: lower_bound;
int: upper_bound;
int: machines;
int: jobs;
array [1..machines, 1..jobs] of int: tasks;
array [1..machines-1, 1..jobs] of int: next;
array [1..jobs] of int: tasks_not_zero;

var lower_bound..upper_bound: c;
array [1..machines+1, 1..jobs, 1..max(tasks)] of var 0..upper_bound+1: T;

constraint forall(m in 1..machines) (
              forall(j in 1..jobs) (
                forall(t in tasks[m, j]+1..max(tasks)) (
                  T[m, j, t] = 0
                )
                /\
                forall(t in 1..tasks[m, j]) (
                  T[m, j, t] > 0
				  /\
				  T[m, j, t] <= c
                )
              )
          );

constraint forall(m in 1..machines) (
			alldifferent_except_0(array1d(T[m, .., ..]))
);

constraint forall(j in 1..jobs) (
                forall(t in 1..max(tasks)) (
                  T[machines+1, j, t] = upper_bound+1
                )
              );
          
constraint forall(j in 1..jobs) (
              forall(m in 1..machines-1) (
                ((tasks[m,j] != 0) -> (T[m,j,tasks[m,j]] < T[next[m,j],j,1]))
                /\
                forall(t in 1..tasks[m, j]-1) (
                  T[m,j,t] < T[m,j,t+1]
                )
              )
              /\ 
              forall(t in 1..tasks[machines, j]-1) (
                T[machines,j,t] < T[machines,j,t+1]
              )
);


solve minimize c;

output [show(c) ++ "\n"];
output [show(jobs) ++ " " ++ show(machines) ++ "\n"];
output [concat([show(T[m, j, ..]) ++ "\n" | m in 1..machines]) ++ "\n" | j in 1..jobs]
