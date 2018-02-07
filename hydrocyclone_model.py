import math
import numpy as np

np.set_printoptions(suppress=True)

rF = 163.0 #gpm
rPD = 21.0 #psid

number_of_cleaners = [1, 1, 1]

# consistencies are listed as mass fractions
F_cons = [.01, .009, .0125]
A_cons = [.0083, .008, .0097]
R_cons = [.0232, .0242, .0333]

# pressures are in psi
F_pres = [34.5, 36.7, 38]
A_pres = [12, 11.1, 16.3]
R_pres = [12.8, 11.1, 16.3]

# aFF = ((aPD)^(1/2)*((rFF)^(1/2)/(rPD)^(1/2)))^(2)

flow_factor = math.sqrt(rF / rPD)

#calculate the feed flow of stage i
def feed_flow(i):
  actual_PD = F_pres[i] - A_pres[i]
  flow = number_of_cleaners[i] * (math.sqrt(actual_PD)  * flow_factor) ** 2
  return(flow)

#rounded_feed_flow = round(feed_flow(0), 2)
#print('\nFeed flow =', rounded_feed_flow, 'gpm\n')

#calculate the accept and reject flows of stage i
def stage_flow(i):
  A = np.array([[1, 1], [A_cons[i], R_cons[i]]])
  B = np.array([feed_flow(i), F_cons[i] * feed_flow(i)])
  X = np.linalg.solve(A, B)
  return(X)
  
# flowrates are in gpm
F_flow = [feed_flow(0), feed_flow(1), feed_flow(2)]
A_flow = [stage_flow(0)[0], stage_flow(1)[0], stage_flow(2)[0]]
R_flow = [stage_flow(0)[1], stage_flow(1)[1], stage_flow(2)[1]]
  
print(F_flow)
print(A_flow)
print(R_flow)



