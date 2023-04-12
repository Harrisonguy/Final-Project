from tkinter import *
import inspect
import os
import apod_desktop
from tkinter import ttk
import image_lib
import ctypes
import sqlite3
from PIL import Image, ImageTk
from tkcalendar import *
import datetime as dt

# Determine the path and parent directory of this script
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)

# Initialize the image cache
apod_desktop.init_apod_cache(script_dir)

# TODO: Create the GUI
root = Tk()
root.geometry()
root.title("Astronomy Picture of the Day Viewer")
root.rowconfigure(0, weight=75)
root.rowconfigure(1, weight=25)


# Set the window icon
icon_path = os.path.join(script_dir, 'nasa.ico')
app_id = 'COMP593.APODImageViewer'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
root.iconbitmap(icon_path)

# add frames 
frm_top = ttk.Frame(root)
frm_top.grid(row=0, column=0, columnspan=2, sticky=NSEW)

frm_btm_left = ttk.LabelFrame(root, text='View Cached Image')
frm_btm_left.grid(row=1, column=0, sticky=NSEW) 

frm_btm_right = ttk.LabelFrame(root, text='Get More Images')
frm_btm_right.grid(row=1, column=1, sticky=NSEW)

# add widgets
select_img_lbl = ttk.Label(frm_btm_left, text='Select Image')
select_img_lbl.grid(row=0, column=0, sticky=NSEW)

# Put image into frame
image_path = os.path.join(script_dir, 'nasa.png')
nasa_logo = Image.open(image_path)
img_nasa = ImageTk.PhotoImage(nasa_logo)
lbl_image = ttk.Label(frm_top, image=img_nasa)
lbl_image.grid(padx=10, pady=10)

lbl_exp = ttk.Label(frm_top, text=None, wraplength=1000)
lbl_exp.grid(row=1, padx=10, pady=10)

def handle_set_desktop():  
    global image_path
    image_lib.set_desktop_background_image(image_path)

background_button = Button(frm_btm_left, text='Set as Desktop', command=handle_set_desktop)
background_button.grid(row=0, column=2)

# Pull-down list of saved apod titles
title_list = sorted(apod_desktop.get_all_apod_titles())
img_menu = ttk.Combobox(frm_btm_left, value=title_list, state='readonly')
img_menu.set("Select an Image")
img_menu.grid(row=0, column=1, padx=10)


def handle_title_select(event):
    sel_title = img_menu.get()   
    query = f"""SELECT file_path, explanation FROM apod WHERE title = ?"""
    con = sqlite3.connect(apod_desktop.image_cache_db)
    cur = con.cursor()
    cur.execute(query, (sel_title,))
    query_result = cur.fetchone()
    global image_path
    image_path = query_result[0]
    explantion = query_result[1]
    update_image(explantion, image_path)

img_menu.bind('<<ComboboxSelected>>', handle_title_select)
earliest_date = dt.date(1995, 6, 16)
current_date = dt.date.today()
cal = DateEntry(frm_btm_right, mindate=earliest_date, maxdate=current_date)
cal.grid(row=0, column=1)

def get_selected_date():
    selected_date = cal.get_date().strftime('%Y-%m-%d')
    apod_id = apod_desktop.add_apod_to_cache(selected_date) 
    apod_dict = apod_desktop.get_apod_info(apod_id)
    global image_path
    image_path= apod_dict['file_path']
    print(image_path)
    explanation = apod_dict['explanation']
    title = apod_dict['title']
    title_list.append(title)
    img_menu['values'] = title_list
    update_image(explanation, image_path, title)

def update_image(explantion, file_path, title=None):
    
    sel_image = Image.open(file_path)
    max_size = (1200, 800)
    sel_image.thumbnail(max_size)
    
    current_img = ImageTk.PhotoImage(sel_image)
    lbl_image.configure(image=current_img)
    lbl_image.image = current_img
    
    lbl_exp.config(text=explantion)
    
    if title is not None:
        img_menu.set(title)


select_date_lbl = ttk.Label(frm_btm_right, text='Select Date')
select_date_lbl.grid(row=0, column=0)

download_button = Button(frm_btm_right, text='Download Image', command=get_selected_date)
download_button.grid(row=0, column=2)
root.mainloop()