import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QApplication, QLineEdit, QFrame, QGridLayout, QLabel, QInputDialog
from PyQt5.QtGui import *

field_cons = {}
consistencies = {}
field_pres = {}
pressures = {}
number_of_stages = 6

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
    
        
    def calculate(self):
        
        for i in range(0, number_of_stages):
            #test = consistencies['{}F'.format(i + 1)].text()
            consistencies.update({'{}F'.format(i + 1): field_cons['{}F'.format(i + 1)].text(), 
                '{}A'.format(i + 1): field_cons['{}A'.format(i + 1)].text(), '{}R'.format(i + 1): field_cons['{}R'.format(i + 1)].text()})
            pressures.update({'{}F'.format(i + 1): field_pres['{}F'.format(i + 1)].text(), 
                '{}A'.format(i + 1): field_pres['{}A'.format(i + 1)].text(), '{}R'.format(i + 1): field_pres['{}R'.format(i + 1)].text()})


    def initUI(self):

        cons_title = QLabel('Consistencies (%):')
        pressure_title = QLabel('Pressures (psi):')
        calculate_button = QPushButton('Calculate')

        #set this with dropdown, range: 1 - 6

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
        calc_hbox = QHBoxLayout()
        cons_vbox = QVBoxLayout()
        pres_vbox = QVBoxLayout()

        data_hbox.addLayout(cons_vbox)
        data_hbox.addLayout(pres_vbox)
        data_hbox.addStretch(1) #not sure what his does. need to push boxes left

        cons_vbox.addWidget(cons_title) #vertical box containing consistency table
        cons_vbox.addLayout(cons_grid)
        cons_vbox.addLayout(calc_hbox)
        cons_vbox.addStretch(1) #pushes consistency table and calculate button upward when resizing window
        cons_vbox.setContentsMargins(0, 0, 20, 0)

        pres_vbox.addWidget(pressure_title) #vertical box containing pressure table
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




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex1 = Example()
    # ex2 = Example()
    sys.exit(app.exec())