#ifndef COPYCAT_H
#define COPYCAT_H

#include <vector>
#include <iostream>

#include <scip/scip.h>
#include <scip/scipdefplugins.h>

class CopycatSolver
{
public:
    CopycatSolver(int _n, int _d, int _m, int _h);

    ~CopycatSolver();

    void solve(void);
private:
    SCIP* scip;

    int n; // Number of x state variables
    int d; // Number of y state variables
    int m; // Number of futures
    int h; // Horizon depth

    std::vector<std::vector<std::vector<SCIP_VAR *>>> vars_x;
    std::vector<std::vector<std::vector<SCIP_VAR *>>> vars_a;
    std::vector<std::vector<std::vector<SCIP_VAR *>>> vars_y;
    std::vector<SCIP_CONS *> constraints;

    void init_scip_env();
    void create_vars();
};

#endif
