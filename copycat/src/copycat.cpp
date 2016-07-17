#include "copycat.hpp"
#include <sstream>
#include <cstdlib>
#include <numeric>

#include "scip_exception.hpp"

using namespace std;

CopycatSolver::CopycatSolver(int _n, int _d, int _m, int _h)
: scip(NULL), is_first_action(true), n(_n), d(_d), m(_m), h(_h),
  vars_x(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_n))),
  vars_a(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_n))),
  vars_y(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_d))),
  vars_z(_m, vector<SCIP_Var *>(_h))
{
    init_scip_env();
    create_vars();
    srand(time(NULL));
}

void CopycatSolver::init_scip_env()
{
   SCIP_CALL_EXC(SCIPcreate(&scip));

   SCIP_CALL_EXC(SCIPincludeDefaultPlugins(scip));

   // Disable scip output to stdout
   //SCIP_CALL_EXC(SCIPsetMessagehdlr(scip, NULL));

   SCIP_CALL_EXC(SCIPcreateProb(scip, "copycat", NULL, NULL, NULL, NULL, NULL, NULL, NULL));

   SCIP_CALL_EXC(SCIPsetObjsense(scip, SCIP_OBJSENSE_MAXIMIZE));
}

void CopycatSolver::create_vars()
{
    ostringstream namebuf;
    SCIP_Var* var;
    for (int k = 0; k < m; ++k)
    {
        for (int t = 0; t < h; ++t)
        {
            namebuf.str("");
            namebuf << "z#" << k << "#" << t;
            SCIP_CALL_EXC(SCIPcreateVar(scip, &var, namebuf.str().c_str(),
                                        0.0, 1.0, 0.0, SCIP_VARTYPE_BINARY,
                                        TRUE, FALSE, NULL, NULL, NULL, NULL, NULL));
            SCIP_CALL_EXC(SCIPaddVar(scip, var));
            vars_z[k][t] = var;

            for (int i = 0; i < n; ++i)
            {
                 namebuf.str("");
                 namebuf << "x#" << k << "#" << t << "#" << i;
                 SCIP_CALL_EXC(SCIPcreateVar(scip, &var, namebuf.str().c_str(),
                                             0.0, 1.0, 0.0, SCIP_VARTYPE_BINARY,
                                             TRUE, FALSE, NULL, NULL, NULL, NULL, NULL));
                 SCIP_CALL_EXC(SCIPaddVar(scip, var));
                 vars_x[k][t][i] = var;

                 namebuf.str("");
                 namebuf << "a#" << k << "#" << t << "#" << i;
                 SCIP_CALL_EXC(SCIPcreateVar(scip, &var, namebuf.str().c_str(),
                                             0.0, 1.0, 0.0, SCIP_VARTYPE_BINARY,
                                             TRUE, FALSE, NULL, NULL, NULL, NULL, NULL));
                 SCIP_CALL_EXC(SCIPaddVar(scip, var));
                 vars_a[k][t][i] = var;
            }

            for (int i = 0; i < d; ++i)
            {
                 namebuf.str("");
                 namebuf << "y#" << k << "#" << t << "#" << i;
                 SCIP_CALL_EXC(SCIPcreateVar(scip, &var, namebuf.str().c_str(),
                                             0.0, 1.0, 1.0, SCIP_VARTYPE_BINARY,
                                             TRUE, FALSE, NULL, NULL, NULL, NULL, NULL));
                 SCIP_CALL_EXC(SCIPaddVar(scip, var));
                 vars_y[k][t][i] = var;
            }
        }
    }
}

/*
void CopycatSolver::disp(std::ostream& out)
{
   // get the best found solution from scip
   SCIP_SOL * sol = SCIPgetBestSol(_scip);
   out << "solution for " << _n << "-queens:" << endl << endl;

   // when SCIP did not succeed then sol is NULL
   if (sol == NULL)
   {
      out << "no solution found" << endl;
      return;
   }

   for( size_t i = 0; i < _n; ++i )
   {
      for( size_t j = 0; j < _n; ++j )
         out << " ---";
      out << endl;

      for( size_t j = 0; j < _n; ++j )
      {
         out << "| ";
         // we display a D in every field if x[i][j] = 1 which means that a queen will be placed there
         if ( SCIPgetSolVal(_scip, sol, _vars[i][j]) > 0.5 )
            out << "D ";
         else
            out << "  ";
      }
      out << "|" << endl;
   }
   for( size_t j = 0; j < _n; ++j)
      out << " ---";
   out << endl;
}
*/

CopycatSolver::~CopycatSolver(void)
{
    for (int k = 0; k < m; ++k)
    {
        for (int t = 0; t < h; ++t)
        {
            for (int i = 0; i < n; ++i)
            {
                SCIP_CALL_EXC(SCIPreleaseVar(scip, &vars_x[k][t][i]));
                SCIP_CALL_EXC(SCIPreleaseVar(scip, &vars_a[k][t][i]));
            }
            for (int i = 0; i < d; ++i)
            {
                SCIP_CALL_EXC(SCIPreleaseVar(scip, &vars_y[k][t][i]));
            }
        }
    }

    release_constraints();

    SCIP_CALL_EXC(SCIPfree(&scip));
}

std::vector<int> CopycatSolver::next_action(const vector<int>& states)
{
    if (!is_first_action)
        release_constraints();

    create_constraints(states);
    is_first_action = false;
    // TODO: SCIP_CALL_EXC(SCIPsolve(scip));
    return get_optimal_action();
}

