#include "copycat.hpp"
#include <sstream>
#include "scip_exception.hpp"

using namespace std;

CopycatSolver::CopycatSolver(int _n, int _d, int _m, int _h)
: scip(NULL), is_first_action(true), n(_n), d(_d), m(_m), h(_h),
  vars_x(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_n))),
  vars_a(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_n))),
  vars_y(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_d))),
  x_transition_constraints(_m, vector<vector<SCIP_Cons *>>(_h, vector<SCIP_Cons *>(_n))),
  y_transition_constraints(_m, vector<vector<SCIP_Cons *>>(_h, vector<SCIP_Cons *>(_d))),
  initial_x_constraints(_m, vector<SCIP_Cons *>(_n)),
  initial_y_constraints(_m, vector<SCIP_Cons *>(_d)),
  initial_a_constraints(_m, vector<SCIP_Cons *>(_n))
{
    init_scip_env();
    create_vars();
}

void CopycatSolver::init_scip_env()
{
   SCIP_CALL_EXC(SCIPcreate(&scip));

   SCIP_CALL_EXC(SCIPincludeDefaultPlugins(scip));

   // Disable scip output to stdout
   SCIP_CALL_EXC(SCIPsetMessagehdlr(scip, NULL));

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
            for (int i = 0; i < n; i++)
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

            for (int i = 0; i < d; i++)
            {
                 namebuf.str("");
                 namebuf << "y#" << k << "#" << t << "#" << i;
                 SCIP_CALL_EXC(SCIPcreateVar(scip, &var, namebuf.str().c_str(),
                                             0.0, 1.0, 0.0, SCIP_VARTYPE_BINARY,
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
            for (int i = 0; i < n; i++)
            {
                SCIP_CALL_EXC(SCIPreleaseVar(scip, &vars_x[k][t][i]));
                SCIP_CALL_EXC(SCIPreleaseVar(scip, &vars_a[k][t][i]));
                // TODO: SCIP_CALL_EXC(SCIPreleaseCons(scip, &x_transition_constraints[k][t][i]));
            }
            for (int i = 0; i < d; i++)
            {
                SCIP_CALL_EXC(SCIPreleaseVar(scip, &vars_y[k][t][i]));
                // TODO: SCIP_CALL_EXC(SCIPreleaseCons(scip, &y_transition_constraints[k][t][i]));
            }
        }
    }

    for (int k = 0; k < m; k++)
    {
        for (int i = 0; i < n; i++)
        {
            SCIP_CALL_EXC(SCIPreleaseCons(scip, &initial_x_constraints[k][i]));
        }
        for (int i = 0; i < d; i++)
        {
            SCIP_CALL_EXC(SCIPreleaseCons(scip, &initial_y_constraints[k][i]));
        }
    }

    for (int k = 0; k < m - 1; k++)
    {
        for (int i = 0; i < n; i++)
        {
            SCIP_CALL_EXC(SCIPreleaseCons(scip, &initial_a_constraints[k][i]));
        }
    }

    SCIP_CALL_EXC(SCIPfree(&scip));
}

std::vector<int> CopycatSolver::next_action(const vector<int>& states)
{
    if (is_first_action)
    {
        create_constraints(states);
        is_first_action = false;
    }
    else
    {
        modify_constraints(states);
    }

    // TODO: SCIP_CALL_EXC(SCIPsolve(scip));
    return get_optimal_action();
}

SCIP_RETCODE CopycatSolver::create_constraints(const vector<int>& states)
{
    SCIP_CALL(create_initial_states_constraints(states));
    SCIP_CALL(create_initial_actions_constraints());

    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_initial_states_constraints(const std::vector<int>& states)
{
    SCIP_CONS *cons;
    ostringstream namebuf;

    for (int k = 0; k < m; k++)
    {
        for (int i = 0; i < n; i++)
        {
            namebuf.str("");
            namebuf << "cons_x#" << k << "#0" <<  i;

            SCIP_CALL(SCIPcreateConsLinear(scip, &cons, namebuf.str().c_str(),
                                           0, NULL, NULL, states[i], states[i],
                                           TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE));
            SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_x[k][0][i], 1.0));

            SCIP_CALL(SCIPaddCons(scip, cons));
            initial_x_constraints[k][i] = cons;
        }
        for (int i = 0; i < d; i++)
        {
            namebuf.str("");
            namebuf << "cons_y#" << k << "#0" <<  i;

            SCIP_CALL(SCIPcreateConsLinear(scip, &cons, namebuf.str().c_str(),
                                           0, NULL, NULL, states[n + i], states[n + i],
                                           TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE));
            SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_y[k][0][i], 1.0));

            SCIP_CALL(SCIPaddCons(scip, cons));
            initial_y_constraints[k][i] = cons;
        }
    }

    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::create_initial_actions_constraints()
{
    SCIP_CONS *cons;
    ostringstream namebuf;

    for (int k = 0; k < m - 1; k++)
    {
        for (int i = 0; i < n; i++)
        {
            namebuf.str("");
            namebuf << "cons_a#" << k << "#0" <<  i;

            SCIP_CALL(SCIPcreateConsLinear(scip, &cons, namebuf.str().c_str(),
                                           0, NULL, NULL, 0.0, 0.0,
                                           TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE));
            SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_y[k][0][i], 1.0));
            SCIP_CALL(SCIPaddCoefLinear(scip, cons, vars_y[k + 1][0][i], -1.0));

            SCIP_CALL(SCIPaddCons(scip, cons));
            initial_a_constraints[k][i] = cons;
        }
    }
    return SCIP_OKAY;
}

SCIP_RETCODE CopycatSolver::modify_constraints(const vector<int>& states)
{
    return SCIP_OKAY;
}

vector<int> CopycatSolver::get_optimal_action()
{
    return vector<int>();
}
