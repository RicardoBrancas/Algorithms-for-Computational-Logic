include "exactly.mzn";
include "count.mzn";

int: upper_bound;
int: m;
int: j;

var 0..upper_bound: c;

array [1..m, 1..j] of int: tasks;

array [1..m, 1..upper_bound] of var 0..j: T;


constraint forall(x in 1..m)(
               forall(y in 1..j) (
                   exactly(tasks[x,y], T[x,..], y)
               )
           );
           
constraint forall(x in 1..m)(
               forall(y in 1..upper_bound) (
                   y > c -> T[x, y] = 0
               )
           );
           
constraint forall(x in 2..m)(
               forall(y in 1..upper_bound) (
                   forall(z in 1..j) (
                     (y > 1 -> (T[x, y] == z -> exactly(tasks[x-1, z], T[x-1,1..y-1], z)))
                     /\
                     (y = 1 -> (T[x, y] == z -> tasks[x-1, z] = 0))
                   )
               )
           );
           
solve minimize c;
output [show(T[x,..]) ++ "\n" | x in 1..m]