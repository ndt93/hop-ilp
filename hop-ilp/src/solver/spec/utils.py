import re
from gurobipy import Model, Var, LinExpr, quicksum
from mrf.utils import is_set, count_set_bit, count_set_bits


def make_path(vars_list, bitmask):
    # type: (list[str]|list[Var], int) -> list[(list[str]|list[Var], int)]
    """
    Make a path i.e. list of (var, sign) from a list of variables and a bitmask.
    Each variable's sign corresponds to a bit in the bitmask going from LSB.
    """
    ret = []
    for i in range(len(vars_list)):
        if is_set(bitmask, i):
            ret.append((vars_list[i], 1))
        else:
            ret.append((vars_list[i], 0))
    return ret


def add_and_constraints(model, xs, z, name):
    # type: (Model, list[(Var, int)]|list[Var], float, str) -> object
    """
    Adds constraints to Gurobi model such that z is equivalent
    to the logic AND of variables in xs using the rule:
    * nz <= (x1 + x2 + ... + xn) <= (n - 1) + z
    :param model: Gurobi model
    :param xs: list of variables or (variable, sign)
    :param z:
    :param name: constraints' prefix
    """

    sum_expr = sum_vars(xs)

    n = len(xs)
    name_lb = "lb:{}".format(name) if name else ""
    name_ub = "ub:{}".format(name) if name else ""
    lb_cons = model.addConstr(n * z <= sum_expr, name_lb)
    up_cons = model.addConstr(sum_expr <= (n - 1) + z, name_ub)

    return lb_cons, up_cons


def add_or_constraints(model, xs, z, name):
    # type: (Model, list[(Var, int)]|list[Var], float, str) -> object
    """
    Adds and constraints to Gurobi model such that z is equivalent
    to the logic OR of variables in xs using the rule:
    * z <= (x1 + x2 + ... + xn) <= nz
    :param model: Gurobi model
    :param xs: list of variables or (variable, sign)
    :param z:
    :param name: constraints' prefix
    """

    sum_expr = sum_vars(xs)

    n = len(xs)
    name_lb = "lb:{}".format(name) if name else ""
    name_ub = "ub:{}".format(name) if name else ""
    lb_cons = model.addConstr(z <= sum_expr, name_lb)
    ub_cons = model.addConstr(sum_expr <= n * z, name_ub)

    return lb_cons, ub_cons


def sum_vars(xs):
    # type: (list[(Var, int)]|list[Var]) -> LinExpr()
    """
    Returns a Gurobi's LinExpr that represents the sum of variables in xs
    :param xs: list of variables or (variable, sign)
    """

    if len(xs) == 0:
        return LinExpr()

    if not isinstance(xs[0], tuple):
        return quicksum(xs)

    sum_expr = LinExpr()

    for x, sign in xs:
        if sign == 1:
            sum_expr += x
        elif sign == 0:
            sum_expr += (1 - x)

    return sum_expr


def get_rddl_list(line):
    list_str = line[line.index('{')+1:line.rindex('}')]
    return re.split(r'\W+', list_str.strip())


def get_rddl_assignment_val(rddl_str, t):
    # type: (str, type) -> t
    val_start = rddl_str.index('=') + 1
    val_end = rddl_str.rindex(';')
    return t(rddl_str[val_start:val_end])


def get_rddl_function_params(rddl_str, func_name):
    # type: (str, str) -> [str]
    params_match = re.search(r'%s\s*\((.*)\)' % (func_name,), rddl_str)
    params_str = params_match.group(1)
    return params_str.split(',')
