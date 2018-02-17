#To do:
#System info sheet. break sheets into tabs?
#consistency wizard
#generate report button: create report with info on each stage and recommendations based on reject rates, backflows, PD, etc.
#mass balance

import sys
import math
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

np.set_printoptions(suppress=True) #converts numbers from scientific to standard notation (numpy)


def stage_flow_calc(i):
    #pressure drop = feed pressure - accept pressure
    actual_PD = window.pressures['{}F'.format(i + 1)] - window.pressures['{}A'.format(i + 1)]
    
    #feed flow to a cleaner = (sqrt(pressure drop) * sqrt((reference flowrate) / (reference pressure drop))) ^ 2
    window.F_flow[i] = window.number_of_cleaners['stage {}'.format(i + 1)] * (math.sqrt(actual_PD) * 
    hydrocyclones.flow_dict[window.cleaner_model_in_stage]) ** 2 
    
    A = np.array([[1, 1], [window.consistencies['{}A'.format(i + 1)], window.consistencies['{}R'.format(i + 1)]]])
    B = np.array([window.F_flow[i], window.consistencies['{}F'.format(i + 1)] * window.F_flow[i]])
    X = np.linalg.solve(A, B)
    window.A_flow[i] = X[0]
    window.R_flow[i] = X[1]

def WW_flow_calc(i):
    #feed to each stage is diluted by whitewater and the accepts flow from the following stage
    if i < window.number_of_stages - 1:
        if i < window.number_of_stages - 2:
            window.WW_flow[i] = window.F_flow[i + 1] - window.R_flow[i] - window.A_flow[i + 2]
        else:
            window.WW_flow[i] = window.F_flow[i + 1] - window.R_flow[i] 

#add functionality for reverse, combicleaners, and FRUs if possible.
class hydrocyclones():

    cleaner_models = []
    flow_dict = {}

    def __init__(self, model, reference_flow, reference_PD): #maybe add optional arguments for ideal RRV and RRW range
        self.model = model
        self.reference_flow = reference_flow
        self.reference_PD = reference_PD
        self.reference_data = [self.reference_flow, self.reference_PD]
        self.flow_factor = math.sqrt(self.reference_flow / self.reference_PD)
        
        hydrocyclones.flow_dict.update({self.model: self.flow_factor}) 
        hydrocyclones.cleaner_models.append([self.model])

CLP_700 = hydrocyclones('CLP 700', 163, 21) #check reference sheets. store these in a seperate file and make it possible to add custome models
CLP_350 = hydrocyclones('CLP 350', 135, 21) 
posiflow = hydrocyclones('Posiflow', 70, 20)


