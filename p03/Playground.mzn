include "exactly.mzn";

int: upper_bound;
int: m;
int: j;

var int: c;

array [1..m, 1..j] of int: tasks;

array [1..m, 1..upper_bound] of var 1..j: T;


constraint forall(x in 1..m)(
               forall(y in 1..j-1) (
                   exactly(tasks[x,y], T[x,..], y)
               )
           );
           
output [show (tasks) ++ "lol"];
% solve satisfy;
% output ["Machine " ++ show(x) ++ " " ++ show(T[x,y]) ++ "\n" | x in 1..m, y in 1..upper_bound]

%output [show(T[1,..])];
%output [show(T[2,..])];