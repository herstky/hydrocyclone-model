import math
import tkinter

#need to update python

rF = 163.0 #gpm
rPD = 21.0 #psid
number_of_cleaners = 1
# request user input for cleaner style or manual reference data. use CLP 700 as default

consistencies = dict()
pressures = dict()

# consistencies are listed as %
consistencies['F1'] = 1.00
consistencies['A1'] = 0.83
consistencies['R1'] = 2.32
consistencies['F2'] = 0.90
consistencies['A2'] = 0.80
consistencies['R2'] = 2.42
consistencies['F3'] = 1.25
consistencies['A3'] = 0.97
consistencies['R3'] = 3.33

# pressures are in psi
pressures['F1'] = 34.5
pressures['A1'] = 14.0
pressures['R1'] = 12.8
pressures['F2'] = 36.7
pressures['A2'] = 11.1
pressures['R2'] = 13.5
pressures['F3'] = 38.0
pressures['A3'] = 16.3
pressures['R3'] = 10.4

# aFF = ((aPD)^(1/2)*((rFF)^(1/2)/(rPD)^(1/2)))^(2)

# 1/2 is evaluated as an integer. need to update to python 3.x to get expected results
flow_factor = math.sqrt(rF / rPD)

def feed_flow(actual_feed_pressure, actual_accept_pressure):
  actual_PD = actual_feed_pressure - actual_accept_pressure
  flow = number_of_cleaners * (math.sqrt(actual_PD)  * flow_factor) ** 2
  return(flow)

rounded_feed_flow = round(feed_flow(pressures['F1'], pressures['A1']), 2)
print('\nFeed flow =', rounded_feed_flow, 'gpm\n')


