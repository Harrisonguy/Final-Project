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


def update_image(explantion, file_path):
    
    sel_image = Image.open(file_path)
    max_size = (1200, 800)
    sel_image.thumbnail(max_size)
    current_img = ImageTk.PhotoImage(sel_image)
    lbl_image.configure(image=current_img)
    lbl_image.image = current_img
    
    
    lbl_exp = ttk.Label(frm_top, text=explantion, wraplength=1000)
    lbl_exp.grid(row=1, padx=10, pady=10)



    return