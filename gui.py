# To do:
# pressure entry table. should be to the left of consistency entry table. seperate frame?
# drop down menu for number of stages. main script should fetch that variable from this script
# scalable system visualization and data output

import tkinter as tk
import hydrocyclone_model as hm

root = tk.Tk()

# entries should be converted from percentage to decimal
F_cons = [0] * hm.number_of_stages 
A_cons = [0] * hm.number_of_stages
R_cons = [0] * hm.number_of_stages

entries = {}

tk.Label(root, text="Consistencies (%):").grid(columnspan=6, sticky=tk.W)

# build consistency entry table. input is in percent, so they must be converted to decimal
for i in range(0, hm.number_of_stages):
	tk.Label(root, text="{}F =".format(i + 1)).grid(row=1, column=(2 * i))
	tk.Label(root, text="{}A =".format(i + 1)).grid(row=2, column=(2 * i))
	tk.Label(root, text="{}R =".format(i + 1)).grid(row=3, column=(2 * i))
	entries.update({'{}F'.format(i + 1): tk.Entry(root, width=5), '{}A'.format(i + 1): tk.Entry(root, width=5), '{}R'.format(i + 1): tk.Entry(root, width=5)}) 
	entries['{}F'.format(i + 1)].grid(row=1, column=2 * i + 1, padx=(0, 10))
	entries['{}A'.format(i + 1)].grid(row=2, column=2 * i + 1, padx=(0, 10))
	entries['{}R'.format(i + 1)].grid(row=3, column=2 * i + 1, padx=(0, 10))

# fetch data from entry tables. this should apply to all data tables
def calculate():
	for i in range(0, hm.number_of_stages):
		try: 
			F_cons[i] = float(entries['{}F'.format(i + 1)].get())
			print("{}F consistency = {}".format(i + 1, F_cons[i]))
			A_cons[i] = float(entries['{}A'.format(i + 1)].get())
			print("{}A consistency = {}".format(i + 1, A_cons[i]))
			R_cons[i] = float(entries['{}R'.format(i + 1)].get())
			print("{}R consistency = {}".format(i + 1, R_cons[i]))
		except: 
			print("Please enter a value in every field")
			return()

	# A_cons[i] = float(entries['{}A'.format(i + 1)].get())
	# R_cons[i] = float(entries['{}R'.format(i + 1)].get())

quit = tk.Button(root, text="Quit", command=root.quit).grid(row=hm.number_of_stages + 1, columnspan=2, sticky=tk.W, pady=4)

calculate_button = tk.Button(root, text="Calculate", command=calculate).grid(row=hm.number_of_stages + 1, columnspan=4, sticky=tk.E, pady=4)


# root.geometry('200x100')

root.mainloop()