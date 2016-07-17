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
    void print_problem();
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
    std::vector<std::vector<SCIP_VAR *>> vars_z;

    std::vector<SCIP_Cons *> constraints;

    /*
     * Private methods
     */
    void init_scip_env();
    void create_vars();
    double generate_rand();

    SCIP_RETCODE create_constraints(const std::vector<int>& states);
    SCIP_RETCODE create_initial_states_constraints(const std::vector<int>& states);
    SCIP_RETCODE create_initial_actions_constraints();
    SCIP_RETCODE create_transition_constraints();
    SCIP_RETCODE create_y_transition_constraints(
            int k, int t, const std::vector<int>& determinized_x);

    void release_constraints();

    // Create constraint in the form of <var> = <value>
    SCIP_RETCODE create_single_var_constraint(
            const char* name, SCIP_Var* var, SCIP_Real value, SCIP_Cons** pcons);
    // Create constraint without adding variable or coefficients
    SCIP_RETCODE create_constraint(
            const char* name, SCIP_Real lhs, SCIP_Real rhs, SCIP_Cons** pcons);
    std::vector<int> get_optimal_action();
};

#endif
