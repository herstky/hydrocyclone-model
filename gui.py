import tkinter as tk
import hydrocyclone_model as hm

root = tk.Tk()

# entries are in decimal format
F_cons = [] 
A_cons = []
R_cons = []

entries = {}

# entries = [[] for i in range(hm.number_of_stages)]
# entries[0][0] = 5
# print(entries[1][1])


for i in range(0, hm.number_of_stages):
	tk.Label(root, text="{}F cons% = ".format(i + 1)).grid(row=0, column=(2 * i))
	tk.Label(root, text="{}A cons% = ".format(i + 1)).grid(row=1, column=(2 * i))
	tk.Label(root, text="{}R cons% = ".format(i + 1)).grid(row=2, column=(2 * i))
	entries = {'{}F'.format(i + 1): tk.Entry(root, width="5"), '{}A'.format(i + 1): tk.Entry(root, width="5"), '{}R'.format(i + 1): tk.Entry(root, width="5")}
	entries['{}F'.format(i + 1)].grid(row=0, column=2 * i + 1)
	entries['{}A'.format(i + 1)].grid(row=1, column=2 * i + 1)
	entries['{}R'.format(i + 1)].grid(row=2, column=2 * i + 1)
	# F_cons[i] = 
	# A_cons[i] =
	# R_cons[i] = 
		

print(hm.number_of_stages)

# root.geometry('200x100')

root.mainloop()