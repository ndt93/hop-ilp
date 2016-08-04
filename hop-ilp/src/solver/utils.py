from gurobipy import LinExpr, quicksum


def add_and_constraints(model, xs, z, name=""):
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
    name_lb = "{}_lb".format(name) if name else ""
    name_ub = "{}_ub".format(name) if name else ""
    model.addConstr(n * z <= sum_expr, name_lb)
    model.addConstr(sum_expr <= (n - 1) + z, name_ub)


def add_or_constraints(model, xs, z, name=""):
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
    name_lb = "{}_lb".format(name) if name else ""
    name_ub = "{}_ub".format(name) if name else ""
    model.addConstr(z <= sum_expr, name_lb)
    model.addConstr(sum_expr <= n * z, name_ub)


def sum_vars(xs):
    """
    Returns a Gurobi's LinExpr that represents the sum of variables in xs

    :param xs: list of variables or (variable, sign)
    """

    sum_expr = LinExpr()

    if len(xs) == 0:
        return sum_expr

    if isinstance(xs[0], tuple):
        for x, sign in xs:
            if sign == 1:
                sum_expr += x
            elif sign == -1:
                sum_expr += (1 - x)

        return sum_expr

    return quicksum(xs)
