import string
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from shutil import *
import requests
import json
import datetime
import cpuinfo
#
# ---------------     ABOUT    ----------------
# Real-time monitoring tool for DEFORM FEM simulation by reading and plotting data from .MSG files.
# Written by Fang Shi, assisted by YanShun Hou.
# ---------------  Python lib  ----------------
# pip install numpy
# pip install matplotlib
# pip install requests
# pip install py-cpuinfo
# ---------------  Version log ----------------
# Version 1.0  (2023-07-31)
# Version 1.1  (2023-07-31): Bug fix.
# Version 1.2  (2023-07-31): Read from copy.
# Version 1.3  (2023-07-31): Auto update.
# Version 1.4  (2023-07-31): Add plots.
# Version 1.5  (2023-07-31): Bug fix: folder has more than 2 MSG files.
# Version 1.6  (2023-07-31): Minor revison.
# Version 1.7  (2023-07-31): Bug fix.
# Version 1.8  (2023-07-31): Save data in memory; save data to txt file.
# Version 1.9  (2023-07-31): Add user figure title.
# Version 1.10 (2023-08-01): Send notification to phone when the ring stops.
# Version 1.11 (2023-08-01): Bug fix for notification.
# Version 1.12 (2023-08-02): Improvements.
# Version 1.13 (2023-08-02): Save to png files.
# Version 1.14 (2023-08-02): Save txt every 5 plots.
# Version 1.15 (2023-08-02): Reduce notifiction sending frenquency.
# Version 1.16 (2023-08-03): Bug fix.
# Version 1.17 (2023-08-05): Plot grid; Improvements..
#

#*********************************
#  Parameter settings.
#*********************************
Plot_Figure  = True
Save_Data    = True
Send_Message = True
Font_Size    = 10  #Set font size
Figure_Title = ' ' #Type the case name here
Figure_Grid  = 'True'

#*********************************
#  Search for .msg files in the current folder.
#*********************************
# Get current directory
current_dir = os.getcwd()
# Check if there are any files with the '.MSG' extension in the current folder.
msg_files = [file for file in os.listdir(current_dir) if file.endswith(".MSG")]
if(msg_files):
    msg_file_falg=True
    #Read .MSG files that meet the size requirements.
    for i_Read in range(0,len(msg_files)):
        msg_file = msg_files[i_Read]
        msg_file_info = os.stat(msg_file)
        msg_file_size = msg_file_info.st_size
        # print(msg_file_size)
        if(msg_file_size>100.0):  #Greater than 100 bytes
            msg_file = msg_files[i_Read]
            break
    msg_file_path = os.path.join(current_dir, msg_file)
    msg_copy_file = 'READ_MSG.MSG'
else:
    msg_file_falg=False
    print('ERROR :: Can not find msg file.')
    print('Sleep for 100000 second then exit.')
    time.sleep(100000)

#*********************************
#    Start time.
#*********************************
start_time     = time.time()
CPU_Time       = np.array([], dtype=float) #Define an empty array of floating-point numbers.
Rolling_Time   = np.array([], dtype=float) #Define an empty array of floating-point numbers.

#---------------------------
#  Data initialization.
#---------------------------
DATA_step_number  = np.array([], dtype=int)   #Define an empty array of integers.
DATA_time         = np.array([], dtype=float) #Define an empty array of floating-point numbers.
DATA_R_out        = np.array([], dtype=float) #Define an empty array of floating-point numbers.
DATA_R_in         = np.array([], dtype=float) #Define an empty array of floating-point numbers.
DATA_Revol        = np.array([], dtype=float) #Define an empty array of floating-point numbers.
Max_Plot_Step     = -1

#---------------------------
#  send_ifttt_notice.
#---------------------------
IFTTT_Key = 'ZlKCDYxrWncNulam0ew4G'
def send_ifttt_notice(event_name, key, *args):
    url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{key}"
    text_list = []
    for text in args:
        text_list.append(text)
    payload = {"value1": text_list[0], "value2": text_list[1], "value3": text_list[2]}
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    print(text_list)
    print(response.text)
    
