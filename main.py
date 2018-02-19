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


np.set_printoptions(suppress = True) #converts numbers from scientific to standard notation (numpy)

def stage_key(stage_number, location = ''):
    return('stage {} {}'.format(stage_number, location))

#add functionality for reverse, combicleaners, and FRUs if possible.
class Hydrocyclones():

    cleaner_models = []
    flow_dict = {}

    def __init__(self, model, reference_flow, reference_PD): #maybe add optional arguments for ideal RRV and RRW range
        self.model = model
        self.reference_flow = reference_flow
        self.reference_PD = reference_PD
        self.flow_factor = math.sqrt(reference_flow / reference_PD)
        
        Hydrocyclones.flow_dict.update({model: self.flow_factor}) 
        Hydrocyclones.cleaner_models.append([model])

CLP_700 = Hydrocyclones('CLP 700', 163, 21) #check reference sheets. store these in a seperate file and make it possible to add custome models
CLP_350 = Hydrocyclones('CLP 350', 135, 21) 
posiflow = Hydrocyclones('Posiflow', 70, 20)

class Stage():

    consistencies = {} 
    pressures = {} 
    hydrocyclone_model = {}
    number_of_hydrocyclones = {}
    flow_rates = {}

    def __init__(self, stage_number):
        self.stage_number = stage_number
    
    def get_number_of_stages(self):
        select_stages = ('1', '2', '3', '4', '5', '6', '7')
        stages_chosen, ok = QInputDialog.getItem(self, 'Setup', 'Number of stages:', select_stages, 0, False)
        if ok and stages_chosen:
            return(int(stages_chosen))
        else:
            app.exec()

    def stage_flow_calc(self): 
        actual_PD = Stage.pressures[stage_key(self.stage_number, 'feed')] - Stage.pressures[stage_key(self.stage_number, 'accepts')]

        #feed flow to a cleaner = (sqrt(pressure drop) * (flow factor)) ^ 2
        feed_flow = Stage.number_of_hydrocyclones[stage_key(self.stage_number)] * (math.sqrt(actual_PD) 
        * Hydrocyclones.flow_dict[Stage.hydrocyclone_model[stage_key(self.stage_number)]]) ** 2
        Stage.flow_rates.update({stage_key(self.stage_number, 'feed'): feed_flow})
        
        A = np.array([[1, 1], [Stage.consistencies[stage_key(self.stage_number, 'accepts')], 
        Stage.consistencies[stage_key(self.stage_number, 'rejects')]]])
        
        B = np.array([Stage.flow_rates[stage_key(self.stage_number, 'feed')], 
        Stage.consistencies[stage_key(self.stage_number, 'feed')] * Stage.flow_rates[stage_key(self.stage_number, 'feed')]])
       
        X = np.linalg.solve(A, B)
        Stage.flow_rates[stage_key(self.stage_number, 'accepts')] = X[0]
        Stage.flow_rates[stage_key(self.stage_number, 'rejects')] = X[1]

    def WW_flow_calc(self):
        #feed to each stage is diluted by whitewater and the accepts flow from the following stage
        if self.stage_number < Stage.number_of_stages:
            next_stage_feed_flow = Stage.flow_rates[stage_key(self.stage_number + 1, 'feed')] 
            current_stage_reject_flow = Stage.flow_rates[stage_key(self.stage_number, 'rejects')]
            if self.stage_number < Stage.number_of_stages - 1:
                downstream_accept_flow = Stage.flow_rates[stage_key(self.stage_number + 2, 'accepts')]
               
                Stage.flow_rates.update({stage_key(self.stage_number, 'ww'): next_stage_feed_flow - current_stage_reject_flow - downstream_accept_flow})
            
            else:
                Stage.flow_rates.update({stage_key(self.stage_number, 'ww'): next_stage_feed_flow - current_stage_reject_flow})

