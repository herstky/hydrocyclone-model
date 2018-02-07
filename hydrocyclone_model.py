import math
import numpy as np

np.set_printoptions(suppress=True)

rF = 163.0 #gpm
rPD = 21.0 #psid

number_of_stages = 3
number_of_cleaners = [1, 1, 1]

# consistencies are listed as mass fractions
F_cons = [.01, .009, .0125]
A_cons = [.0083, .008, .0097]
R_cons = [.0232, .0242, .0333]

# pressures are in psi
F_pres = [34.5, 36.7, 38]
A_pres = [12, 11.1, 16.3]
R_pres = [12.8, 11.1, 16.3]

# flow rates are in gpm. assign placeholder values
F_flow = [0] * number_of_stages
A_flow = [0] * number_of_stages
R_flow = [0] * number_of_stages

flow_factor = math.sqrt(rF / rPD)

#rounded_feed_flow = round(feed_flow(0), 2)
#print('\nFeed flow =', rounded_feed_flow, 'gpm\n')

#calculate all flowrates in stage i
def stage_flow(i):
	actual_PD = F_pres[i] - A_pres[i]
	F_flow[i] = number_of_cleaners[i] * (math.sqrt(actual_PD)  * flow_factor) ** 2
	A = np.array([[1, 1], [A_cons[i], R_cons[i]]])
	B = np.array([F_flow[i], F_cons[i] * F_flow[i]])
	X = np.linalg.solve(A, B)
	return(X)
  
# run flow calculation for each stage
for i in range(0, number_of_stages):
	A_flow[i] = stage_flow(i)[0]
	R_flow[i] = stage_flow(i)[1]
  
print(F_flow)
print(A_flow)
print(R_flow)




