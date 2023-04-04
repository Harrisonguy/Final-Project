from tkinter import *
import inspect
import os
import apod_desktop
from tkinter import ttk

# Determine the path and parent directory of this script
script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
script_dir = os.path.dirname(script_path)

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# TODO: Create the GUI
root = Tk()
root.geometry('600x400')
root.title("Astronomy Picture of the Day Viewer")

test_options = [0,1,2,3,4,5,6,7,8,9]


# add frames 
frm_top = ttk.Frame(root)
frm_top.grid(row=0, column=0, columnspan=2)

frm_btm_left = ttk.LabelFrame(root, text='View Cached Image')
frm_btm_left.grid(row=1, column=0) 

frm_btm_right = ttk.LabelFrame(root, text='Get More Images')
frm_btm_right.grid(row=1, column=1)

# add widgets
select_img_lbl = ttk.Label(frm_btm_left, text='Select Image')
select_img_lbl.grid(row=0, column=0, sticky=S)

background_button = Button(frm_btm_left, text='Set as Desktop')
background_button.grid(row=0, column=2)

img_menu = ttk.Combobox(frm_btm_left, value=test_options)
img_menu.grid(row=0, column=1, padx=10)

select_date_lbl = ttk.Label(frm_btm_right, text='Select Date')
select_date_lbl.grid(row=0, column=0)

selected_date = ttk.Entry(frm_btm_right)
selected_date.grid(row=0, column=1, padx=10)

download_button = Button(frm_btm_right, text='Download Image')
download_button.grid(row=0, column=2)
root.mainloop()