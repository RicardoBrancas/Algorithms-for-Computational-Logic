
% Generate
1 { exec(J, M, D, T) : timestep(T) } 1 :- subtask(J, M, D).

% Define
task(J, M) :- dur(J, M, D).
subtask(J, M, 1..D) :- dur(J, M, D).

next(J, M, T1, M, T2) :- subtask(J, M, T1),
                         subtask(J, M, T2),
                         T2 = T1 + 1.

next(J, M1, T1, M2, T2) :- subtask(J, M1, T1),
                           subtask(J, M2, T2),
                           dur(J, M1, D1),
                           D1 != 0,
                           T1 = D1,
                           T2 = 1,
                           next(J, M1, M2).

used(lowerbound).
used(1..T) :- used(T).
used(T) :- exec(_, _, _, T).

% Test
:- next(J, M1, D1, M2, D2),
   exec(J, M1, D1, T1),
   exec(J, M2, D2, T2),
   T1 >= T2.

:- exec(J, M, D, T1), 
   exec(J, M, D, T2),
   T1 != T2. 

:- exec(J1, M, D1, T1),
   exec(J2, M, D2, T2),
   T1 = T2,
   1 {J1 != J2; D1 != D2}.

%:- exec(J1, M, D1, T1),
%   exec(J2, M, D2, T2),
%   exec(J1, M, D3, T3),
%   exec(J2, M, D4, T4),
%   J1 != J2,
%   T1 < T2, T2 < T3, T3 < T4.

#minimize { T : used(T) }.
#heuristic exec(J, M, D, T) : subtask(J, M, D), timestep(T). [upperbound-T+1,level]
#heuristic exec(J, M, D, T) : subtask(J, M, D), timestep(T). [1,sign]
#show exec/4.
