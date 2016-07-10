#include "copycat.hpp"
#include <sstream>
#include "scip_exception.hpp"

using namespace std;

CopycatSolver::CopycatSolver(int _n, int _d, int _m, int _h)
: scip(NULL), n(_n), d(_d), m(_m), h(_h),
  vars_x(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_n))),
  vars_a(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_n))),
  vars_y(_m, vector<vector<SCIP_Var *>>(_h, vector<SCIP_Var *>(_d)))
{
    init_scip_env();
    create_vars();
    /*
    for( size_t i = 0; i < _n; ++i )
    {
       SCIP_CONS * cons;
       namebuf.str("");
       namebuf<<"row_"<<i;

       // create SCIP_CONS object
       // this is an equality since there must be a queen in every row
       SCIP_CALL_EXC(SCIPcreateConsLinear(_scip, & cons, namebuf.str().c_str(), 0, NULL, NULL, 1.0, 1.0,
 					  TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE) );

       // add the vars belonging to field in this row to the constraint
       for( size_t j = 0; j < _n; ++j )
          SCIP_CALL_EXC( SCIPaddCoefLinear(_scip, cons, _vars[i][j], 1.0) );

       // add the constraint to scip
       SCIP_CALL_EXC( SCIPaddCons(_scip, cons) );

       // store the constraint for later on
       _cons.push_back(cons);
    }*/
}

void CopycatSolver::init_scip_env()
{
   SCIP_CALL_EXC(SCIPcreate(&scip));

   SCIP_CALL_EXC(SCIPincludeDefaultPlugins(scip));

   // disable scip output to stdout
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
            }
            for (int i = 0; i < d; i++)
            {
                SCIP_CALL_EXC(SCIPreleaseVar(scip, &vars_y[k][t][i]));
            }
        }
    }

    for(vector<SCIP_CONS *>::size_type i = 0; i < constraints.size(); ++i)
    {
        SCIP_CALL_EXC(SCIPreleaseCons(scip, &constraints[i]) );
    }

    SCIP_CALL_EXC(SCIPfree(&scip));
}

void CopycatSolver::solve(void)
{
   SCIP_CALL_EXC(SCIPsolve(scip));
}
