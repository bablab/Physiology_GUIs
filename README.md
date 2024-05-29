# Physiology_GUIs

Author: Paul Savoca

Email: ps365@g.ucla.edu

Twitter: @pw_savoca

Lab: Brain and Body Lab, UCLA

# Neurokit2 ECG GUI (nk_ecg_gui.py)
This application is intended for manual editing of ECG data from .Acq files. 
The GUI allows for manual checking and editting of R-peaks which are initially detected using the Neurokit2 (Makowski et al., 2020).

As of May 2024, you can also edit ECG data stored as a time-series in a .Csv file. The data must be stored as a single column with no header. The application will prompt you to manually enter the sampling rate of your data.

The application generates 2 output files: 

1. the filtered ECG signal
2. the finalized set of R-peaks

These files can then be used for ECG-based analyses (e.g., IBI, HRV, ect.)

### Installation & Running
1. Download ['nk_ecg_gui.py'](https://github.com/bablab/Physiology_GUIs/blob/main/NK_ECG_GUI/nk_ecg_gui.py)
   * Sample Physiology Data (acquired at 2kHz) is also available: NK_ECG_GUI/Sample_Data/[Sample_Physio_2kHz.acq](https://github.com/bablab/Physiology_GUIs/blob/main/NK_ECG_GUI/Sample_Data/Sample_Physio_2kHz.acq)
3. Install necessary dependencies:
  * 'pip install numpy neurokit2 PySimpleGUI matplotlib mpl_point_clicker bioread'
4. To start application -- From command line: 'python nk_ecg_gui.py'

### Using Neurokit2 ECG GUI
After selecting the .acq file you want to clean, select the channel containing your ECG data and the notch filter you wish to use:
<img width="614" alt="nk_gui_settings" src="https://github.com/bablab/Physiology_GUIs/assets/116229946/aed2c77d-4653-472b-b08a-9d289bf3564c">

You can then visualize your ECG Data. Zoom and Scroll through data using toolbar:
<img width="1149" alt="nk_gui_viewECG" src="https://github.com/bablab/Physiology_GUIs/assets/116229946/d5062414-bb42-49aa-9faa-e265f573f30e">

You can manually added missing peaks using the "Add Peak" function and then clicking where you would like to add the r-peak. It will automatically "snap" to nearest peak:
<img width="1083" alt="nk_gui_addPeak" src="https://github.com/bablab/Physiology_GUIs/assets/116229946/4b9c1909-2892-4cd0-98a5-9fed83530b5d">

Alternatively, you can use the "Remove Peak" to identify peaks that were erronously detected, and you wish to be removed from analyses:
<img width="1088" alt="nk_gui_removePeak" src="https://github.com/bablab/Physiology_GUIs/assets/116229946/3767c495-cd4e-4150-a882-bf8623003b05">



