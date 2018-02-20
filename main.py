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

#formats dictionary key
def stage_key(stage_number, position = ''):
    return('stage {} {}'.format(stage_number, position))

class Furnish:

    #densities are in pounds per cubic foot
    fiber_densities = {
        'water': 62.4, 'paper birch': 34, 'american chestnut': 25, 
        'red maple': 30, 'carolina poplar': 24, 'white spruce': 23,
        'black spruce': 25, 'norway spruce': 30, 'longleaf pine': 29, 
        'virginia pine': 26, 'jack pine': 24, 'red pine': 27,
        'western hemlock': 25, 'eastern hemlock': 24, 'carolina hemlock': 30,
        'alpine fir': 21, 'noble fir': 22, 'douglas fir': 29,
        'white cedar': 26} 

    def __init__(
        self,
        component1, component1_fraction = 1, #component fractions are mass fractions
        component2 = 'water', component2_fraction = 0, #water is used as a placeholder. mass fraction is 0 unless otherwise specified
        component3 = 'water', component3_fraction = 0, 
        component4 = 'water', component4_fraction = 0):

        self.component1 = component1
        self.component1_fraction = component1_fraction
        self.component2 = component2
        self.component2_fraction = component2_fraction
        self.component3 = component3
        self.component3_fraction = component3_fraction
        self.component4 = component4
        self.component4_fraction = component4_fraction

    def density(self, stage_number, position):
        if position == 'ww':
            fiber_mass_fraction = Stage.consistencies['ww']

        else:
            fiber_mass_fraction = Stage.consistencies[stage_key(stage_number, position)]
        
        weighted_average = self.component1_fraction * Furnish.fiber_densities[self.component1] 
        + self.component2_fraction * Furnish.fiber_densities[self.component2]
        + self.component3_fraction * Furnish.fiber_densities[self.component3]
        + self.component4_fraction * Furnish.fiber_densities[self.component4]
        
        return(fiber_mass_fraction * weighted_average)

hardwood_softwood_blend = Furnish('white spruce', .5, 'carolina poplar', .5)
softwood = Furnish('longleaf pine')
hardwood = Furnish('paper birch')


#add functionality for reverse, combicleaners, and FRUs if possible.
class Hydrocyclones:

    hydrocyclone_models = []
    flow_dict = {}

    def __init__(self, model, reference_flow, reference_PD): #maybe add optional arguments for ideal RRV and RRW range
        self.model = model
        self.reference_flow = reference_flow
        self.reference_PD = reference_PD
        self.flow_factor = math.sqrt(reference_flow / reference_PD)
        
        Hydrocyclones.flow_dict.update({model: self.flow_factor}) 
        Hydrocyclones.hydrocyclone_models.append([model])

CLP_700 = Hydrocyclones('CLP 700', 163, 21) #check reference sheets. store these in a seperate file and make it possible to add custome models
CLP_350 = Hydrocyclones('CLP 350', 135, 21) 
posiflow = Hydrocyclones('Posiflow', 70, 20)

class Stage:

    consistencies = {} #percent
    pressures = {} #psi
    hydrocyclone_model = {}
    number_of_hydrocyclones = {}
    flow_rates = {} #gpm
    mass_flow_rates = {} #bone-dry short tons per day (BDSTPD)

    def __init__(self, stage_number):
        self.stage_number = stage_number
    
    def get_number_of_stages(self):
        select_stages = ('1', '2', '3', '4', '5', '6', '7')
        stages_chosen, ok = QInputDialog.getItem(self, 'Setup', 'Number of stages:', select_stages, 0, False)
        if ok and stages_chosen:
            return(int(stages_chosen))
        else:
            app.exec()

    @staticmethod
    def mass_flow(stage_number, flow, position):
        #gal/min * (0.133681 ft^3)/gal * lb/ft^3 * (0.0005 st)/lb * (1440 min)/day 
        return(flow * softwood.density(stage_number, position) * 0.133681 * 0.0005 * 1440)

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

        feed_mass_flow = Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'feed')], 'feed')
        accepts_mass_flow = Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'accepts')], 'accepts')
        rejects_mass_flow = Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'rejects')], 'rejects')
        
        Stage.mass_flow_rates.update({
            stage_key(self.stage_number, 'feed'): feed_mass_flow,
            stage_key(self.stage_number, 'accepts'): accepts_mass_flow,
            stage_key(self.stage_number, 'rejects'): rejects_mass_flow})

        # print(Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'feed')], 'feed'))
        # print(Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'accepts')], 'accepts'))
        # print(Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'rejects')], 'rejects'))

    def ww_flow_calc(self):
        #feed to each stage is diluted by whitewater and downstream accepts
        if self.stage_number < Stage.number_of_stages:
            next_stage_feed_flow = Stage.flow_rates[stage_key(self.stage_number + 1, 'feed')] 
            current_stage_reject_flow = Stage.flow_rates[stage_key(self.stage_number, 'rejects')]
            if self.stage_number < Stage.number_of_stages - 1:
                downstream_accept_flow = Stage.flow_rates[stage_key(self.stage_number + 2, 'accepts')]
               
                Stage.flow_rates.update({stage_key(self.stage_number, 'ww'): next_stage_feed_flow - current_stage_reject_flow - downstream_accept_flow})
                ww_mass_flow = Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'ww')], 'ww')
                Stage.mass_flow_rates.update({stage_key(self.stage_number, 'ww'): ww_mass_flow})

            else:
                Stage.flow_rates.update({stage_key(self.stage_number, 'ww'): next_stage_feed_flow - current_stage_reject_flow})
                ww_mass_flow = Stage.mass_flow(self.stage_number, Stage.flow_rates[stage_key(self.stage_number, 'ww')], 'ww')
                Stage.mass_flow_rates.update({stage_key(self.stage_number, 'ww'): ww_mass_flow})


