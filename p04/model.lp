
% Generate
1 { exec(J, M, D, T) : timestep(T) } 1 :- subtask(J, M, D).
used(T) :- exec(_, _, _, T).

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

used(T) :- lowerbound(B), timestep(T), T < B.

% Test
:- next(J, M1, D1, M2, D2),
   exec(J, M1, D1, T1),
   exec(J, M2, D2, T2),
   T1 >= T2.

:- subtask(J, M, D), 
   timestep(T1), 
   timestep(T2), 
   T1 != T2, 
   exec(J, M, D, T1), 
   exec(J, M, D, T2).

:- exec(J1, M, D1, T1),
   exec(J2, M, D2, T2),
   T1 = T2,
   1 {J1 != J2; D1 != D2}.

#minimize { T : used(T) }.
#show exec/4.