class Gui(QWidget):

    def __init__(self):
        super().__init__()
        
        Stage.number_of_stages = Stage.get_number_of_stages(self)

        self.field_number_of_hydrocyclones = {}

        #consistencies are entered as percentages then converted to decimals before being stored in this dictionary
        self.field_cons = {}

        #pressures are in psi
        self.field_pres = {}
                           
        self.model_dropdown = [0] * Stage.number_of_stages

        #instantiate a Stage object for each stage
        for number in range(Stage.number_of_stages):
            Stage.stage_dictionary = {stage_key(number + 1): Stage(number + 1) for number in range(Stage.number_of_stages)}
                
        self.initUI()


    #called when "caclulate button is pressed. gets data from user entry fields, converts it from strings to floats, and maps 
    #to dictionaries that are used for calculations. calls calculation functions
    def calculate(self):
        try:
            Stage.consistencies.update({'ww': float(self.field_cons['ww'].text()) / 100})



            for stage_number in range(Stage.number_of_stages):
                Stage.number_of_hydrocyclones.update({stage_key(stage_number + 1): 
                int(self.field_number_of_hydrocyclones[stage_key(stage_number + 1)].text())})
                
                Stage.hydrocyclone_model.update({stage_key(stage_number + 1): self.model_dropdown[stage_number].currentText()})

                Stage.consistencies.update({
                    stage_key(stage_number + 1, 'feed'): float(self.field_cons[stage_key(stage_number + 1, 'feed')].text()) / 100, 
                    stage_key(stage_number + 1, 'accepts'): float(self.field_cons[stage_key(stage_number + 1, 'accepts')].text()) / 100, 
                    stage_key(stage_number + 1, 'rejects'): float(self.field_cons[stage_key(stage_number + 1, 'rejects')].text()) / 100})
                
                Stage.pressures.update({
                    stage_key(stage_number + 1, 'feed'): float(self.field_pres[stage_key(stage_number + 1, 'feed')].text()),
                    stage_key(stage_number + 1, 'accepts'): float(self.field_pres[stage_key(stage_number + 1, 'accepts')].text()), 
                    stage_key(stage_number + 1, 'rejects'): float(self.field_pres[stage_key(stage_number + 1, 'rejects')].text())})

                Stage.stage_flow_calc(Stage.stage_dictionary[stage_key(stage_number + 1)])

                print(stage_key(stage_number + 1, 'feed'), Stage.flow_rates[stage_key(stage_number + 1, 'feed')], 'gpm')
                print(stage_key(stage_number + 1, 'accepts'), Stage.flow_rates[stage_key(stage_number + 1, 'accepts')], 'gpm')
                print(stage_key(stage_number + 1, 'rejects'), Stage.flow_rates[stage_key(stage_number + 1, 'rejects')], 'gpm')

            for stage_number in range(Stage.number_of_stages):
                Stage.WW_flow_calc(Stage.stage_dictionary[stage_key(stage_number + 1)])
                
                if stage_number < Stage.number_of_stages - 1:
                    print(stage_key(stage_number + 1, 'ww'), Stage.flow_rates[stage_key(stage_number + 1, 'ww')], 'gpm')

            print(Stage.flow_rates)

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
        for stage_number in range(Stage.number_of_stages):
            self.number_of_hydrocyclones_label = QLabel('Cleaners in stage {} ='.format(stage_number+ 1))
            self.sys_grid.addWidget(self.number_of_hydrocyclones_label, stage_number+ 1, 0)

            self.field_number_of_hydrocyclones.update({stage_key(stage_number+ 1): QLineEdit()})
            self.sys_grid.addWidget(self.field_number_of_hydrocyclones[stage_key(stage_number+ 1)], stage_number+ 1, 1)

            self.model_dropdown[stage_number] = QComboBox()
            for Hydrocyclones.cleaner_model in Hydrocyclones.cleaner_models:
                self.model_dropdown[stage_number].addItem(Hydrocyclones.cleaner_model[0]) #0th item in list refers to cleaner model
            
            self.sys_grid.addWidget(self.model_dropdown[stage_number], stage_number+ 1, 2) 
            
            Stage.hydrocyclone_model.update({stage_key(stage_number+ 1): self.model_dropdown[stage_number].currentText()})

            self.cons_feed_label = QLabel('{}F ='.format(stage_number+ 1)) #create labels
            self.cons_accepts_label = QLabel('{}A ='.format(stage_number+ 1))
            self.cons_rejects_label = QLabel('{}R ='.format(stage_number+ 1))

            self.cons_grid.addWidget(self.cons_feed_label, stage_number, 0) #add labels to grid
            self.cons_grid.addWidget(self.cons_accepts_label, stage_number, 2)
            self.cons_grid.addWidget(self.cons_rejects_label, stage_number, 4)

            self.field_cons.update({
                stage_key(stage_number+ 1, 'feed'): QLineEdit(), 
                stage_key(stage_number+ 1, 'accepts'): QLineEdit(), 
                stage_key(stage_number+ 1, 'rejects'): QLineEdit()}) #maps fields to a dictionary

            self.cons_grid.addWidget(self.field_cons[stage_key(stage_number+ 1, 'feed')], stage_number, 1) #add fields to grid
            self.cons_grid.addWidget(self.field_cons[stage_key(stage_number+ 1, 'accepts')], stage_number, 3)
            self.cons_grid.addWidget(self.field_cons[stage_key(stage_number+ 1, 'rejects')], stage_number, 5)
            
            self.pres_feed_label = QLabel('{}F ='.format(stage_number+ 1))
            self.pres_accepts_label = QLabel('{}A ='.format(stage_number+ 1))
            self.pres_rejects_label = QLabel('{}R ='.format(stage_number+ 1))
            self.pres_grid.addWidget(self.pres_feed_label, stage_number, 0)
            self.pres_grid.addWidget(self.pres_accepts_label, stage_number, 2)
            self.pres_grid.addWidget(self.pres_rejects_label, stage_number, 4)

            self.field_pres.update({
                stage_key(stage_number+ 1, 'feed'): QLineEdit(), 
                stage_key(stage_number+ 1, 'accepts'): QLineEdit(), 
                stage_key(stage_number+ 1, 'rejects'): QLineEdit()})

            self.pres_grid.addWidget(self.field_pres[stage_key(stage_number+ 1, 'feed')], stage_number, 1)
            self.pres_grid.addWidget(self.field_pres[stage_key(stage_number+ 1, 'accepts')], stage_number, 3)
            self.pres_grid.addWidget(self.field_pres[stage_key(stage_number+ 1, 'rejects')], stage_number, 5)            


        #create label, map field to dictionary, and add field to grid for WW consistency
        self.cons_grid.addWidget(QLabel('WW ='), Stage.number_of_stages, 0) 
        self.field_cons.update({'ww': QLineEdit()})
        self.cons_grid.addWidget(self.field_cons['ww'], Stage.number_of_stages, 1)

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
    window = Gui()
    sys.exit(app.exec())