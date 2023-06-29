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

#-----------------Start Updated Code

#Load Dependencies
import numpy as np
from numpy import savetxt
import neurokit2 as nk
#import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mpl_point_clicker import clicker
from matplotlib.figure import Figure
import PySimpleGUI as sg
import os

#Define Plotting Functions
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)
    return figure_canvas_agg, toolbar

def draw(figure_canvas_agg, toolbar):
    figure_canvas_agg.draw()
    toolbar.update()


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

##Starting Screen
layout_intro = [[sg.T("")], [sg.Text("Information about ECG Cleaning Application.")],
          [sg.Text("Intructions:")],
          [sg.Text("1) Select .Acq Physio File")],
          [sg.Text("2) Select ECG Source Channel and Filtering Parameters")],
          [sg.Text("3) View Filtered Data -- Add or Remove R Peaks")],
          [sg.Text("4) Save Edits -- Outputs Filtered ECG and Index of Correct R Peaks")],
          [sg.Text("Press Continue to Begin.")],
          [sg.Button('Continue'), sg.B('Exit')]]

#Build Window
window_intro = sg.Window('ECG Cleaning App', layout_intro, size=(600,400))
    
while True:
    event, values = window_intro.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        window_intro.close()
        break
    elif event == "Continue":
        window_intro.close()
        break

##Input Selection Screen
layout_file = [[sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")],[sg.Button("Submit")]]

#Build Window
window_file = sg.Window('ECG Cleaning App', layout_file, size=(600,150))

    
while True:
    event, values = window_file.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    elif event == "Submit":
        file_name = values["-IN-"]
        window_file.close()
        break
    
      
physio_file = nk.read_acqknowledge(file_name)
physio_file = physio_file[0]
channels = tuple(physio_file.columns)

##Window to Select Output location & Sampling Rate  
layout_settings = [[sg.T("")],[sg.Text("Select ECG Source:"), sg.Combo(channels, default_value='',key='-IN4-')],
         [sg.Text("Sampling Rate (Hz):"), sg.Input(key='-IN3-')],
         [sg.Text("Notch Filter:"),sg.Radio("60Hz", "notch", key='60', default=True),sg.Radio("50Hz", "notch", key='50')],
         [sg.T("")], [sg.Text("Choose Output Location: "), sg.Input(), sg.FolderBrowse(key="-IN2-")],
         [sg.Button("Submit")]]

###Building Window
window_settings = sg.Window('ECG Cleaning App', layout_settings, size=(600,300))
    
while True:
    event, values = window_settings.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        break
    elif event == "Submit":
        output_location = values["-IN2-"]
        sampling_rate = int(values["-IN3-"])
        ecg_source = values["-IN4-"]
        if values['60']==True:
            notch_filter= 60
        elif values['50']==True:
            notch_filter= 50
        window_settings.close()
        break

#ECG Processing
Raw_ECG = physio_file[ecg_source]
SR=sampling_rate
ecg_clean = nk.ecg_clean(Raw_ECG, sampling_rate=SR, method='neurokit', powerline=notch_filter)
r_peaks = nk.ecg_peaks(ecg_clean, sampling_rate=SR)

# 2. create PySimpleGUI window, a fixed-size Frame with Canvas which expand in both x and y.

layout = [
    [sg.T('Edit Physio Data')],
    [sg.B('Plot'), sg.B('Save'),sg.B('Exit')],
    [sg.T('Controls:')],
    [sg.Canvas(key='controls_cv')],
    [sg.T('Figure:')],
    [sg.Column(
        layout=[
            [sg.Canvas(key='fig_cv',
                       # it's important that you set this size
                       size=(1500, 750),
                       expand_x=True,
                       expand_y=True
                       )]
        ],
        background_color='#DAE0E6',
        pad=(0, 0)
    )],
]

window = sg.Window('Matplotlib', layout, finalize=True, resizable = True)

# 3. Create a matplotlib canvas under sg.Canvas or sg.Graph
fig = Figure(figsize=(20, 10), dpi=125)#, subplotpars = True)
ax = fig.add_subplot()
figure_canvas_agg, toolbar = draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas) #ADDED

# 4. initial for figure
ax.set_title("ECG Data")
ax.set_xlabel("Time (Seconds)")
ax.set_ylabel("Volts")


# 5. PySimpleGUI event loop
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    elif event == 'Plot':
        ax.cla()                    # Clear axes first if required
        fig.subplots_adjust(right=.80, left=0.1, bottom=0.15, top=0.9)
        time = np.linspace(0, ecg_clean.shape[0] / SR, ecg_clean.shape[0])
        peaks = (np.where(r_peaks[0] == 1)[0])
        ax.set_title("ECG Data")
        ax.set_xlabel("Time (Seconds)")
        ax.set_ylabel("Volts")
        ax.plot(time, ecg_clean, 'r-')
        ax.plot(peaks/SR, ecg_clean[peaks], "o") 
        klicker = clicker(ax, ["Remove", "Add"], markers=["X","o"])
        draw(figure_canvas_agg, toolbar)             # do Update to GUI canvas

#Saving Edits
    elif event == 'Save':
        #Error parameter for snap-to-peak funcationality. Error is +/- 0.125s
        peak_error = SR * 0.125 
        
        ecg_edits = klicker.get_positions()
        add = (ecg_edits['Add'])
        add = [i[0] for i in add]
        
        add = [i * SR for i in add]
        
        #Snap to Peak Correction
        for i in add:
            add_start = int(i-peak_error)
            add_end = int(i+peak_error)
            
            if add_start < 0:
                add_start = 0
                
            if add_end > len(ecg_clean) * SR:
                add_end = len(ecg_clean) * SR
                
            i = np.argmax(ecg_clean[((add_start)):((add_end))]) + (i-peak_error)
    
        add = [int(i) for i in add]
        remove = ecg_edits['Remove']
        remove = [i[0] for i in remove]
        remove = [i * SR for i in remove]
        all_peaks = [*remove, *add, *peaks]
        all_peaks = sorted(all_peaks)
    
        i=1;
        while i<len(all_peaks):
            if(all_peaks[i]-all_peaks[i-1] < peak_error):
                all_peaks.remove(all_peaks[i])
                all_peaks.remove(all_peaks[i-1])
            else:
                i+=1
        all_peaks = np.array(all_peaks)

        ax.cla()                    # Clear axes first if required
        fig.subplots_adjust(right=.80, left=0.1, bottom=0.15, top=0.9)
        time = np.linspace(0, ecg_clean.shape[0] / SR, ecg_clean.shape[0])
        peaks = (np.where(r_peaks[0] == 1)[0])
        ax.set_title("ECG Data")
        ax.set_xlabel("Time (Seconds)")
        ax.set_ylabel("Volts")
        
        ax.plot(time, ecg_clean, 'r-')
        ax.plot(all_peaks/SR, ecg_clean[all_peaks], "o")
        
     
        draw(figure_canvas_agg, toolbar)             # do Update to GUI canvas
        
        
        #Save Outputs
        ppt_name = file_name.rsplit('/',1)[1]
        ppt_name = ppt_name.replace(".acq", "")
        Rs_name = "{}_r_peaks_edited.csv".format(ppt_name)
        ECG_name = "{}_ECG_cleaned.csv".format(ppt_name)
        os.chdir(output_location)
        savetxt(Rs_name, all_peaks, delimiter=',')
        savetxt(ECG_name, ecg_clean, delimiter=',')

# 7. Close window to exit
window.close()



