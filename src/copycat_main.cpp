#include "copycat.hpp"
#include <cstdlib>
#include <iostream>
#include "scip_exception.hpp"

using namespace std;

int main(int args, char ** argv)
{
   if (args < 5)
   {
      cerr << argv[0]
           << " <number of x states> <number of y states> <number of futures> <horizon depth>" << endl;
      exit(EXIT_FAILURE);
   }

   int n = abs(atoi(argv[1]));
   int d = abs(atoi(argv[2]));
   int m = abs(atoi(argv[3]));
   int h = abs(atoi(argv[4]));

   try
   {
      CopycatSolver solver(n, d, m, h);

      solver.solve();
   }
   catch (const SCIPException& exc)
   {
      cerr << exc.what() << endl;
      exit((int) exc.getRetcode());
   }

   return EXIT_SUCCESS;
}
