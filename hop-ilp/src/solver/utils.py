from gurobipy import LinExpr


def add_and_constraints(model, xs, z, name=""):
    """
    Adds and returns constraints to Gurobi model such that z is equivalent
    to the logic AND of variables in sx using the rule:
    * nz <= (x1 + x2 + ... + xn) <= (n - 1) + z

    :param model: Gurobi model
    :param xs: list of (variable, sign)
    :param z:
    :param name: constraints' prefix
    """
    sum_expr = LinExpr()
    for x, sign in xs:
        if sign == 1:
            sum_expr += x
        elif sign == -1:
            sum_expr += (1 - x)

    n = len(xs)
    name_lb = "{}_lb".format(name) if name else ""
    name_ub = "{}_ub".format(name) if name else ""
    model.addConstr(n * z <= sum_expr, name_lb)
    model.addConstr(sum_expr <= (n - 1) + z, name_ub)
