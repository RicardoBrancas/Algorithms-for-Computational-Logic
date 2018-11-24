include "count.mzn";
include "global_cardinality.mzn";

predicate gcc(array[int] of var int: x, array[int] of var int: counts) =
  global_cardinality(x,
                     [ i | i in index_set(counts) ],
                     array1d(counts));

int: lower_bound;
int: upper_bound;
int: m;
int: j;
array [1..m, 1..j] of int: tasks;

var lower_bound..upper_bound: c;
array [1..m, 1..upper_bound] of var 0..j: T;


constraint forall(x in 1..m)(
			   gcc(T[x,..], tasks[x, ..])
           );
           
constraint forall(x in 1..m)(
               forall(y in c..upper_bound) (
                   T[x, y] = 0
               )
           );
           
constraint forall(x in 2..m)(
               forall(z in 1..j) (
                   T[x, 1] == z -> tasks[x-1, z] = 0
               )
               /\
               forall(y in 2..upper_bound) (
                   forall(z in 1..j) (
                     T[x, y] == z -> count(T[x-1,1..y-1], z, tasks[x-1, z])
                   )
               )
           );
           
solve minimize c;
output [show(T[x,..]) ++ "\n" | x in 1..m]
