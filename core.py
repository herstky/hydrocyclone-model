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








class hydrocyclones(QWidget):

    def __init__(self):
        super().__init__()
        
        self.number_of_stages = self.get_number_of_stages()
        print(self.number_of_stages)
        
        self.field_cons = {}
        self.consistencies = {}

        #pressures are in psi
        self.field_pres = {}
        self.pressures = {}

        #reference cleaner values
        self.rF = 163.0 #gpm
        self.rPD = 21.0 #psid

        self.WW_cons = .0002                     

        # flow rates are in gpm. assign placeholder values
        self.F_flow = [0] * self.number_of_stages
        self.A_flow = [0] * self.number_of_stages
        self.R_flow = [0] * self.number_of_stages

        self.number_of_cleaners = [1] * self.number_of_stages #update this 

        self.WW_flow = [0] * (self.number_of_stages - 1) # WW_flow dilutes rejects of corresponding stage. no dilution on final stage

        self.flow_factor = math.sqrt(self.rF / self.rPD)

        self.initUI()
    
    #should this be a class method?


    def get_number_of_stages(self):

        stages = ("1", "2", "3", "4", "5", "6", "7")
        self.num, ok = QInputDialog.getItem(self, "Setup", "Number of stages:", stages, 0, False)
        if ok and self.num:
            return(int(self.num))
        else:
            app.exec()


    #this should probably be a class method
    # @staticmethod  
    def calculate(self):
        print(self)
        print(self.number_of_stages)
        try:
            for i in range(0, self.number_of_stages):
                #print(float(field_cons['{}F'.format(i + 1)].text()) + 1)
                self.consistencies.update({'{}F'.format(i + 1): float(self.field_cons['{}F'.format(i + 1)].text()), 
                    '{}A'.format(i + 1): float(self.field_cons['{}A'.format(i + 1)].text()), '{}R'.format(i + 1): float(self.field_cons['{}R'.format(i + 1)].text())})
                self.pressures.update({'{}F'.format(i + 1): float(self.field_pres['{}F'.format(i + 1)].text()), 
                    '{}A'.format(i + 1): float(self.field_pres['{}A'.format(i + 1)].text()), '{}R'.format(i + 1): float(self.field_pres['{}R'.format(i + 1)].text())})
                #print(pressures['{}A'.format(i + 1)])
        except(ValueError): 
            print("Please enter a value in each field")



    def foo():
        print("bar")

    def stage_flow(self, i):
        #!!THIS DOESNT TAKE WW OR ACCEPTS RECIRC INTO ACCOUNT!!
        #print(consistencies['{}F'.format(i + 1)])
        self.actual_PD = self.pressures['{}F'.format(i + 1)] - self.pressures['{}A'.format(i + 1)]
        #print(actual_PD)
        self.F_flow[i] = self.number_of_cleaners[i] * (math.sqrt(self.actual_PD) * self.flow_factor) ** 2
        self.A = np.array([[1, 1], [self.consistencies['{}A'.format(i + 1)], self.consistencies['{}R'.format(i + 1)]]])
        self.B = np.array([self.F_flow[i], self.consistencies['{}F'.format(i + 1)] * self.F_flow[i]])
        #print(A, B)
        self.X = np.linalg.solve(self.A, self.B)
        self.A_flow[i] = self.X[0]
        self.R_flow[i] = self.X[1]

        if i < self.number_of_stages - 1:
            self.WW_flow[i] = self.F_flow[i + 1] - self.R_flow[i]
        
        return()

    def calculate_flow(self):
        for i in range(0, self.number_of_stages):
            self.stage_flow(i)
            print(self.F_flow[i])
            print(self.A_flow[i])
            print(self.R_flow[i])
            if i < self.number_of_stages - 1:
                print(self.WW_flow[i])

 


    def initUI(self):

        

        sys_info_title = QLabel('System Info:')
        cons_title = QLabel('Consistencies (%):')
        pres_title = QLabel('Pressures (psi):')
        calculate_button = QPushButton('Calculate')


        sys_grid = QGridLayout()
        cons_grid = QGridLayout()
        pres_grid = QGridLayout()

        print(self.number_of_stages)
        for i in range(0, self.number_of_stages):
            self.field_cons.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): QLineEdit(), '{}R'.format(i + 1): QLineEdit()}) #map fields to a dictionary
            cons_grid.addWidget(self.field_cons['{}F'.format(i + 1)], i, 1)
            cons_grid.addWidget(self.field_cons['{}A'.format(i + 1)], i, 3)
            cons_grid.addWidget(self.field_cons['{}R'.format(i + 1)], i, 5)
            
            cons_feed_label = QLabel('{}F ='.format(i + 1))
            cons_accepts_label = QLabel('{}A ='.format(i + 1))
            cons_rejects_label = QLabel('{}R ='.format(i + 1))
            cons_grid.addWidget(cons_feed_label, i, 0)
            cons_grid.addWidget(cons_accepts_label, i, 2)
            cons_grid.addWidget(cons_rejects_label, i, 4)

            self.field_pres.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): QLineEdit(), '{}R'.format(i + 1): QLineEdit()})
            pres_grid.addWidget(self.field_pres['{}F'.format(i + 1)], i, 1)
            pres_grid.addWidget(self.field_pres['{}A'.format(i + 1)], i, 3)
            pres_grid.addWidget(self.field_pres['{}R'.format(i + 1)], i, 5)            

            pres_feed_label = QLabel('{}F ='.format(i + 1))
            pres_accepts_label = QLabel('{}A ='.format(i + 1))
            pres_rejects_label = QLabel('{}R ='.format(i + 1))
            pres_grid.addWidget(pres_feed_label, i, 0)
            pres_grid.addWidget(pres_accepts_label, i, 2)
            pres_grid.addWidget(pres_rejects_label, i, 4)
        
        cons_grid.addWidget(QLabel('WW ='), self.number_of_stages, 0)
        cons_grid.addWidget(QLineEdit(), self.number_of_stages, 1)

        data_hbox = QHBoxLayout() #outermost box
        sys_info_vbox = QVBoxLayout()
        cons_vbox = QVBoxLayout()
        calc_hbox = QHBoxLayout()
        pres_vbox = QVBoxLayout()

        data_hbox.addLayout(sys_info_vbox)
 

        sys_info_vbox.addWidget(sys_info_title)
        sys_info_vbox.addLayout(sys_grid)
        sys_info_vbox.addStretch(1)
        sys_info_vbox.setContentsMargins(0, 0, 20, 0)

        data_hbox.addLayout(cons_vbox)
        data_hbox.addLayout(pres_vbox)
        data_hbox.addStretch(1) #not sure what his does. need to push boxes left

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
        calculate_button.clicked.connect(self.calculate_flow)

        
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Data Table')
        self.show()


#if __name__ == '__main__':
app = QApplication(sys.argv)
ex1 = hydrocyclones()
sys.exit(app.exec())