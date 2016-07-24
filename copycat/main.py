from gurobipy import *

if __name__ == "__main__":
	try:
		m = Model("mip1")

		x = m.addVar(vtype=GRB.BINARY, name="x")
		y = m.addVar(vtype=GRB.BINARY, name="y")
		z = m.addVar(vtype=GRB.BINARY, name="z")

		m.setObjective(x + y + 2*z, GRB.MAXIMIZE)

		m.addConstr(x + 2*y + 3*z <= 4, "c0")
		m.addConstr(x + y >= 1, "c1")

		m.optimize()

		for v in m.getVars():
			print(v.varName, v.x)

		print('Obj: ', m.objVal)
	except GurobiError as e:
		print("Error:", e)
