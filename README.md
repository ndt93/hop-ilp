## HOP-ILP

Implementations of serveral solvers for probabilistic planning problems such as MDP using Hindsight Optimization (HOP)

* An implementation of the paper: [Hindsight optimization for probabilistic planning with factored actions](http://www.aaai.org/ocs/index.php/ICAPS/ICAPS15/paper/download/10600/10404).
The solver reduces the HOP problem into a integer linear program via satistfiability clauses and employ a generic ILP solver.
This also includes a custom parser for the Symbolic Sperseus (SPUDD) file format.

    * Dependencies: [Gurobi](http://www.gurobi.com/), [ANTLR v4 runtime](http://www.antlr.org/download.html)

* An currently researched HOP solver which reduces the HOP problem into a Maximum A Posteriori problem in an Markov Random Field.

    * Dependency: [David Sontag's MPLP solver](http://cs.nyu.edu/~dsontag/code/mplp_ver2.tgz)