SCIP_RETCODE CopycatSolver::create_constraints(const vector<int>& states)
{
    SCIP_CALL(create_initial_states_constraints(states));
    SCIP_CALL(create_initial_actions_constraints());
    SCIP_CALL(create_transition_constraints());
    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_initial_states_constraints(const std::vector<int>& states)
{
    SCIP_CONS *cons;
    ostringstream namebuf;

    for (int k = 0; k < m; ++k)
    {
        for (int i = 0; i < n; ++i)
        {
            namebuf.str("");
            namebuf << "cons_x#" << k << "#0#" <<  i;
            SCIP_CALL(create_single_var_constraint(namebuf.str().c_str(), vars_x[k][0][i], states[i], &cons));
            constraints.push_back(cons);
        }
        for (int i = 0; i < d; ++i)
        {
            namebuf.str("");
            namebuf << "cons_y#" << k << "#0#" <<  i;
            SCIP_CALL(create_single_var_constraint(namebuf.str().c_str(), vars_y[k][0][i], states[n + i], &cons));
            constraints.push_back(cons);
        }
    }

    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_initial_actions_constraints()
{
    SCIP_CONS *cons;
    ostringstream namebuf;

    for (int k = 0; k < m - 1; ++k)
    {
        for (int i = 0; i < n; ++i)
        {
            namebuf.str("");
            namebuf << "cons_a#" << k << "#0#" <<  i;

            SCIP_CALL(create_constraint(namebuf.str().c_str(), 0.0, 0.0, &cons));
            SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_a[k][0][i], 1.0));
            SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_a[k + 1][0][i], -1.0));
            constraints.push_back(cons);
        }
    }
    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_transition_constraints()
{
    SCIP_CONS *cons;
    ostringstream namebuf;
    vector<int> determinized_x(n);

    for (int k = 0; k < m; ++k)
    {
        for (int t = 1; t < h; ++t)
        {
            for (int i = 0; i < n; ++i)
            {
                namebuf.str("");
                namebuf << "cons_x#" << k << "#" <<  t << "#" << i;

                if (generate_rand() < 0.5)
                {
                    SCIP_CALL(create_single_var_constraint(namebuf.str().c_str(), vars_x[k][t][i], 0.0, &cons));
                    determinized_x[i] = 0;
                }
                else
                {
                    SCIP_CALL(create_single_var_constraint(namebuf.str().c_str(), vars_x[k][t][i], 1.0, &cons));
                    determinized_x[i] = 1;
                }

                constraints.push_back(cons);
            }

            SCIP_CALL(create_y_transition_constraints(k, t, determinized_x));
        }
    }

    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_y_transition_constraints(int k, int t, const std::vector<int>& determinized_x)
{
    SCIP_CONS *cons;
    ostringstream namebuf;

    int positive_x_count = accumulate(begin(determinized_x), end(determinized_x), 0);
    SCIP_Var **cons_a_vars = new SCIP_Var*[n];
    SCIP_Real *cons_a_coeffs = new SCIP_Real[n];
    for (int i = 0; i < n; ++i)
    {
        cons_a_vars[i] = vars_a[k][t - 1][i];
        cons_a_coeffs[i] = determinized_x[i] == 0 ? 1.0 : -1.0;
    }

    if (generate_rand() < 0.49)
    {
        namebuf.str("");
        namebuf << "cons_y#" << k << "#" <<  t << "#0";
        SCIP_CALL(SCIPcreateConsLinear(scip, &cons, namebuf.str().c_str(),
                                       n, cons_a_vars, cons_a_coeffs,
                                       1 - positive_x_count, n + 1 - positive_x_count,
                                       TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE));
        SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_y[k][t][0], 1.0));
        SCIP_CALL(SCIPaddCons(scip, cons));
        constraints.push_back(cons);
    }

    for (int i = 1; i < d; ++i)
    {
        if (generate_rand() >= 0.49)
            continue;

        namebuf.str("");
        namebuf << "cons_y#" << k << "#" <<  t << "#" << i;
        SCIP_CALL(SCIPcreateConsLinear(scip, &cons, namebuf.str().c_str(),
                                       n, cons_a_vars, cons_a_coeffs,
                                       -positive_x_count, n + 1 - positive_x_count,
                                       TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE));
        SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_y[k][t][i - 1], -1.0));
        SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_y[k][t][i], 1.0));
        SCIP_CALL(SCIPaddCons(scip, cons));
        constraints.push_back(cons);
    }

    delete [] cons_a_vars;
    delete [] cons_a_coeffs;
    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_single_var_constraint(
        const char* name, SCIP_Var* var, SCIP_Real value, SCIP_Cons** pcons)
{
    SCIP_CALL(create_constraint(name, value, value, pcons));
    SCIP_CALL(SCIPaddCoefLinear(scip, *pcons, var, 1.0));
    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_constraint(
        const char* name, SCIP_Real lhs, SCIP_Real rhs, SCIP_Cons** pcons)
{
    SCIP_CALL(SCIPcreateConsLinear(scip, pcons, name,
                                   0, NULL, NULL, lhs, rhs,
                                   TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE));
    SCIP_CALL(SCIPaddCons(scip, *pcons));
    return SCIP_OKAY;
}

void CopycatSolver::release_constraints()
{
    for (auto cons : constraints)
    {
        SCIP_CALL_EXC(SCIPdelCons(scip, cons));
        SCIP_CALL_EXC(SCIPreleaseCons(scip, &cons));
    }
    constraints.clear();
}

vector<int> CopycatSolver::get_optimal_action()
{
    return vector<int>();
}

double CopycatSolver::generate_rand()
{
    return ((double) rand()) / RAND_MAX;
}

void CopycatSolver::print_problem()
{
    SCIP_CALL_EXC(SCIPprintOrigProblem(scip, NULL, NULL, FALSE));
}
