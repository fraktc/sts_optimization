# Facility Location Problem using Mixed Integer Linear Programming (MILP)

from pulp import *

# Data
warehouses = [1, 2, 3]
customers = [1, 2, 3, 4]

opening_cost = {1: 500, 2: 400, 3: 600}
capacity = {1: 70, 2: 50, 3: 80}
demand = {1: 30, 2: 20, 3: 40, 4: 10}
service_cost = {
    (1,1):10, (1,2):24, (1,3):18, (1,4):30,
    (2,1):14, (2,2):16, (2,3):20, (2,4):22,
    (3,1):16, (3,2):20, (3,3):14, (3,4):26
}




# Problem

model = LpProblem("Facility_Location", LpMinimize)

# Decision Variables


#y_j  = 1 if warehouse j is opened, 0 otherwise.
y = LpVariable.dicts("OpenWarehouse", warehouses, 0,1 , LpBinary)


#x_ij  = 1 if customer i is assigned to warehouse j , 0 otherwise.
x = LpVariable.dicts("Assign", [(i,j) for i in customers for j in warehouses ], 0,1 ,LpBinary)

# Objective


# Minimize Z =  Sum_j {Opening_cost_j}*y_j + Sum_i Sum_j ServiceCost{i,j}*x_i,j


model += lpSum(opening_cost[j]*y[j] for j in warehouses) + lpSum(service_cost[(j,i)]*x[(i,j)] for i in customers for j in warehouses)


# Constraints



# 3.1 Each customer must be assigned to one warehouse
# Sum{j} X_i,j = 1, for all i.

for i in customers:
    model += lpSum(x[(i,j)] for j in warehouses) ==1

# 3.2 Customer can only be assigned to open warehouse
# x_ij<= y_j , for i,j.

for i in customers:
    for j in warehouses:
        model += x[(i,j)] <= y[j]

# 3.3 Respect warehouse capacities

# Sum_i Demand_i * x_ij <= Capacity_j * y_j , for_all j.

for j in warehouses:
    model += lpSum(demand[i]*x[(i,j)] for i in customers) <= capacity[j]*y[j]


# Solve

model.solve()

# Results:

print(f"Status: {LpStatus[model.status]}")

for j in warehouses:
    print(f"Warehouse {j} open: {int(value(y[j]))}")

for i in customers:
    for j in warehouses:
        if value(x[(i,j)]) > 0.5:
            print(f"Customer {i} assigned to warehouse {j}")
        
print(f"Total cost = {value(model.objective)}")




