from gurobipy import *
from logger import logger


class ILPBase(object):
    constr_cats = ['init_states', 'init_actions', 'concurrency', 'transition', 'reward']

    def __init__(self, name, problem, num_futures, time_limit=None, debug=False):
        self.problem_name = name
        self.problem = problem
        self.num_futures = num_futures
        self.debug = debug

        self.constrs = {cat: [] for cat in self.constr_cats} # type: dict[str, list[Constr]]

        self.model = Model(name)

        if time_limit:
            self.model.params.timeLimit = time_limit

        if debug:
            self.model.update()
            self.model.write('model.lp')
        else:
            self.model.setParam(GRB.Param.OutputFlag, 0)

        self.all_vars, self.states, self.actions = self.add_variables()
        self.add_fixed_constrs()

    def solve(self):
        logger.info('optimizing_model')
        self.model.optimize()

        if self.model.Status == GRB.Status.INFEASIBLE or self.model.Status == GRB.Status.INF_OR_UNBD:
            raise Exception('Failed to find solution')

        if self.model.Status == GRB.Status.TIME_LIMIT:
            logger.info('time_limit_exceeded')

        suggested_actions = {}
        for a in self.actions.select('*', 0, 0):
            suggested_actions[a[0]] = int(self.all_vars[a].X)

        return suggested_actions, self.model.objVal

    def init_next_step(self, states):
        self.problem.variables.update(states)
        self.set_init_states_constraints()
        self.set_transition_constrs()
        logger.info("reinitialized_model")

    def add_variables(self):
        """
        Adds variables to the LP model. Variables include both
        state variables and action variables
        :rtype: (dict[(str, int, int), Var], tuplelist, tuplelist)
        :return : (all variables, states, actions)
        """
        variables = {}
        states = tuplelist()
        actions = tuplelist()

        for v in self.problem.variables:
            for k in range(self.num_futures):
                for t in range(self.problem.horizon):
                    lp_var = self.model.addVar(vtype=GRB.BINARY,
                                               name='%s^%d^%d' % (v, k, t))
                    variables[v, k, t] = lp_var
                    states.append((v, k, t))

        for a in self.problem.actions:
            for k in range(self.num_futures):
                for t in range(self.problem.horizon):
                    lp_var = self.model.addVar(vtype=GRB.BINARY,
                                               name='%s^%d^%d' % (a, k, t))
                    variables[a, k, t] = lp_var
                    actions.append((a, k, t))

        self.model.update()
        logger.info('added_variables|num_vars=%d' % len(variables))
        return variables, states, actions

    def add_fixed_constrs(self):
        self.add_concurrency_constrs()
        self.add_init_actions_constrs()
        self.add_reward_constrs()

    def add_concurrency_constrs(self):
        max_concurrency = self.problem.max_concurrency

        if max_concurrency == len(self.problem.actions):
            return

        for k in range(self.num_futures):
            for t in range(self.problem.horizon):
                s = quicksum([self.all_vars[a]
                              for a in self.actions.select('*', k, t)])
                constr = self.model.addConstr(s <= max_concurrency, 'maxcon:{}^{}'.format(k, t))
                self.constrs['concurrency'].append(constr)

        logger.info('added_max_concurrency_constraints')

    def add_init_actions_constrs(self):
        for a in self.problem.actions:
            first_actions = self.actions.select(a, '*', 0)
            for i in range(len(first_actions) - 1):
                a1 = self.all_vars[first_actions[i]]
                a2 = self.all_vars[first_actions[i + 1]]
                constr_name = 'init-act:{}^{}'.format(a, i)
                constr = self.model.addConstr(a1 == a2, name=constr_name)
                self.constrs['init_actions'].append(constr)

        logger.info('added_hop_action_constraints')

    def add_reward_constrs(self):
        logger.warn('add_reward_constrs is not implemented by subclass %s' % self.__class__.__name__)

    def set_init_states_constraints(self):
        for constr in self.constrs['init_states']:
            self.model.remove(constr)
        self.constrs['init_states'] = []

        first_states = self.states.select('*', '*', 0)
        init_values = self.problem.variables

        for v in first_states:
            init_value = init_values[v[0]]
            constr_name = 'init:{}^{}'.format(v[0], v[1])
            constr = self.model.addConstr(self.all_vars[v] == init_value, name=constr_name)
            self.constrs['init_states'].append(constr)

    def set_transition_constrs(self):
        logger.warn('set_transition_constrs is not implemented by subclass %s' % self.__class__.__name__)