class gui(QWidget):

    def __init__(self):
        super().__init__()
        
        self.number_of_stages = self.get_number_of_stages()
        
        self.cleaner_model_in_stage = [0] * self.number_of_stages #list of cleaner models used in each stage

        #consistencies are entered as percentages then converted to decimals before being stored in this dictionary
        self.field_cons = {}
        self.consistencies = {} 

        #pressures are in psi
        self.field_pres = {}
        self.pressures = {}                    

        self.model_dropdown = [0] * self.number_of_stages

        # flow rates are in gpm. assign placeholder values
        self.F_flow = [0] * self.number_of_stages
        self.A_flow = [0] * self.number_of_stages
        self.R_flow = [0] * self.number_of_stages

        self.field_number_of_cleaners = {}
        self.number_of_cleaners = {} 

        #WW_flow dilutes rejects of corresponding stage. no dilution on final stage
        self.WW_flow = [0] * (self.number_of_stages - 1) 

        self.initUI()
    
    #dropdown menu to select number of stages. gets called before window is created
    def get_number_of_stages(self):
        stages = ('1', '2', '3', '4', '5', '6', '7')
        self.num, ok = QInputDialog.getItem(self, 'Setup', 'Number of stages:', stages, 0, False)
        if ok and self.num:
            return(int(self.num))
        else:
            app.exec()


    #called when "caclulate button is pressed. gets data from user entry fields, converts it from strings to floats, and maps 
    #to dictionaries that are used for calculations. calls calculation functions
    def calculate(self):
        try:
            self.consistencies.update({'WW': float(self.field_cons['WW'].text()) / 100})

            for i in range(self.number_of_stages):
                self.number_of_cleaners.update({'stage {}'.format(i + 1): 
                int(self.field_number_of_cleaners['stage {}'.format(i + 1)].text())})

                self.cleaner_model_in_stage = str(self.model_dropdown[i].currentText())

                self.consistencies.update({'{}F'.format(i + 1): float(self.field_cons['{}F'.format(i + 1)].text()) / 100, 
                '{}A'.format(i + 1): float(self.field_cons['{}A'.format(i + 1)].text()) / 100, 
                '{}R'.format(i + 1): float(self.field_cons['{}R'.format(i + 1)].text()) / 100})
                
                self.pressures.update({'{}F'.format(i + 1): float(self.field_pres['{}F'.format(i + 1)].text()),
                '{}A'.format(i + 1): float(self.field_pres['{}A'.format(i + 1)].text()), 
                '{}R'.format(i + 1): float(self.field_pres['{}R'.format(i + 1)].text())})

                stage_flow_calc(i)

                print('{}F Flow ='.format(i + 1), self.F_flow[i], 'gpm')
                print('{}A Flow ='.format(i + 1), self.A_flow[i], 'gpm')
                print('{}R Flow ='.format(i + 1), self.R_flow[i], 'gpm')

            for i in range(self.number_of_stages):
                if i < self.number_of_stages - 1:
                    WW_flow_calc(i)
                    print('{}WW Flow ='.format(i + 1), self.WW_flow[i], 'gpm')

        except(ValueError): #request data if any fields are left blank. needs to be a message box.
            print('Please enter a value in each field')


    def initUI(self):
        self.sys_info_title = QLabel('System Info:')
        self.cons_title = QLabel('Consistencies (%):')
        self.pres_title = QLabel('Pressures (psi):')
        self.calculate_button = QPushButton('Calculate')

        self.sys_grid = QGridLayout()
        self.cons_grid = QGridLayout()
        self.pres_grid = QGridLayout()

        #adds labels and fields for number of cleaners and cleaner models for each stage
        for i in range(self.number_of_stages):
            self.number_of_cleaners_label = QLabel('Cleaners in stage {} ='.format(i + 1))
            self.sys_grid.addWidget(self.number_of_cleaners_label, i + 1, 0)

            self.field_number_of_cleaners.update({'stage {}'.format(i + 1): QLineEdit()})
            self.sys_grid.addWidget(self.field_number_of_cleaners['stage {}'.format(i + 1)], i + 1, 1)

            self.model_dropdown[i] = QComboBox()
            for hydrocyclones.cleaner_model in hydrocyclones.cleaner_models:
                self.model_dropdown[i].addItem(hydrocyclones.cleaner_model[0]) #0th item in list refers to cleaner model
            
            self.sys_grid.addWidget(self.model_dropdown[i], i + 1, 2) 

        #this loop maps fields to a dictionary of consistency and pressure values and adds them to the corresponding grids
        for i in range(self.number_of_stages):
            self.cons_feed_label = QLabel('{}F ='.format(i + 1)) #create labels
            self.cons_accepts_label = QLabel('{}A ='.format(i + 1))
            self.cons_rejects_label = QLabel('{}R ='.format(i + 1))

            self.cons_grid.addWidget(self.cons_feed_label, i, 0) #add labels to grid
            self.cons_grid.addWidget(self.cons_accepts_label, i, 2)
            self.cons_grid.addWidget(self.cons_rejects_label, i, 4)

            self.field_cons.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): 
            QLineEdit(), '{}R'.format(i + 1): QLineEdit()}) #maps fields to a dictionary
            self.cons_grid.addWidget(self.field_cons['{}F'.format(i + 1)], i, 1) #add fields to grid
            self.cons_grid.addWidget(self.field_cons['{}A'.format(i + 1)], i, 3)
            self.cons_grid.addWidget(self.field_cons['{}R'.format(i + 1)], i, 5)
            
            self.pres_feed_label = QLabel('{}F ='.format(i + 1))
            self.pres_accepts_label = QLabel('{}A ='.format(i + 1))
            self.pres_rejects_label = QLabel('{}R ='.format(i + 1))
            self.pres_grid.addWidget(self.pres_feed_label, i, 0)
            self.pres_grid.addWidget(self.pres_accepts_label, i, 2)
            self.pres_grid.addWidget(self.pres_rejects_label, i, 4)

            self.field_pres.update({'{}F'.format(i + 1): QLineEdit(), '{}A'.format(i + 1): 
            QLineEdit(), '{}R'.format(i + 1): QLineEdit()})
            self.pres_grid.addWidget(self.field_pres['{}F'.format(i + 1)], i, 1)
            self.pres_grid.addWidget(self.field_pres['{}A'.format(i + 1)], i, 3)
            self.pres_grid.addWidget(self.field_pres['{}R'.format(i + 1)], i, 5)            


        #create label, map field to dictionary, and add field to grid for WW consistency
        self.cons_grid.addWidget(QLabel('WW ='), self.number_of_stages, 0) 
        self.field_cons.update({'WW': QLineEdit()})
        self.cons_grid.addWidget(self.field_cons['WW'], self.number_of_stages, 1)

        self.data_hbox = QHBoxLayout() #outermost box
        self.sys_vbox = QVBoxLayout()
        self.cons_vbox = QVBoxLayout()
        self.calc_hbox = QHBoxLayout()
        self.pres_vbox = QVBoxLayout()

        self.data_hbox.addLayout(self.sys_vbox)
 
        self.sys_vbox.addWidget(self.sys_info_title)
        self.sys_vbox.addLayout(self.sys_grid)
        self.sys_vbox.addStretch(1)
        self.sys_vbox.setContentsMargins(0, 0, 20, 0)

        self.data_hbox.addLayout(self.cons_vbox)
        self.data_hbox.addLayout(self.pres_vbox)
        self.data_hbox.addStretch(1) #not sure what his does. need to push boxes left

        self.cons_vbox.addWidget(self.cons_title) #vertical box containing consistency table
        self.cons_vbox.addLayout(self.cons_grid)
        self.cons_vbox.addLayout(self.calc_hbox)
        self.cons_vbox.addStretch(1) #pushes consistency table and calculate button upward when resizing window
        self.cons_vbox.setContentsMargins(20, 0, 20, 0)

        self.pres_vbox.addWidget(self.pres_title) #vertical box containing pressure table
        self.pres_vbox.addLayout(self.pres_grid)
        self.pres_vbox.addStretch(1) #pushes pressure table upward when resizing window
        self.pres_vbox.setContentsMargins(20, 0, 0, 0)
        
        self.calc_hbox.addWidget(self.calculate_button) #box for calculate button
        self.calc_hbox.addStretch(1)
  
        self.setLayout(self.data_hbox)

        self.calculate_button.clicked.connect(self.calculate)
        
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Data Table')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = gui()
    sys.exit(app.exec())