class Gui(QWidget):

    def __init__(self):
        super().__init__()
        
        #get number of stages from dropdown menu
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


    #called when 'caclulate' button is pressed. gets data from user entry fields, converts it from strings to floats, and maps 
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
                Stage.ww_flow_calc(Stage.stage_dictionary[stage_key(stage_number + 1)])
                
                # if stage_number < Stage.number_of_stages - 1:
                #     print(stage_key(stage_number + 1, 'ww'), Stage.flow_rates[stage_key(stage_number + 1, 'ww')], 'gpm')

            print('consistencies = ' + str(Stage.consistencies))
            print('flow rates = ' + str(Stage.flow_rates))
            print('mass flow rates = ' + str(Stage.mass_flow_rates))

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
            self.number_of_hydrocyclones_label = QLabel('Cleaners in stage {} ='.format(stage_number + 1))
            self.sys_grid.addWidget(self.number_of_hydrocyclones_label, stage_number+ 1, 0)

            self.field_number_of_hydrocyclones.update({stage_key(stage_number + 1): QLineEdit()})
            self.sys_grid.addWidget(self.field_number_of_hydrocyclones[stage_key(stage_number + 1)], stage_number + 1, 1)

            #create cleaner model selection dropdown menu
            self.model_dropdown[stage_number] = QComboBox()
            for model in Hydrocyclones.hydrocyclone_models:
                self.model_dropdown[stage_number].addItem(model[0]) #0th item in list refers to cleaner model
            
            self.sys_grid.addWidget(self.model_dropdown[stage_number], stage_number + 1, 2) 
            
            Stage.hydrocyclone_model.update({stage_key(stage_number + 1): self.model_dropdown[stage_number].currentText()})

            self.cons_feed_label = QLabel('{}F ='.format(stage_number + 1)) #create labels
            self.cons_accepts_label = QLabel('{}A ='.format(stage_number + 1))
            self.cons_rejects_label = QLabel('{}R ='.format(stage_number + 1))

            self.cons_grid.addWidget(self.cons_feed_label, stage_number, 0) #add labels to grid
            self.cons_grid.addWidget(self.cons_accepts_label, stage_number, 2)
            self.cons_grid.addWidget(self.cons_rejects_label, stage_number, 4)

            self.field_cons.update({
                stage_key(stage_number + 1, 'feed'): QLineEdit(), 
                stage_key(stage_number + 1, 'accepts'): QLineEdit(), 
                stage_key(stage_number + 1, 'rejects'): QLineEdit()}) #maps fields to a dictionary

            self.cons_grid.addWidget(self.field_cons[stage_key(stage_number + 1, 'feed')], stage_number, 1) #add fields to grid
            self.cons_grid.addWidget(self.field_cons[stage_key(stage_number + 1, 'accepts')], stage_number, 3)
            self.cons_grid.addWidget(self.field_cons[stage_key(stage_number + 1, 'rejects')], stage_number, 5)
            
            self.pres_feed_label = QLabel('{}F ='.format(stage_number + 1))
            self.pres_accepts_label = QLabel('{}A ='.format(stage_number + 1))
            self.pres_rejects_label = QLabel('{}R ='.format(stage_number + 1))
            self.pres_grid.addWidget(self.pres_feed_label, stage_number, 0)
            self.pres_grid.addWidget(self.pres_accepts_label, stage_number, 2)
            self.pres_grid.addWidget(self.pres_rejects_label, stage_number, 4)

            self.field_pres.update({
                stage_key(stage_number + 1, 'feed'): QLineEdit(), 
                stage_key(stage_number + 1, 'accepts'): QLineEdit(), 
                stage_key(stage_number + 1, 'rejects'): QLineEdit()})

            self.pres_grid.addWidget(self.field_pres[stage_key(stage_number + 1, 'feed')], stage_number, 1)
            self.pres_grid.addWidget(self.field_pres[stage_key(stage_number + 1, 'accepts')], stage_number, 3)
            self.pres_grid.addWidget(self.field_pres[stage_key(stage_number + 1, 'rejects')], stage_number, 5)            


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