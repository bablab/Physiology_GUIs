#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 27 22:43:01 2023

Neurokit ECG Editor GUI

@author: Paul Savoca
Email: ps365@g.ucla.edu
Twitter: @pw_savoca
Lab: Brain and Body Lab, UCLA

This application is intended for manual editing of ECG data from .Acq files. 
The GUI allows for manual checking and editting of R-peaks which are initial detected using the Neurokit2 (Makowski et al., 2020).
The application generates 2 output files: 
    1) the filtered ECG signal
    2) the finalized set of R-peaks
These files can then be used for ECG-based analyses (e.g., IBI, HRV, ect.)
"""

#Load Dependencies
import numpy as np
from numpy import savetxt
import neurokit2 as nk
#import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#from mpl_point_clicker import clicker
#import mpl_connect
from matplotlib.figure import Figure
import PySimpleGUI as sg
import os
import re
import pandas as pd


#Create Empty Delete and Add Peak Arrays
delete_peaks=[]
add_peaks=[]

#Define Plotting Functions
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    #figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    #toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)
    return figure_canvas_agg, toolbar

def draw(figure_canvas_agg, toolbar):
    figure_canvas_agg.draw()
    #toolbar.update()   

def onpick1(event):
    thisline = event.artist
    xval = thisline.get_xdata()
    yval = thisline.get_ydata()
    ind = event.ind
    
    if edit_mode == 'add' and thisline == ecg:
        max_ind = np.argmax(yval[ind])
        max_ind = ind[max_ind]
        local_max = findpeak(max_ind, ecg_clean)
        ax.plot(xval[local_max], yval[local_max], 'yo')
        draw(figure_canvas_agg, toolbar)
        add_peaks.append(local_max)
        
    if edit_mode == 'remove' and thisline == points:
        ax.plot(xval[ind], yval[ind], 'rx')
        draw(figure_canvas_agg, toolbar)
        delete_peaks.append(int(ind))
        
    if edit_mode == 'add_nosnap' and thisline == ecg:
        max_ind = np.argmax(yval[ind])
        max_ind = ind[max_ind]
        local_max = max_ind
        ax.plot(xval[local_max], yval[local_max], 'yo')
        draw(figure_canvas_agg, toolbar)
        add_peaks.append(local_max)
        
#Snap to Peak Correction
def findpeak(x, ecg_clean):
    peak_error = SR * 0.125
    win_start = int(x - peak_error)
    win_end = int(x + peak_error)
    if win_start < 0:
        win_start = 0
    if win_end > len(ecg_clean)*SR:
        win_end = len(ecg_clean) *SR
    x = np.argmax(ecg_clean[((win_start)):((win_end))]) + (x - peak_error)
    return int(x)

#Ploting Clean ECG with R-peaks
def ecg_plot():
    fig.subplots_adjust(right=.95, left=0.1, bottom=0.15, top=0.9)
    time = np.linspace(0, ecg_clean.shape[0] / SR, ecg_clean.shape[0])
    ax.set_title("ECG Data")
    ax.set_xlabel("Time (Seconds)")
    ax.set_ylabel("Volts")
    ecg, = ax.plot(time, ecg_clean, 'r-', picker=True)
    points, = ax.plot(peaks/SR, ecg_clean[peaks], "bo", picker=True) 
    draw(figure_canvas_agg, toolbar)
    return ecg, points

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

#Starting Screen
layout_intro = [[sg.T("")], [sg.Text("Information about ECG Cleaning Application.")],
          [sg.Text("Instructions:")],
          [sg.Text("1) Select .Acq Physio File or .Csv (single column, no header) Physio Timeseries")],
          [sg.Text("2) Select ECG Source Channel and/or Parameters")],
          [sg.Text("3) View Filtered Data -- Add or Remove R Peaks")],
          [sg.Text("4) Save Edits -- Outputs Filtered ECG and Index of Correct R Peaks")],
          [sg.Text("Press Continue to Begin.")],
          [sg.Button('Continue'), sg.B('Exit')]]

#Build Window
window_intro = sg.Window('ECG Cleaning App', layout_intro, size=(600,400))
        
while True:
    event, values = window_intro.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        exit()
        window_intro.close()
        break
        
    elif event == "Continue":
        window_intro.close()
        break
        
#Input Selection Screen
layout_file = [[sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],
               [sg.Button("Load"), sg.Button("Exit")]]

#Build Window
window_file = sg.Window('ECG Cleaning App', layout_file, size=(600,150))
    
while True:
    event, values = window_file.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        exit()
        break
    elif event == "Load":
        file_name = values["-IN-"]
        window_file.close()
        break
       
#File Prep for ACQ Files
if re.search(".acq", file_name):
    #Pull Channel names and Sampling Rate
    physio_file, sampling_rate = nk.read_acqknowledge(file_name)
    channels = tuple(physio_file.columns)
    
    ##Window to Select Channel & Notch Filter  
    layout_settings = [[sg.T("")],[sg.Text("Select ECG Source:"), sg.Combo(channels, default_value='',key='-Source-')],
             [sg.Text("Notch Filter:"),sg.Radio("60Hz", "notch", key='60', default=True),sg.Radio("50Hz", "notch", key='50')],
             [sg.Button("Plot Signal"), sg.Button("Exit")]]
    
    ###Building Window
    window_settings = sg.Window('ECG Cleaning App', layout_settings, size=(600,300))
        
    while True:
        event, values = window_settings.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            exit()
            break
        elif event == "Plot Signal":
            ecg_source = values["-Source-"]
            if values['60']==True:
                notch_filter= 60
            elif values['50']==True:
                notch_filter= 50
            window_settings.close()
            break
    
    

#File Prep for CSV Files

elif re.search(".csv", file_name):
    physio_file = pd.read_csv(file_name, header=None)
    
    ##Window to Select Sampling Rate & Notch Filter  
    layout_settings = [[sg.T("")],[sg.Text("Set Sampling Rate:"), sg.Input('', enable_events=True, key='-SRINPUT-', font=('Arial Bold', 20), expand_x=True, justification='left')],
             [sg.Text("Notch Filter:"),sg.Radio("60Hz", "notch", key='60', default=True),sg.Radio("50Hz", "notch", key='50')],
             [sg.Button("Plot Signal"), sg.Button("Exit")]]
    
    ###Building Window
    window_settings = sg.Window('ECG Cleaning App', layout_settings, size=(600,300))
        
    while True:
        event, values = window_settings.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            exit()
            break
        elif event == "Plot Signal":
            sampling_rate = np.float64(values["-SRINPUT-"])
            ecg_source = 0
            if values['60']==True:
                notch_filter= 60
            elif values['50']==True:
                notch_filter= 50
            window_settings.close()
            break

#If Invlaid File type (not ACQ or CSV)
else:
    layout_fileError = [[sg.T("")],
              [sg.Text("ERROR: Invalid File Type")],
              [sg.Text("Only acceptable file type: .acq or .csv")],
              [sg.Button('Exit')]]
    
    window_fileError = sg.Window('ECG Cleaning App', layout_fileError, size=(600,400))
    
    while True:
        event, values = window_fileError.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            exit()
            window_fileError.close()
            break

#ECG Processing
Raw_ECG = physio_file[ecg_source]
SR=sampling_rate
print(type(SR))
ecg_clean = nk.ecg_clean(Raw_ECG, sampling_rate=SR, method='neurokit', powerline=notch_filter)
r_peaks = nk.ecg_peaks(ecg_clean, sampling_rate=SR)
peaks = (np.where(r_peaks[0] == 1)[0])
peaks = peaks.tolist()

# 2. create PySimpleGUI window, a fixed-size Frame with Canvas which expand in both x and y.
layout = [
    [sg.T('Edit Physio Data')],
    [sg.B('Re-Plot'), sg.B('Save'),sg.B('Exit')],
    [sg.T('Controls:')],
    [sg.B('Add Peak (Snap)', button_color = ('white','black')), sg.B('Remove Peak', button_color = ('white','black')),
     sg.B('Add Peak (No-Snap)', button_color = ('white','black')), sg.Canvas(key='controls_cv')],
    [sg.Column(
        layout=[
            [sg.Canvas(key='fig_cv',
                       size=(1500, 750),
                       expand_x=True,
                       expand_y=True
                       )]
        ],
        background_color='#DAE0E6',
        pad=(0, 0)
    )],
]

window = sg.Window('ECG Editor', layout, finalize=True, resizable = True)

# 3. Create a plot of the ECG Data
fig = Figure(figsize=(20, 10), dpi=125)
fig.canvas.mpl_connect('pick_event', onpick1)
ax = fig.add_subplot()
figure_canvas_agg, toolbar = draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
ecg, points = ecg_plot()

# 4. GUI Events
while True:
    event, values = window.read()
   
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    
    elif event == 'Add Peak (Snap)':
        edit_mode = 'add'
        window['Add Peak (Snap)'].update(button_color = ('black','yellow'))
        window['Remove Peak'].update(button_color = ('white','black'))
        window['Add Peak (No-Snap)'].update(button_color = ('white','black'))
        
    
    elif event == 'Remove Peak':
        edit_mode = 'remove'
        window['Remove Peak'].update(button_color = ('black','yellow'))
        window['Add Peak (Snap)'].update(button_color = ('white','black'))
        window['Add Peak (No-Snap)'].update(button_color = ('white','black'))
        
    elif event == 'Add Peak (No-Snap)':
        edit_mode = 'add_nosnap'
        window['Remove Peak'].update(button_color = ('white','black'))
        window['Add Peak (Snap)'].update(button_color = ('white','black'))
        window['Add Peak (No-Snap)'].update(button_color = ('black','yellow'))
       
    
    elif event == 'Re-Plot':
        #Reset Graph and Edited Points
        ax.cla()
        add_peaks =[]
        delete_peaks = []
        #New Plot
        ecg, points = ecg_plot()
     
#Saving Edits & Plot Final Product
    elif event == 'Save':

        #Open pop-up to select output folder
        output_location=sg.popup_get_folder('Select Output Location', title="Output Folder")

        #Clear what was previously drawn
        ax.cla()                  
        
        #Remove Peaks Identified as Errors
        for i in sorted(delete_peaks, reverse=True):
            del peaks[int(i)]
        
        #Add Peaks identified as missing
        for i in add_peaks:
            peaks.append(i)  
        peaks = np.array(sorted(peaks))
        
        #Plot Final Product -- No more ability to edit; gray out buttons
        window['Remove Peak'].update(button_color = ('white','gray'), disabled=True)
        window['Add Peak (Snap)'].update(button_color = ('white','gray'), disabled=True)
        window['Add Peak (No-Snap)'].update(button_color = ('white','gray'), disabled=True)
        ecg_plot()
        
        #Save Outputs
        ppt_name = file_name.rsplit('/',1)[1]
        ppt_name = ppt_name.replace(".acq", "")
        ppt_name = ppt_name.replace(".csv", "")
        Rs_name = "{}_r_peaks_edited.csv".format(ppt_name)
        ECG_name = "{}_ECG_cleaned.csv".format(ppt_name)
        os.chdir(output_location)
        savetxt(Rs_name, peaks, delimiter=',')
        savetxt(ECG_name, ecg_clean, delimiter=',')

#Close window to exit
window.close()



