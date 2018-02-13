#To do:
#System info sheet. break sheets into tabs?
#consistency wizard

import sys
import math
import numpy as np
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit, QFrame, QGridLayout, QLabel, QInputDialog
from PyQt5.QtGui import *

np.set_printoptions(suppress=True) #converts numbers from scientific to standard notation

#consistencies are in %
field_cons = {}
consistencies = {}

#pressures are in psi
field_pres = {}
pressures = {}

number_of_stages = 2

#reference cleaner values
rF = 163.0 #gpm
rPD = 21.0 #psid

number_of_cleaners = [1] * number_of_stages #update this 

# flow rates are in gpm. assign placeholder values
F_flow = [0] * number_of_stages
A_flow = [0] * number_of_stages
R_flow = [0] * number_of_stages

WW_cons = .0002
WW_flow = [0] * (number_of_stages - 1) # WW_flow dilutes rejects of corresponding stage. no dilution on final stage

flow_factor = math.sqrt(rF / rPD)

def foo():
    print("bar")

def stage_flow(i):
    #!!THIS DOESNT TAKE WW INTO ACCOUNT!!
    #print(consistencies['{}F'.format(i + 1)])
    actual_PD = pressures['{}F'.format(i + 1)] - pressures['{}A'.format(i + 1)]
    #print(actual_PD)
    F_flow[i] = number_of_cleaners[i] * (math.sqrt(actual_PD) * flow_factor) ** 2
    A = np.array([[1, 1], [consistencies['{}A'.format(i + 1)], consistencies['{}R'.format(i + 1)]]])
    B = np.array([F_flow[i], consistencies['{}F'.format(i + 1)] * F_flow[i]])
    #print(A, B)
    X = np.linalg.solve(A, B)
    A_flow[i] = X[0]
    R_flow[i] = X[1]

    if i < number_of_stages - 1:
        WW_flow[i] = F_flow[i + 1] - R_flow[i]
    
    return()

def calculate_flow():
    for i in range(0, number_of_stages):
        stage_flow(i)
        print(F_flow[i])
        print(A_flow[i])
        print(R_flow[i])
        if i < number_of_stages - 1:
            print(WW_flow[i])

class hydrocyclones(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
    
    @staticmethod  
    def calculate():
    
        try:
            for i in range(0, number_of_stages):
                #print(float(field_cons['{}F'.format(i + 1)].text()) + 1)
                consistencies.update({'{}F'.format(i + 1): float(field_cons['{}F'.format(i + 1)].text()), 
                    '{}A'.format(i + 1): float(field_cons['{}A'.format(i + 1)].text()), '{}R'.format(i + 1): float(field_cons['{}R'.format(i + 1)].text())})
                pressures.update({'{}F'.format(i + 1): float(field_pres['{}F'.format(i + 1)].text()), 
                    '{}A'.format(i + 1): float(field_pres['{}A'.format(i + 1)].text()), '{}R'.format(i + 1): float(field_pres['{}R'.format(i + 1)].text())})
                #print(pressures['{}A'.format(i + 1)])
        except(ValueError): 
            print("Please enter a value in each field")


    def initUI(self):

        sys_info_title = QLabel('System Info:')
        cons_title = QLabel('Consistencies (%):')
        pres_title = QLabel('Pressures (psi):')
        calculate_button = QPushButton('Calculate')


        sys_grid = QGridLayout()
        cons_grid = QGridLayout()
        pres_grid = QGridLayout()


        for i in range(0, number_of_stages):
            field_cons.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): QLineEdit(), '{}R'.format(i + 1): QLineEdit()})
            cons_grid.addWidget(field_cons['{}F'.format(i + 1)], i, 1)
            cons_grid.addWidget(field_cons['{}A'.format(i + 1)], i, 3)
            cons_grid.addWidget(field_cons['{}R'.format(i + 1)], i, 5)
            
            cons_feed_label = QLabel('{}F ='.format(i + 1))
            cons_accepts_label = QLabel('{}A ='.format(i + 1))
            cons_rejects_label = QLabel('{}R ='.format(i + 1))
            cons_grid.addWidget(cons_feed_label, i, 0)
            cons_grid.addWidget(cons_accepts_label, i, 2)
            cons_grid.addWidget(cons_rejects_label, i, 4)

            field_pres.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): QLineEdit(), '{}R'.format(i + 1): QLineEdit()})
            pres_grid.addWidget(field_pres['{}F'.format(i + 1)], i, 1)
            pres_grid.addWidget(field_pres['{}A'.format(i + 1)], i, 3)
            pres_grid.addWidget(field_pres['{}R'.format(i + 1)], i, 5)            

            pres_feed_label = QLabel('{}F ='.format(i + 1))
            pres_accepts_label = QLabel('{}A ='.format(i + 1))
            pres_rejects_label = QLabel('{}R ='.format(i + 1))
            pres_grid.addWidget(pres_feed_label, i, 0)
            pres_grid.addWidget(pres_accepts_label, i, 2)
            pres_grid.addWidget(pres_rejects_label, i, 4)
        

        data_hbox = QHBoxLayout() #outermost box
        sys_info_vbox = QVBoxLayout()
        cons_vbox = QVBoxLayout()
        calc_hbox = QHBoxLayout()
        pres_vbox = QVBoxLayout()

        data_hbox.addLayout(sys_info_vbox)
        data_hbox.addLayout(cons_vbox)
        data_hbox.addLayout(pres_vbox)
        data_hbox.addStretch(1) #not sure what his does. need to push boxes left

        sys_info_vbox.addWidget(sys_info_title)
        sys_info_vbox.addLayout(sys_grid)
        sys_info_vbox.addStretch(1)
        sys_info_vbox.setContentsMargins(0, 0, 20, 0)

        cons_vbox.addWidget(cons_title) #vertical box containing consistency table
        cons_vbox.addLayout(cons_grid)
        cons_vbox.addLayout(calc_hbox)
        cons_vbox.addStretch(1) #pushes consistency table and calculate button upward when resizing window
        cons_vbox.setContentsMargins(20, 0, 20, 0)

        pres_vbox.addWidget(pres_title) #vertical box containing pressure table
        pres_vbox.addLayout(pres_grid)
        pres_vbox.addStretch(1) #pushes pressure table upward when resizing window
        pres_vbox.setContentsMargins(20, 0, 0, 0)
        
        calc_hbox.addWidget(calculate_button) #box for calculate button
        calc_hbox.addStretch(1)
  
        self.setLayout(data_hbox)


        calculate_button.clicked.connect(self.calculate)
        calculate_button.clicked.connect(calculate_flow)

        
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Data Table')
        self.show()


#if __name__ == '__main__':
app = QApplication(sys.argv)
ex1 = hydrocyclones()
sys.exit(app.exec())