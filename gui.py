import tkinter as tk
import hydrocyclone_model as hm

root = tk.Tk()

def create_stage(i):
	tk.Label(root, text="{}F cons% = ".format(i + 1)).grid(row=0, column=(2 * i + 1))
	tk.Label(root, text="{}A cons% = ".format(i + 1)).grid(row=1, column=(2 * i + 1))
	tk.Label(root, text="{}R cons% = ".format(i + 1)).grid(row=2, column=(2 * i + 1))

print(hm.number_of_stages)

# for i in range(0, number_of_stages):


# root.geometry('200x100')

for i in range(0, hm.number_of_stages):
	create_stage(i)

root.mainloop()