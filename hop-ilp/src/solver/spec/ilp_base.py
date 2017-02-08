from gurobipy import *
from logger import logger
import model.model
import utils


class ILPBase(object):
    constr_cats = ['init_states', 'init_actions', 'concurrency', 'transition', 'reward']

    def __init__(self, name, problem, num_futures, time_limit=None, debug=False):
        self.problem_name = name  # type: str
        self.problem = problem  # type: model.model.Model
        self.num_futures = num_futures  # type: int
        self.debug = debug  # type: bool

        self.constrs = {cat: [] for cat in self.constr_cats}  # type: dict[str, list[Constr]]
        self.transition_vars = []
        self.model = Model(name)

        if time_limit:
            self.model.params.timeLimit = time_limit

        if not debug:
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

        logger.info('added_init_actions_constraints')

    def add_reward_objective(self):
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

    def reset_transition_constrs(self):
        for constr in self.constrs['transition']:
            self.model.remove(constr)
        for v in self.transition_vars:
            self.model.remove(v)

        self.constrs['transition'] = []
        self.transition_vars = []

    def paths_to_transition_constrs(self, paths, k, h, v):
        # type: (list[list[(Var, int)]], int, int, str) -> None
        paths = self.str_paths_to_var_paths(paths, k, h - 1)
        path_fvars = []

        for path_idx, path in enumerate(paths):
            fvarname = 'f:{}^{}^{}^{}'.format(v, k, h, path_idx)
            fvar = self.model.addVar(vtype=GRB.BINARY, name=fvarname)
            path_fvars.append(fvar)
            self.model.update()
            constrs = utils.add_and_constraints(self.model, path, fvar, name=fvarname)
            self.constrs['transition'].extend(constrs)

        tvarname = 'fs:{}^{}^{}'.format(v, k, h)
        tvar = self.model.addVar(vtype=GRB.BINARY, name=tvarname)
        self.model.update()
        constrs = utils.add_or_constraints(self.model, path_fvars, tvar, name=tvarname)
        self.constrs['transition'].extend(constrs)

        next_state = self.all_vars[v, k, h]
        constr_name = 'transition:{}^{}^{}'.format(v, k, h)
        constr = self.model.addConstr(next_state == tvar, name=constr_name)
        self.constrs['transition'].append(constr)

        self.transition_vars.extend(path_fvars)
        self.transition_vars.append(tvar)

    def paths_to_reward_constrs(self, paths, leaves, k, h):
        # type: (list[list[(Var, int)]], list[float], int, int) -> None
        for i, (p, l) in enumerate(zip(paths, leaves)):
            coeff = 1. / self.num_futures * l
            name = 'w^{}^{}^{}'.format(k, h, i)
            w = self.model.addVar(vtype=GRB.BINARY, obj=coeff, name=name)
            self.model.update()

            constr_name = 'reward^{}^{}^{}'.format(k, h, i)
            utils.add_and_constraints(self.model, p, w, name=constr_name)

    def str_paths_to_var_paths(self, str_paths, k, h):
        return [self.str_path_to_var_path(p, k, h) for p in str_paths]

    def str_path_to_var_path(self, str_path, k, h):
        # type: (list[(str, int)], int, int) -> list[(Var, int)]
        return [(self.all_vars[v, k, h], s) for v, s in str_path]

