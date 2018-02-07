# To do:
# implement whitewater (pull?) flow
# implement troubleshoot mode with incremental consistency adjustment
# include mass flows

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

WW_cons = .0002
WW_flow = [0] * (number_of_stages - 1) # WW_flow dilutes rejects of corresponding stage. no dilution on final stage

flow_factor = math.sqrt(rF / rPD)

#rounded_feed_flow = round(feed_flow(0), 2)
#print('\nFeed flow =', rounded_feed_flow, 'gpm\n')

#calculate all flowrates in stage i. returns a matrix where index 0 corresponds to accepts and 1 to rejects
def stage_flow(i):
	actual_PD = F_pres[i] - A_pres[i]
	F_flow[i] = number_of_cleaners[i] * (math.sqrt(actual_PD)  * flow_factor) ** 2
	A = np.array([[1, 1], [A_cons[i], R_cons[i]]])
	B = np.array([F_flow[i], F_cons[i] * F_flow[i]])
	X = np.linalg.solve(A, B)
	A_flow[i] = X[0]
	R_flow[i] = X[1]
	return(X)
  
# run flow calculation for each stage. maps stage_flow calculations to corresponding lists
for i in range(0, number_of_stages):
	stage_flow(i)
  
print(F_flow)
print(A_flow)
print(R_flow)

# whitewater: reject flow and consistencies are known. whitewater consisency will be given. whitewater flow calculated from reject consistency and feed consistency to following stage
# example: reject mass fraction = 0.03, reject flow = 19 gpm, next stage feed mass fraction = .012, feed flow = 170 gpm, whitewater mass fraction = 0.0002. 

# R1_flow + WW_flow = F2_flow 
# R1_flow * R1_cons + WW_flow * WW_cons = F2_flow * F2_cons <-- this overdefines the system(?)
# WW_flow = (F2_flow * F2_cons - R1_flow * R1_cons) / WW_cons 


for i in range(0, number_of_stages - 1):
	WW_flow[i] = F_flow[i + 1] - R_flow[i]

print(WW_flow)





