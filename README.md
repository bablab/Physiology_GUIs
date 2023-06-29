# Physiology_GUIs

Author: Paul Savoca

Email: ps365@g.ucla.edu

Twitter: @pw_savoca

Lab: Brain and Body Lab, UCLA

# Neurokit2 ECG GUI (nk_ecg_gui.py)
This application is intended for manual editing of ECG data from .Acq files. 
The GUI allows for manual checking and editting of R-peaks which are initially detected using the Neurokit2 (Makowski et al., 2020).

The application generates 2 output files: 

1. the filtered ECG signal
2. the finalized set of R-peaks

These files can then be used for ECG-based analyses (e.g., IBI, HRV, ect.)

### Installation & Running
1. Download 'nk_ecg_gui.py'
   * Sample Physiology Data (acquired at 2kHz) is also available: NK_ECG_GUI/Sample_Data/Sample_Physio_2kHz.acq
3. Install necessary dependencies:
  * numpy
  * neurokit2
  * PySimpleGUI
  * matplotlib
  * mpl_point_clicker
  * os
  * bioread   
4. To start application -- From command line: 'python nk_ecg_gui.py'