#*********************************
#  Start plotting and save the data.
#*********************************
for i_Plot in range(1,1000000):
    this_plot_send_notification = False
    ring_stop_count = 0 
    print('\n'+'Plot count:', str(i_Plot)) 
    
    # CPU_Time.
    CPU_Time   = np.append(CPU_Time,float(time.time() - start_time))
    
    #---------------------------
    #  Read file.
    #---------------------------   
    copyfile(msg_file_path, msg_copy_file)    
    msg_file = open(msg_copy_file,"r")    
    while True:
        #Read one line.
        current_Line = msg_file.readline()  #Current line.
        if current_Line:
            # If the line is not empty.
            if len(current_Line)>0:
                current_Line = current_Line.strip() # Remove leading spaces.
                if(current_Line[0:11]=='STEP NUMBER'):  #If the line starts with 'STEP NUMBER'.
                    current_step_number = int(current_Line[23:])  #The equal sign is at position 23.
                    if(current_step_number>Max_Plot_Step):
                        Max_Plot_Step  = current_step_number
                        DATA_step_number = np.append(DATA_step_number, current_step_number) #Add an element to the array.
                if(current_Line[0:11]=='Time/Stroke'):  #If the line starts with 'Time/Stroke'.
                    if(current_step_number>=Max_Plot_Step):
                        current_time = float(current_Line[16:27]) 
                        DATA_time = np.append(DATA_time, current_time) #Add elements to array.
                if(current_Line[0:9]=='Rmax/min:'):  #If the line starts with 'Rmax/min'.
                    if(current_step_number>=Max_Plot_Step):
                        current_Rmax = float(current_Line[11:22]) 
                        current_Rmin = float(current_Line[23:35]) 
                        DATA_R_out = np.append(DATA_R_out, current_Rmax) #Add elements to array.
                        DATA_R_in  = np.append(DATA_R_in, current_Rmin) #Add elements to array.
                if(current_Line[0:22]=='Tot Rotation(deg/rev):'):  #If the line starts with 'Tot Rotation(deg/rev)'.
                    if(current_step_number>=Max_Plot_Step):
                        current_Revol = float(current_Line[36:49]) 
                        DATA_Revol  = np.append(DATA_Revol, current_Revol) #Add elements to array.
                if(current_Line[0:22]=='Current Rotation(deg):'):  #If the line starts with 'Current Rotation(deg)'.
                    if(current_step_number>=Max_Plot_Step):
                        current_Rotation = float(current_Line[23:38]) 
                        #If the calculation has lasted more than 10 minutes.
                        current_elapsed_time = float(time.time() - start_time)
                        if(current_elapsed_time > 10.0*60.0):
                            if(current_Rotation<0.0000001): 
                                ring_stop_count = ring_stop_count + 1
                                if(ring_stop_count>=2):  #If more than two steps are stalled.
                                    if(Send_Message):    #If message sending is enabled. v1.17.
                                        if(np.mod(i_Plot,5)==0): #Send message every 5 plots. v1.15.
                                            if(this_plot_send_notification == False):  #If current plot notification has not been sent. v1.11.
                                                this_plot_send_notification = True
                                                IFTTT_Text1 = 'Step number-'+str(current_step_number)+'; CPU-'+str(cpuinfo.get_cpu_info()['brand_raw'])+';'
                                                IFTTT_Text2 = 'Case name-'+Figure_Title+'; Rolling time-'+str(current_time)+';'
                                                IFTTT_Text3 = 'Time-' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
                                                send_ifttt_notice('deform_simulation',IFTTT_Key, IFTTT_Text1,IFTTT_Text2,IFTTT_Text3) 

        else:
            break
            
    msg_file.close()

    # Rolling_Time.
    if('current_time' in vars()):
        Rolling_Time   = np.append(Rolling_Time,current_time) 
    
    # Delete file(s).
    os.remove(msg_copy_file)
    
    # Time spent. 
    print('\n'+'Elapsed time: {:.2f} s.'.format(time.time() - start_time)) 
    
    #---------------
    # Save data.
    #---------------
    if(Save_Data):
        if(np.mod(i_Plot,5)==0):
            np.savetxt('DATA_step_number_'+str(Max_Plot_Step)+'.txt',DATA_step_number) 
            np.savetxt('DATA_time_'       +str(Max_Plot_Step)+'.txt',DATA_time) 
            np.savetxt('DATA_R_out_'      +str(Max_Plot_Step)+'.txt',DATA_R_out) 
            np.savetxt('DATA_R_in_'       +str(Max_Plot_Step)+'.txt',DATA_R_in) 
            np.savetxt('DATA_Revol_'      +str(Max_Plot_Step)+'.txt',DATA_Revol) 
    
    #------------------------
    # Plot curve.
    #------------------------
    if(Plot_Figure):    
        # Plot simulation step-time curve.
        fig = plt.figure(figsize=(13,8))
        fig.canvas.manager.set_window_title(Figure_Title) 
        plt.subplot(231)
        min_len = min(len(DATA_step_number),len(DATA_time))
        plt.plot(DATA_step_number[0:min_len], DATA_time[0:min_len])
        plt.xlabel("Step number",fontsize=Font_Size)
        plt.ylabel("Rolling time (s)",fontsize=Font_Size)
        plt.title("Step number - Rolling time Figure",fontsize=Font_Size)
        if(Figure_Grid):    # Mesh
            plt.grid()
            
        # Plot simulation step-diameter curve.
        plt.subplot(232)
        min_len = min(len(DATA_step_number),len(DATA_R_out))
        plt.plot(DATA_step_number[0:min_len], 2.0*DATA_R_out[0:min_len])
        plt.xlabel("Step number",fontsize=Font_Size)
        plt.ylabel("Outer diameter (mm)",fontsize=Font_Size)
        plt.title("Step number - Outer diameter Figure",fontsize=Font_Size)
        if(Figure_Grid):    # Mesh
            plt.grid()
            
        # Plot simulation step-inner diameter curve.
        plt.subplot(233)
        min_len = min(len(DATA_step_number),len(DATA_R_in))
        plt.plot(DATA_step_number[0:min_len], 2.0*DATA_R_in[0:min_len])
        plt.xlabel("Step number",fontsize=Font_Size)
        plt.ylabel("Inner diameter (mm)",fontsize=Font_Size)
        plt.title("Step number - Inner diameter Figure",fontsize=Font_Size)
        if(Figure_Grid):    # Mesh
            plt.grid()
            
        # Plot time-diameter curve.
        plt.subplot(234)
        min_len = min(len(DATA_time),len(DATA_R_out))
        plt.plot(DATA_time[0:min_len], 2.0*DATA_R_out[0:min_len])
        plt.xlabel("Rolling time (s)",fontsize=Font_Size)
        plt.ylabel("Outer diameter (mm)",fontsize=Font_Size)
        plt.title("Rolling time - Outer diameter Figure",fontsize=Font_Size)
        if(Figure_Grid):    # Mesh
            plt.grid()
            
        # Plot time-rotation cycles curve.
        plt.subplot(235)
        min_len = min(len(DATA_time),len(DATA_Revol))
        plt.plot(DATA_time[0:min_len], DATA_Revol[0:min_len])
        plt.xlabel("Rolling time (s)",fontsize=Font_Size)
        plt.ylabel("Rotation (round)",fontsize=Font_Size)
        plt.title("Rolling time - Rotation Figure",fontsize=Font_Size)
        if(Figure_Grid):    # Mesh
            plt.grid()
            
        # Plot CPU time-Rolling time curve.
        plt.subplot(236)
        min_len = min(len(CPU_Time),len(Rolling_Time))
        plt.plot(CPU_Time[0:min_len]/60.0/60.0, Rolling_Time[0:min_len])
        plt.xlabel("CPU time (hour)",fontsize=Font_Size)
        plt.ylabel("Rolling time (s)",fontsize=Font_Size)
        plt.title("CPU time - Rolling time Figure",fontsize=Font_Size)
        if(Figure_Grid):    # Mesh
            plt.grid()
            
        # Prevent plot overlapping.
        plt.tight_layout()
        
        # Plot all figures.
        plt.show(block = False)
        
        # Save figures every 5 plots.
        if(np.mod(i_Plot,5)==0):
            png_title = Figure_Title+'_figue_of_step_'+str(current_step_number)+'.png'
            plt.savefig(png_title,dpi=300) 
        
        # Plot every 120 seconds.
        plt.pause(120)
        # plt.pause(20)
        
        # Close figure
        plt.close()
    

print('\n'+'All done.')
