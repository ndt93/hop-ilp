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

    std::vector<int> next_action(const std::vector<int>& states);
private:
    /*
     * Private fields
     */
    SCIP* scip;
    bool is_first_action;

    int n; // Number of x state variables
    int d; // Number of y state variables
    int m; // Number of futures
    int h; // Horizon depth

    // States indexed by [future][step][state]
    std::vector<std::vector<std::vector<SCIP_VAR *>>> vars_x;
    std::vector<std::vector<std::vector<SCIP_VAR *>>> vars_a;
    std::vector<std::vector<std::vector<SCIP_VAR *>>> vars_y;

    // Transition constraints indexed by [future][step][state]
    std::vector<std::vector<std::vector<SCIP_Cons *>>> x_transition_constraints;
    std::vector<std::vector<std::vector<SCIP_Cons *>>> y_transition_constraints;
    // Initial action constraints indexed by [future][state]
    std::vector<std::vector<SCIP_Cons *>> initial_x_constraints;
    std::vector<std::vector<SCIP_Cons *>> initial_y_constraints;
    std::vector<std::vector<SCIP_Cons *>> initial_a_constraints;

    /*
     * Private methods
     */
    void init_scip_env();
    void create_vars();

    SCIP_RETCODE create_constraints(const std::vector<int>& states);
    SCIP_RETCODE create_initial_states_constraints(const std::vector<int>& states);
    SCIP_RETCODE create_initial_actions_constraints();

    SCIP_RETCODE modify_constraints(const std::vector<int>& states);

    std::vector<int> get_optimal_action();
};

#endif
