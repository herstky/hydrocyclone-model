#To do:
#System info sheet. break sheets into tabs?
#consistency wizard
#generate report button: create report with info on each stage and recommendations based on reject rates, backflows, PD, etc.
#mass balance

import sys
import math
import numpy as np
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit, QFrame, QGridLayout, QLabel, QInputDialog, QComboBox
from PyQt5.QtGui import *

np.set_printoptions(suppress=True) #converts numbers from scientific to standard notation

cleaner_models = []

class hydrocyclones():
    def __init__(self, model, reference_flow, reference_PD): #maybe add optional arguments for ideal RRV and RRW range

        self.model = model
        self.reference_flow = reference_flow
        self.reference_PD = reference_PD

        cleaner_models.append(self.model)


CLP_700 = hydrocyclones('CLP 700', 163, 21) #check reference sheets. store these in different file
CLP_350 = hydrocyclones('CLP 350', 135, 21) 
posiflow = hydrocyclones('Posiflow', 70, 20)


class gui(QWidget):

    def __init__(self):

        super().__init__()
        
        self.number_of_stages = self.get_number_of_stages()
        
        self.field_cons = {}
        self.consistencies = {} #consistencies are entered as percentages then converted to decimals before being stored in this dictionary

        #pressures are in psi
        self.field_pres = {}
        self.pressures = {}

        #reference cleaner values. should make this a dropdown that will allow users to create custom cleaner styles that are stored in a file
        self.reference_flow = 163.0 #gpm
        self.reference_PD = 21.0 #psid                     

        self.comboBox = [0] * self.number_of_stages

        # flow rates are in gpm. assign placeholder values
        self.F_flow = [0] * self.number_of_stages
        self.A_flow = [0] * self.number_of_stages
        self.R_flow = [0] * self.number_of_stages

        self.field_number_of_cleaners = {}
        self.number_of_cleaners = {} 

        #WW_flow dilutes rejects of corresponding stage. no dilution on final stage
        self.WW_flow = [0] * (self.number_of_stages - 1) 

        #flow factor is a proportionality constant specific to each cleaner that is used to calculate flow from PD
        self.flow_factor = math.sqrt(self.reference_flow / self.reference_PD) 

        self.initUI()
    

    def get_number_of_stages(self):

        stages = ('1', '2', '3', '4', '5', '6', '7')
        self.num, ok = QInputDialog.getItem(self, 'Setup', 'Number of stages:', stages, 0, False)
        if ok and self.num:
            return(int(self.num))
        else:
            app.exec()


    #fetches data from user entry fields, converts it from strings to floats, and maps to dictionaries that are used for calculations
    def calculate(self):

        try:
            self.consistencies.update({'WW': float(self.field_cons['WW'].text()) / 100})

            for i in range(0, self.number_of_stages):
                self.number_of_cleaners.update({'stage {}'.format(i + 1): 
                int(self.field_number_of_cleaners['stage {}'.format(i + 1)].text())})

                self.consistencies.update({'{}F'.format(i + 1): 
                float(self.field_cons['{}F'.format(i + 1)].text()) / 100, '{}A'.format(i + 1): 
                float(self.field_cons['{}A'.format(i + 1)].text()) / 100, '{}R'.format(i + 1): 
                float(self.field_cons['{}R'.format(i + 1)].text()) / 100})
                
                self.pressures.update({'{}F'.format(i + 1): 
                float(self.field_pres['{}F'.format(i + 1)].text()), '{}A'.format(i + 1): 
                float(self.field_pres['{}A'.format(i + 1)].text()), '{}R'.format(i + 1): 
                float(self.field_pres['{}R'.format(i + 1)].text())})

                self.stage_flow_calc(i)

                print('{}F Flow = '.format(i + 1), self.F_flow[i], ' gpm')
                print('{}A Flow = '.format(i + 1), self.A_flow[i], ' gpm')
                print('{}R Flow = '.format(i + 1), self.R_flow[i], ' gpm')

            for i in range(0, self.number_of_stages):
                if i < self.number_of_stages - 1:
                    self.WW_flow_calc(i)
                    print('{}WW Flow = '.format(i + 1), self.WW_flow[i], ' gpm')

        except(ValueError): #request data if any fields are left blank. needs to be a message box.
            print('Please enter a value in each field')


    def stage_flow_calc(self, i):

        self.actual_PD = self.pressures['{}F'.format(i + 1)] - self.pressures['{}A'.format(i + 1)]
        self.F_flow[i] = self.number_of_cleaners['stage {}'.format(i + 1)] * (math.sqrt(self.actual_PD) * self.flow_factor) ** 2
        self.A = np.array([[1, 1], [self.consistencies['{}A'.format(i + 1)], self.consistencies['{}R'.format(i + 1)]]])
        self.B = np.array([self.F_flow[i], self.consistencies['{}F'.format(i + 1)] * self.F_flow[i]])
        self.X = np.linalg.solve(self.A, self.B)
        self.A_flow[i] = self.X[0]
        self.R_flow[i] = self.X[1]
    


    def WW_flow_calc(self, i):

        if i < self.number_of_stages - 1:
            if i < self.number_of_stages -2:
                self.WW_flow[i] = self.F_flow[i + 1] - self.R_flow[i] - self.A_flow[i + 2]
            else:
                self.WW_flow[i] = self.F_flow[i + 1] - self.R_flow[i] 


    def initUI(self):

        sys_info_title = QLabel('System Info:')
        cons_title = QLabel('Consistencies (%):')
        pres_title = QLabel('Pressures (psi):')
        calculate_button = QPushButton('Calculate')

        sys_grid = QGridLayout()
        cons_grid = QGridLayout()
        pres_grid = QGridLayout()


        #add number of cleaners per stage to system info
        for i in range(0, self.number_of_stages):
            number_of_cleaners_label = QLabel('Cleaners in stage {} ='.format(i + 1))
            sys_grid.addWidget(number_of_cleaners_label, i + 1, 0)

            self.field_number_of_cleaners.update({'stage {}'.format(i + 1): QLineEdit()})
            sys_grid.addWidget(self.field_number_of_cleaners['stage {}'.format(i + 1)], i + 1, 1)

            self.comboBox[i] = QComboBox()
            for cleaner_model in cleaner_models:
                self.comboBox[i].addItem(cleaner_model)
            sys_grid.addWidget(self.comboBox[i], i + 1, 2) 




        #this loop maps fields to a dictionary of consistency and pressure values and adds them to the corresponding grids
        for i in range(0, self.number_of_stages):
            cons_feed_label = QLabel('{}F ='.format(i + 1)) #create label
            cons_accepts_label = QLabel('{}A ='.format(i + 1))
            cons_rejects_label = QLabel('{}R ='.format(i + 1))

            cons_grid.addWidget(cons_feed_label, i, 0) #add label to grid
            cons_grid.addWidget(cons_accepts_label, i, 2)
            cons_grid.addWidget(cons_rejects_label, i, 4)

            self.field_cons.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): 
            QLineEdit(), '{}R'.format(i + 1): QLineEdit()}) #maps fields to a dictionary
            cons_grid.addWidget(self.field_cons['{}F'.format(i + 1)], i, 1) #add field to grid
            cons_grid.addWidget(self.field_cons['{}A'.format(i + 1)], i, 3)
            cons_grid.addWidget(self.field_cons['{}R'.format(i + 1)], i, 5)
            
            pres_feed_label = QLabel('{}F ='.format(i + 1))
            pres_accepts_label = QLabel('{}A ='.format(i + 1))
            pres_rejects_label = QLabel('{}R ='.format(i + 1))
            pres_grid.addWidget(pres_feed_label, i, 0)
            pres_grid.addWidget(pres_accepts_label, i, 2)
            pres_grid.addWidget(pres_rejects_label, i, 4)

            self.field_pres.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): 
            QLineEdit(), '{}R'.format(i + 1): QLineEdit()})
            pres_grid.addWidget(self.field_pres['{}F'.format(i + 1)], i, 1)
            pres_grid.addWidget(self.field_pres['{}A'.format(i + 1)], i, 3)
            pres_grid.addWidget(self.field_pres['{}R'.format(i + 1)], i, 5)            


        #create label, map field to dictionary, and add field to grid for WW consistency
        cons_grid.addWidget(QLabel('WW ='), self.number_of_stages, 0) 
        self.field_cons.update({'WW': QLineEdit()})
        cons_grid.addWidget(self.field_cons['WW'], self.number_of_stages, 1)

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

        
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Data Table')
        self.show()


#if __name__ == '__main__':
app = QApplication(sys.argv)
gui = gui()
sys.exit(app.exec())