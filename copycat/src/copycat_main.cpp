#include "copycat.hpp"
#include <cstdlib>
#include <iostream>
#include "scip_exception.hpp"

using namespace std;

int main(int args, char ** argv)
{
    if (args < 5)
    {
        cerr << "Usage: " << argv[0]
             << " <number of x states> <number of y states> <number of futures> <horizon depth>" << endl;
        exit(EXIT_FAILURE);
    }

    int n = abs(atoi(argv[1]));
    int d = abs(atoi(argv[2]));
    int m = abs(atoi(argv[3]));
    int h = abs(atoi(argv[4]));
    vector<int> states(n + d);

    cout << "Enter initial states > ";
    for (int i = 0; i < n; i++)
    {
        cin >> states[i];
    }
    for (int i = 0; i < d; i++)
    {
        states[n + i] = 0;
    }

    try
    {
        cout << "Initializing solver..." << endl;
        CopycatSolver solver(n, d, m, h);
        cout << "Solver initialized" << endl;

        vector<int> next_action = solver.next_action(states);
        solver.print_problem();
        cout << "Action: ";
        for (int i : next_action)
        {
            cout << i << " ";
        }
        cout << endl;
    }
    catch (const SCIPException& exc)
    {
        cerr << exc.what() << endl;
        exit((int) exc.getRetcode());
    }

    return EXIT_SUCCESS;
}
