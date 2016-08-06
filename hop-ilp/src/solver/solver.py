from gurobipy import *
import random

from logger import logger
import utils


class Solver(object):

    def __init__(self, name, problem, num_futures, debug=False):
        self.problem = problem
        self.num_futures = num_futures

        self.m = Model(name)
        self.variables, self.states, self.actions = self.add_variables()
        self.init_constrs = self.add_init_states_constraints()
        self.add_hop_action_constraints()
        self.add_hop_quality_criterion()
        self.intermediate_vars = []
        self.transition_constrs = self.add_transition_constraints()

        if debug:
            self.m.update()
            self.m.write('model.lp')
        else:
            self.m.setParam(GRB.Param.OutputFlag, 0)

    def solve(self):
        logger.info('optimizing_model')
        self.m.optimize()

        if self.m.Status == GRB.Status.INFEASIBLE or self.m.Status == GRB.Status.INF_OR_UNBD:
            raise Exception('Failed to find solution')

        suggested_actions = {}
        for a in self.actions.select('*', 0, 0):
            suggested_actions[a[0]] = int(self.variables[a].X)

        return suggested_actions, self.m.objVal

    def init_next_step(self, states_init_values):
        """
        Reinitialize the solver with a new set of states' values and
        prepare the transitions determinization for the next time step
        """
        for constr in self.init_constrs:
            self.m.remove(constr)
        self.problem.variables.update(states_init_values)
        self.init_constrs = self.add_init_states_constraints()

        for c in self.transition_constrs:
            self.m.remove(c)
            self.transition_constrs = []
        for v in self.intermediate_vars:
            self.m.remove(v)
            self.intermediate_vars = []
        self.transition_constrs = self.add_transition_constraints()

        logger.info("reinitialized_model")

    def add_transition_constraints(self):
        random.seed()
        m = self.m
        horizon = self.problem.horizon
        transition_trees = self.problem.transition_trees
        intermediate_vars = self.intermediate_vars
        transition_constrs = []

        for k in range(self.num_futures):
            for t in range(horizon - 1):
                for v in transition_trees:
                    path_vars = self.determinize_paths(transition_trees[v],
                                                       k, t, v,
                                                       transition_constrs)
                    intermediate_vars.extend(path_vars)

                    i, constrs = self.combine_paths(k, t, v, path_vars)
                    intermediate_vars.append(i)
                    transition_constrs.extend(constrs)

                    next_step_var = self.variables[v, k, t + 1]
                    constr_name = 'trans_{}_{}_{}'.format(v, k, t)
                    constr = m.addConstr(next_step_var == i, name=constr_name)
                    transition_constrs.append(constr)

        return transition_constrs

    def determinize_paths(self, transition_tree, k, t, v, transition_constrs):
        m = self.m
        path_vars = []
        p = [0]

        def determinize_path(nodes):
            if random.random() > nodes[-1][1]:
                return

            name = 'f_{}_{}_{}_{}'.format(v, k, t, p[0])
            i = m.addVar(vtype=GRB.BINARY, name=name)
            path_vars.append(i)
            m.update()

            signed_vars = self.tree_path_to_signed_vars(nodes, k, t)
            constrs = utils.add_and_constraints(m, signed_vars, i, name=name)
            transition_constrs.extend(constrs)

            p[0] += 1

        transition_tree.traverse_paths(determinize_path)
        return path_vars

    def combine_paths(self, k, t, v, path_vars):
        name = 'fs_{}_{}_{}'.format(v, k, t)
        i = self.m.addVar(vtype=GRB.BINARY, name=name)
        self.m.update()

        constrs = utils.add_or_constraints(self.m, path_vars, i, name=name)

        return i, constrs

    def add_hop_quality_criterion(self):
        num_futures = self.num_futures
        m = self.m
        p = [0]

        def func(nodes):
            for k in range(num_futures):
                for t in range(self.problem.horizon):
                    coeff = 1./num_futures * nodes[-1][1]
                    name = 'w_{}_{}_{}'.format(k, t, p[0])
                    v = m.addVar(vtype=GRB.BINARY, obj=coeff, name=name)
                    m.update()

                    signed_vars = self.tree_path_to_signed_vars(nodes, k, t)
                    constr_name = 'reward_{}_{}_{}'.format(k, t, p[0])
                    utils.add_and_constraints(m, signed_vars, v,
                                              name=constr_name)
            p[0] += 1

        self.problem.reward_tree.traverse_paths(func)

        m.ModelSense = GRB.MAXIMIZE
        logger.info('added_hop_quality_criterion')

    def tree_path_to_signed_vars(self, nodes, k, t):
        """
        Returns of list of (variable, sign) from a list of nodes along
        a decision tree path. `sign` has the same value as the value
        associated with each node

        :param nodes: list of (node name, value) on a decision path
        :param k: the future index
        :param t: the horizon index
        """
        return [(self.variables[name, k, t], val) for (name, val) in nodes[:-1]]

    def add_variables(self):
        """
        Adds variables to the LP model. Variables include both
        state variables and action variables
        :return : (all variables, states tuplelist, actions tuplelist)
        """
        if self.problem.horizon is None:
            raise AttributeError('missing horizon attribute in problem')

        horizon = self.problem.horizon
        m = self.m
        variables = {}
        states = tuplelist()
        actions = tuplelist()

        for v in self.problem.variables:
            for k in range(self.num_futures):
                for t in range(horizon):
                    lp_var = m.addVar(vtype=GRB.BINARY,
                                      name='%s_%d_%d' % (v, k, t))
                    variables[v, k, t] = lp_var
                    states.append((v, k, t))

        for a in self.problem.actions:
            for k in range(self.num_futures):
                for t in range(horizon):
                    lp_var = m.addVar(vtype=GRB.BINARY,
                                      name='%s_%d_%d' % (a, k, t))
                    variables[a, k, t] = lp_var
                    actions.append((a, k, t))

        m.update()
        logger.info('added_variables|num_vars=%d' % len(variables))
        return variables, states, actions

    def add_hop_action_constraints(self):
        """
        Adds first step constraints on action variables
        """
        m = self.m
        variables = self.variables
        init_constrs = []

        for a in self.problem.actions:
            first_step_actions = self.actions.select(a, '*', 0)
            for i in range(len(first_step_actions) - 1):
                a1 = variables[first_step_actions[i]]
                a2 = variables[first_step_actions[i + 1]]
                constr_name = 'act_{}_{}'.format(a, i)
                m.addConstr(a1 == a2, name=constr_name)

        logger.info('added_hop_action_constraints')
        return init_constrs

    def add_init_states_constraints(self):
        """
        Adds first step constraints on state variables
        """
        m = self.m
        variables = self.variables
        init_constrs = []

        first_step_states = self.states.select('*', '*', 0)
        init_values = self.problem.variables
        for v in first_step_states:
            init_value = init_values[v[0]]
            constr_name = 'init_{}_{}'.format(v[0], v[1])
            constr = m.addConstr(variables[v] == init_value, name=constr_name)
            init_constrs.append(constr)

        return init_constrs
