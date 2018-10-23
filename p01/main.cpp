#include <iostream>
#include <cstdio>
#include <cstring>

class job_flow_problem {

    unsigned machines, jobs;
    unsigned max_timestep;

    unsigned *tasks;

public:

    job_flow_problem(unsigned m, unsigned j) : machines(m), jobs(j) {
        tasks = new unsigned[m * j];
        std::memset(tasks, 0, m*j);
        max_timestep = 0; //TODO!
    }

    ~job_flow_problem() {
        delete tasks;
    }




    void set_task(unsigned m, unsigned j, unsigned d) {
        tasks[t_index(m,j)] = d;
    }

    void write(std::ostream &os) {
        
    }




    inline unsigned t_index(unsigned m, unsigned j) const {
        return m * jobs + j;
    }

    inline unsigned var_id(unsigned m, unsigned job, unsigned time) {
        return m * jobs * max_timestep + job * max_timestep + time;
    }

};


int main(int argc, char **argv) {

    unsigned n, m;

    std::cin >> n >> m;

    job_flow_problem problem(m, n);

    for (unsigned job = 0; job < n; job++) {
        unsigned k;
        std::cin >> k;

        for(unsigned i = 0; i < k; i++) {
            unsigned machine, duration;
            std::scanf("%d:%d", &machine, &duration);

            problem.set_task(machine, job, duration);
        }
    }

    return 0;
}
