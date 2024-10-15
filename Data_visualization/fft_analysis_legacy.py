import numpy as np
import matplotlib.pyplot as plt
import time
import os
from scipy.fftpack import fft, fftfreq
import numpy as np
import re #import regular expression for extracting file names
from scipy.io import loadmat
from scipy.signal import butter, filtfilt, zpk2sos, sosfiltfilt
from scipy.ndimage import binary_dilation
import concurrent.futures
from skimage.measure import label
import sys
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.attributes("-topmost", True)
root.withdraw()

# Global variable declaration
# Data_file_names = [['SD1_dataFile_002.dat','SD2_dataFile_002.dat']]
def process_DAQ_data(SD_file, Fs_sensor):
    """Processes DAQ data file, converts to voltage, and extracts sensor data.

    Args:
        SD_file: Path to the DAQ data file.
        Fs_sensor: Data sampling frequency.

    Returns:
        A dictionary containing sensor data as NumPy arrays.
    """
    SD_sensor_data = []  # List to store sensor data
    # Read binary data
    SD_Data_file_ID = open(SD_file, "rb")  # sensation data will be the first element in the cell by default
    SD_data_original = np.fromfile(SD_Data_file_ID, dtype=np.int32)

    # Reshape data
    n = 17  # Number of columns in converted data
    m = len(SD_data_original) // n
    SD_data = SD_data_original.reshape((m, n))
    # SD_data = np.zeros((m, n))  # variable for storing the converted data


    # Create empty lists for sensor data
    sensor_data = {
        "A0": [], "A1": [], "A2": [], "A3": [], "A4": [],
        "A5": [], "A6": [], "A7": [], "Aclm_X": [], "Aclm_Y": [], "Aclm_Z": [],
        "Gyro_X": [], "Gyro_Y": [], "Gyro_Z": [], "Mag_X": [],
        "Mag_Y": [], "Mag_Z": []
    }

    # ADC conversion parameters (assuming potentially different resolutions)
    adc_resolutions = {  # Dictionary for sensor-specific ADC resolutions
        "A0": 13, "A1": 13, "A2": 13, "A3": 13, "A4": 13,
        "A5": 13, "A6": 13, "A7": 13,
        "Aclm_X": 16, "Aclm_Y": 16, "Aclm_Z": 16,
        "Gyro_X": 16, "Gyro_Y": 16, "Gyro_Z": 16,
        "Mag_X": 16, "Mag_Y": 16, "Mag_Z": 16
    }

    # Extract and convert sensor data
    i = 0
    for sensor_name in adc_resolutions:
        adc_resolution = adc_resolutions[sensor_name]
        max_adc_value = 2**adc_resolution - 1
        slope = 3.3 / max_adc_value
        # sensor_index = int(sensor_name[1:])  # Extract the numeric part of the sensor name
        sensor_data[sensor_name] = SD_data[:, i] * slope
        SD_sensor_data.append(sensor_data[sensor_name])
        i = i + 1

    # Calculate data points
    n = len(sensor_data["A0"])
    m = n % 256

    print('Data conversion is successful.')
    print(f'Total data point: {n}')
    print(f'Data point less than 512: {m}')

    # plot the first sensor data
    # time_vector = np.arange(len(sensor_data["Mag_Z"])) / Fs_sensor
    # plt.figure(figsize=(10, 5))
    # plt.plot(time_vector, sensor_data["Mag_Z"], label='A0 Sensor')
    # plt.title('Sensor Data A0')
    # plt.xlabel('Time (s)')
    # plt.ylabel('Sensor Output (a.u.)')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    return sensor_data




def visualize_sensor_data(sensor_data, database_name, Fs_sensor):
    """Visualizes sensor data from the provided dictionary.

    Args:
        sensor_data: A dictionary containing sensor data as NumPy arrays. Keys should
                     correspond to sensor names (e.g., "A0", "A1", etc.).
        Fs_sensor: Data sampling frequency.
        database_name: Name to use for saving the visualization.
    """

    # Create the visual directory if it doesn't exist (optional)
    if not os.path.exists('visual'):
        os.makedirs('visual')

    # Calculate time vector
    time_vector = np.arange(len(sensor_data["A0"])) / Fs_sensor

    # Create subplots for the first 5 sensors
    fig, axs = plt.subplots(8, 1, figsize=(15, 15))  # Adjust figsize as needed
    for i, sensor_name in enumerate(list(sensor_data.keys())[:8]):
        axs[i].plot(time_vector, sensor_data[sensor_name], label=sensor_name)
        axs[i].set_title(f'{sensor_name} Sensor Data')
        axs[i].set_xlabel('Time (s)')
        axs[i].set_ylabel('Sensor Output (a.u.)')
        axs[i].legend()
        axs[i].grid(True)

    # Save the first plot
    plt.tight_layout()
    plt.savefig(f'./visual/test_{database_name}_blink.png', dpi=300)
    plt.clf()

    # Create subplots for the next 5 sensors
    fig, axs = plt.subplots(9, 1, figsize=(20, 15))  # Adjust figsize as needed
    for i, sensor_name in enumerate(list(sensor_data.keys())[8:18]):
        axs[i].plot(time_vector, sensor_data[sensor_name], label=sensor_name)
        axs[i].set_title(f'{sensor_name} Sensor Data')
        axs[i].set_xlabel('Time (s)')
        axs[i].set_ylabel('Sensor Output (a.u.)')
        axs[i].legend()
        axs[i].grid(True)

    # Save the second plot
    plt.tight_layout()
    plt.savefig(f'./visual/test_{database_name}_IMU.png', dpi=300)
    plt.clf()

    # Create subplots for the last 9 sensors
    fig, axs = plt.subplots(9, 1, figsize=(15, 12))  # Adjust figsize as needed
    for i, sensor_name in enumerate(list(sensor_data.keys())[10:]):
        # row = i // 3
        # col = i % 3
        axs[i].plot(time_vector, sensor_data[sensor_name], label=sensor_name)
        axs[i].set_title(f'{sensor_name} Sensor Data')
        axs[i].set_xlabel('Time (s)')
        axs[i].set_ylabel('Sensor Output (a.u.)')
        axs[i].legend()
        axs[i].grid(True)

    # Save the third plot
    plt.tight_layout()
    plt.savefig(f'./visual/{database_name}_part3.png', dpi=300)
    plt.clf()


# call the function
#Pzplt_data_1, Pzplt_data_2 = process_DAQ_data(f'G:/Job_AKG/eye_blink_stuff/binary_file_reading/Data00.dat')
# please change the directory to the data file directory if needed
try:
    print("Please select the data file directory")
    initial_dir = f'G:/DATA Visualization/Data_visualization_v5/datafile'  # Define database_dir before using it
    database_dir = filedialog.askdirectory(initialdir=initial_dir)
except:
    # exit
    sys.exit("No directory is selected")
    database_dir = f"H:/MAIMLab/Eye_gesture_recognition/Datafile"
    print("Default directory is used: {}".format(database_dir))
# from the database directory .dat format data load and pass to the process_DAQ_data function
database = []
for root,dirs, files in os.walk(database_dir):
    for file in files:
        if file.endswith('.dat'):
            database.append(file)
database = sorted(database)
print(database)
for i in range(len(database)):
    sensor_data = process_DAQ_data(f"{database_dir}/{database[i]}", Fs_sensor=256)
    visualize_sensor_data(sensor_data, database[i][:-4], Fs_sensor=256)
  



def FFT(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, database_name, Fs_sensor):
    # Perform FFT on both sensor data
    fft_result1 = fft(Pzplt_data_1)
    fft_result2 = fft(Pzplt_data_2)
    fft_result3 = fft(Pzplt_data_3)
    fft_result4 = fft(Pzplt_data_4)
    fft_result5 = fft(Pzplt_data_5)

    # Compute the absolute value of the FFT results to get the magnitude spectrums
    magnitude_spectrum1 = np.abs(fft_result1)
    magnitude_spectrum2 = np.abs(fft_result2)
    magnitude_spectrum3 = np.abs(fft_result3)
    magnitude_spectrum4 = np.abs(fft_result4)
    magnitude_spectrum5 = np.abs(fft_result5)

    # Compute the frequencies corresponding to the FFT values
    frequencies1 = fftfreq(len(Pzplt_data_1), 1/Fs_sensor)
    frequencies2 = fftfreq(len(Pzplt_data_2), 1/Fs_sensor)
    frequencies3 = fftfreq(len(Pzplt_data_3), 1/Fs_sensor)
    frequencies4 = fftfreq(len(Pzplt_data_4), 1/Fs_sensor)
    frequencies5 = fftfreq(len(Pzplt_data_5), 1/Fs_sensor)

    # Only consider the first half of the FFT result and corresponding frequencies
    half_length = len(Pzplt_data_1) // 2
    magnitude_spectrum1 = magnitude_spectrum1[:half_length]
    magnitude_spectrum2 = magnitude_spectrum2[:half_length]
    magnitude_spectrum3 = magnitude_spectrum3[:half_length]
    magnitude_spectrum4 = magnitude_spectrum4[:half_length]
    magnitude_spectrum5 = magnitude_spectrum5[:half_length]
    frequencies1 = frequencies1[:half_length]
    frequencies2 = frequencies2[:half_length]
    frequencies3 = frequencies3[:half_length]
    frequencies4 = frequencies4[:half_length]
    frequencies5 = frequencies5[:half_length]

    # Plot the magnitude spectrums against the frequencies
    #plt.figure(figsize=(10, 5))
    #plt.plot(frequencies1, magnitude_spectrum1, label='A1 Sensor 1')

    fig, axs = plt.subplots(5, figsize=(20, 30))
    #Figure 1--------------------------------------------------------------
    axs[0].plot(frequencies2, magnitude_spectrum2, label='A1 Sensor 2')
    axs[0].set_title('FFT of Sensor Data A1')
    axs[0].set_xlabel('Frequency (Hz)')
    axs[0].set_ylabel('Magnitude')
    axs[0].legend()
    axs[0].grid(True)
    axs[0].set_ylim(0, 500)
    axs[0].set_xlim(0, 256)  # Limit the x-axis to 0-100 Hz
    #plt.savefig('./visual/FFT A1.png', dpi=300)
    # plt.show()

    #plt.figure(figsize=(10, 5))
    #Figure 2--------------------------------------------------------------
    axs[1].plot(frequencies1, magnitude_spectrum1, label='A0 Sensor 1',color='orange')
    axs[1].set_title('FFT of Sensor Data A0')
    axs[1].set_xlabel('Frequency (Hz)')
    axs[1].set_ylabel('Magnitude')
    axs[1].legend()
    axs[1].grid(True)
    axs[1].set_ylim(0, 500)
    axs[1].set_xlim(0, 256)  # Limit the x-axis to 0-100 Hz
    #plt.savefig('./visual/FFT A0.png', dpi=300)
    # plt.show()
    
    #plt.figure(figsize=(10, 5))
    #Figure 3--------------------------------------------------------------
    axs[2].plot(frequencies3, magnitude_spectrum3, label='A2 Sensor 3',color='orange')
    axs[2].set_title('FFT of Sensor Data A2')
    axs[2].set_xlabel('Frequency (Hz)')
    axs[2].set_ylabel('Magnitude')
    axs[2].legend()
    axs[2].grid(True)
    axs[2].set_ylim(0, 500)
    axs[2].set_xlim(0, 256)  # Limit the x-axis to 0-100 Hz
    #plt.savefig('./visual/FFT A2.png', dpi=300)
    # plt.show()
    #plt.figure(figsize=(10, 5))
    #Figure 4--------------------------------------------------------------
    axs[3].plot(frequencies4, magnitude_spectrum4, label='A3 Sensor 4',color='orange')
    axs[3].set_title('FFT of Sensor Data A3')
    axs[3].set_xlabel('Frequency (Hz)')
    axs[3].set_ylabel('Magnitude')
    axs[3].legend()
    axs[3].grid(True)
    axs[3].set_ylim(0, 500)
    axs[3].set_xlim(0, 256)  # Limit the x-axis to 0-100 Hz
    #plt.savefig('./visual/FFT A3.png', dpi=300)
    # plt.show()
    #plt.figure(figsize=(10, 5))
    #Figure 5--------------------------------------------------------------
    axs[4].plot(frequencies5, magnitude_spectrum5, label='A4 Sensor 5',color='orange')
    axs[4].set_title('FFT of Sensor Data A4')
    axs[4].set_xlabel('Frequency (Hz)')
    axs[4].set_ylabel('Magnitude')
    axs[4].legend()
    axs[4].grid(True)
    axs[4].set_ylim(0, 500)
    axs[4].set_xlim(0, 256)  # Limit the x-axis to 0-100 Hz
    #plt.savefig('./visual/FFT A4.png', dpi=300)
    # plt.show()

    plt.tight_layout()
    plt.savefig(f'./visual/fft_{database_name}.png', dpi=600)
    plt.clf()

def band_pass(database_name, Pzplt_data1, Pzplt_data2, Pzplt_data3, Pzplt_data4, Pzplt_data5, lowCutoff_FM, highCutoff_FM, Fs_sensor):
    # ================Bandpass filter design==========================
    #   A band-pass filter with a passband of 1-30 Hz is disigned for the eye blink data

    # Filter setting
    filter_order = 10

    # ========SOS-based design
    #Get second-order sections form
    sos_FM  = butter(filter_order / 2, np.array([lowCutoff_FM, highCutoff_FM]) / (Fs_sensor / 2), 'bandpass', output='sos')# filter order for bandpass filter is twice the value of 1st parameter


    # -----------------------Digital Data filtering (Bandpass filtering)--------------------------------
    Pzplt_data_fltd_1= sosfiltfilt(sos_FM,  Pzplt_data1[0])
    Pzplt_data_fltd_2= sosfiltfilt(sos_FM,  Pzplt_data2[0])
    Pzplt_data_fltd_3= sosfiltfilt(sos_FM,  Pzplt_data3[0])
    Pzplt_data_fltd_4= sosfiltfilt(sos_FM,  Pzplt_data4[0])
    Pzplt_data_fltd_5= sosfiltfilt(sos_FM,  Pzplt_data5[0])

    # -----------------------Data visualization----------------------------
    time_vector = np.arange(len(Pzplt_data1[0][0*1000:])) / Fs_sensor
    max_sample = np.maximum(Pzplt_data_fltd_1,Pzplt_data_fltd_2)
    max_sample = np.maximum(max_sample,Pzplt_data_fltd_3)
    max_sample = np.maximum(max_sample,Pzplt_data_fltd_4)
    max_sample = np.maximum(max_sample,Pzplt_data_fltd_5)

    # fig, axs = plt.subplots(6, figsize=(20, 30))

    # # Plot original and filtered data
    # #-------------------Figure_1----------------------------
    # axs[0].set_title('Digital Band Pass Sensor A0')
    # axs[0].plot(time_vector, Pzplt_data_fltd_1, color='brown', label='A0 Sensor')
    # axs[0].set_xlabel('Time (s)')
    # axs[0].set_ylabel('Sensor Output (a.u.)')
    # axs[0].legend()
    # axs[0].grid(True)


    # #-------------------Figure_2----------------------------
    # axs[1].set_title('Digital Band Pass Sensor A1')
    # axs[1].plot(time_vector, Pzplt_data_fltd_2, color='brown', label='A1 Sensor')
    # axs[1].set_xlabel('Time (s)')
    # axs[1].set_ylabel('Sensor Output (a.u.)')
    # axs[1].legend()
    # axs[1].grid(True)


    # #-------------------Figure_3----------------------------
    # axs[2].set_title('Digital Band Pass Sensor A2')
    # axs[2].plot(time_vector, Pzplt_data_fltd_3, color='brown', label='A2 Sensor')
    # axs[2].set_xlabel('Time (s)')
    # axs[2].set_ylabel('Sensor Output (a.u.)')
    # axs[2].legend()
    # axs[2].grid(True)



    # #-------------------Figure_4----------------------------
    # axs[3].set_title('Digital Band Pass Sensor A3')
    # axs[3].plot(time_vector, Pzplt_data_fltd_4, color='brown', label='A3 Sensor')
    # axs[3].set_xlabel('Time (s)')
    # axs[3].set_ylabel('Sensor Output (a.u.)')
    # axs[3].legend()
    # axs[3].grid(True)

    # #-------------------Figure_5----------------------------
    # axs[4].set_title('Digital Band Pass Sensor A4')
    # axs[4].plot(time_vector, Pzplt_data_fltd_5, color='brown', label='A4 Sensor')
    # axs[4].set_xlabel('Time (s)')
    # axs[4].set_ylabel('Sensor Output (a.u.)')
    # axs[4].legend()
    # axs[4].grid(True)


    # #-------------------Figure_5----------------------------
    # axs[5].set_title('Fused Digital Band Pass data by Non_Max_Suppression')
    # axs[5].plot(time_vector, max_sample, color='purple', label='Piezo Sensor')
    # axs[5].set_xlabel('Time (s)')
    # axs[5].set_ylabel('Sensor Output (a.u.)')
    # axs[5].legend()
    # axs[5].grid(True)


    # plt.tight_layout()
    # # plt.savefig(f'./visual/Digital_Bandpass.png', dpi=600)
    # plt.savefig(f'./visual/Digital_Bandpass_{database_name}.png', dpi=600)
    # plt.clf()

    return Pzplt_data_fltd_1, Pzplt_data_fltd_2, Pzplt_data_fltd_3, Pzplt_data_fltd_4, Pzplt_data_fltd_5
    
def SNR_dB(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, Fs_sensor):
    # SNR calculation
    # user can choose how many sensors the device contains
    # noise lenght should be first 15 seconds of the data and the signal length should be the 15-40 seconds of the data
    # noise data is used to calculate the noise RMS and signal data is used to calculate the signal RMS
    # SNR is calculated by the formula SNR = 20*log10(Signal_RMS/Noise_RMS)
    # SNR is calculated for each sensor data
    # After calculating for each sensor, the max SNR is selected as the SNR of the device
    # The SNR is calculated in dB
    # dB means decibel. e.g. SNR 3dB increase 2 times of the signal power, 6dB means 4 times increase in signal power
    # n = int(input("Enter the number of sensors you want to calculate SNR in dB: "))
    
    noise_start = int(input("Enter the start time of the noise data in seconds: "))
    noise_end = int(input("Enter the end time of the noise data in seconds: "))
    signal_start = int(input("Enter the start time of the signal data in seconds: "))
    signal_end = int(input("Enter the end time of the signal data in seconds: "))


    SNR_dB = []
    

    for Pzplt_data, sensor_num in zip([Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5], ['1', '2', '3', '4', '5']):

        # print(Pzplt_data)
        
        noise_data = Pzplt_data[noise_start*Fs_sensor:noise_end*Fs_sensor]
        noise_mean = np.mean(noise_data)

        signal_data = Pzplt_data[signal_start*Fs_sensor:signal_end*Fs_sensor]
        signal_mean = np.mean(signal_data)

        noise_RMS = np.sqrt(np.mean(noise_data**2))
        signal_RMS = np.sqrt(np.mean(signal_data**2))
        SNR = 20*np.log10(signal_RMS/noise_RMS)
        SNR_dB.append(SNR)

        if sensor_num == '1' or '2': # remove it while using 5 sensors
            print(f"SNR of sensor Pzplt_{sensor_num} is {SNR} dB")
        # print(f"Signal mean {signal_mean}")
        # print(f"noise mean {noise_mean}")



    
    max_SNR = max(SNR_dB)
    print(f"Max SNR of the device is {max_SNR} dB")

def SNR_dB_bgnm(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, Fs_sensor):
    # SNR calculation
    # user can choose how many sensors the device contains
    # noise lenght should be first 15 seconds of the data and the signal length should be the 15-40 seconds of the data
    # noise data is used to calculate the noise RMS and signal data is used to calculate the signal RMS
    # SNR is calculated by the formula SNR = 20*log10(Signal_RMS/Noise_RMS)
    # SNR is calculated for each sensor data
    # After calculating for each sensor, the max SNR is selected as the SNR of the device
    # The SNR is calculated in dB
    # dB means decibel. e.g. SNR 3dB increase 2 times of the signal power, 6dB means 4 times increase in signal power
    # n = int(input("Enter the number of sensors you want to calculate SNR in dB: "))
    
    noise_start = int(input("Enter the start time of the noise data in seconds: "))
    noise_end = int(input("Enter the end time of the noise data in seconds: "))
    signal_start = int(input("Enter the start time of the signal data in seconds: "))
    signal_end = int(input("Enter the end time of the signal data in seconds: "))


    SNR_dB = []
    

    for Pzplt_data, sensor_num in zip([Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5], ['1', '2', '3', '4', '5']):

        # print(Pzplt_data)
        
        noise_data = Pzplt_data[noise_start*Fs_sensor:noise_end*Fs_sensor]
    
        noise_mean = np.mean(noise_data)

        signal_data = Pzplt_data[0][signal_start*Fs_sensor:signal_end*Fs_sensor]
        signal_mean = np.mean(signal_data)

        noise_data = noise_data - noise_mean
        signal_data = signal_data - noise_mean

        plt.figure()
        plt.plot(noise_data[0])
        plt.show()

        noise_RMS = np.sqrt(np.mean(noise_data[0]**2))
        signal_RMS = np.sqrt(np.mean(signal_data[0]**2))
        SNR = 20*np.log10(signal_RMS/noise_RMS)
        SNR_dB.append(SNR)
        if sensor_num == '1' or '2': # remove it while using 5 sensors
            print(f"SNR of sensor Pzplt_{sensor_num} is {SNR} dB")
        # print(f"Signal mean {signal_mean}")
        # print(f"noise mean {noise_mean}")



    
    max_SNR = max(SNR_dB)
    print(f"Max SNR of the device is {max_SNR} dB")

def SNR_dB_AKG(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, Fs_sensor):
    # SNR calculation
    # user can choose how many sensors the device contains
    # noise lenght should be first 15 seconds of the data and the signal length should be the 15-40 seconds of the data
    # noise data is used to calculate the noise RMS and signal data is used to calculate the signal RMS
    # SNR is calculated by the formula SNR = 20*log10(Signal_RMS/Noise_RMS)
    # SNR is calculated for each sensor data
    # After calculating for each sensor, the max SNR is selected as the SNR of the device
    # The SNR is calculated in dB
    # dB means decibel. e.g. SNR 3dB increase 2 times of the signal power, 6dB means 4 times increase in signal power
    # n = int(input("Enter the number of sensors you want to calculate SNR in dB: "))
    
    noise_start = int(input("Enter the start time of the noise data in seconds: "))
    noise_end = int(input("Enter the end time of the noise data in seconds: "))
    signal_start = int(input("Enter the start time of the signal data in seconds: "))
    signal_end = int(input("Enter the end time of the signal data in seconds: "))


    SNR_dB = []
    

    for Pzplt_data, sensor_num in zip([Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5], ['1', '2', '3', '4', '5']):

        # print(Pzplt_data)
        
        noise_data = Pzplt_data[noise_start*Fs_sensor:noise_end*Fs_sensor]
    
        # noise_mean = np.mean(noise_data)
        

        signal_data = Pzplt_data[signal_start*Fs_sensor:signal_end*Fs_sensor]
        # signal_mean = np.mean(signal_data)

        E_signal = np.square(signal_data)
        E_signal = np.mean(E_signal)

        E_noise = np.square(noise_data)
        E_noise = np.mean(E_noise)

        SNR = 10*np.log10((E_signal - E_noise)/E_noise)
        
        SNR_dB.append(SNR)
        # if sensor_num == '1' or '2': # remove it while using 5 sensors
        print(f"SNR of sensor Pzplt_{sensor_num} is {SNR} dB")
        # print(f"Signal mean {signal_mean}")
        # print(f"noise mean {noise_mean}")



    
    max_SNR = max(SNR_dB)
    print(f"Max SNR of the device is {max_SNR} dB")

# def Non_max_Suppression(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5,Fs_sensor=512):
#     time_vector = np.arange(len(Pzplt_data_1[0])) / Fs_sensor
#     max_sample = np.maximum(Pzplt_data_1,Pzplt_data_2)
#     max_sample = np.maximum(max_sample,Pzplt_data_3)
#     max_sample = np.maximum(max_sample,Pzplt_data_4)
#     max_sample = np.maximum(max_sample,Pzplt_data_5)

#     #-----------------Figure-----------------------------------
#     plt.figure(figsize=(6, 4))
#     plt.plot(time_vector,max_sample[0],color='purple')
#     plt.xlabel('Time (s)')
#     plt.ylabel('Sensor Output (a.u.)')
#     plt.tight_layout()
#     plt.savefig(f'./visual/Non_Max_Suppression_Merge_Result.png', dpi=600)
#     plt.clf()


    

# # call the function
# #Pzplt_data_1, Pzplt_data_2 = process_DAQ_data(f'G:/Job_AKG/eye_blink_stuff/binary_file_reading/Data00.dat')
# # please change the directory to the data file directory if needed
# try:
#     print("Please select the data file directory")
#     initial_dir = f'H:/MAIMLab/Eye_gesture_recognition/Datafile'  # Define database_dir before using it
#     database_dir = filedialog.askdirectory(initialdir=initial_dir)
# except:
#     # exit
#     sys.exit("No directory is selected")
#     database_dir = f"H:/MAIMLab/Eye_gesture_recognition/Datafile"
#     print("Default directory is used: {}".format(database_dir))
# # from the database directory .dat format data load and pass to the process_DAQ_data function
# database = []
# for root,dirs, files in os.walk(database_dir):
#     for file in files:
#         if file.endswith('.dat'):
#             database.append(file)
# database = sorted(database)
# print(database)
# for i in range(len(database)):
#     Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5 = process_DAQ_data(f"{database_dir}/{database[i]}", Fs_sensor=512)
#     visual_sensor_data(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, database[i][:-4], Fs_sensor=512)
#     # FFT(Pzplt_data_1[0], Pzplt_data_2[0], Pzplt_data_3[0], Pzplt_data_4[0], Pzplt_data_5[0], database[i][:-4], Fs_sensor=512)
#     Pzplt_data_fltd_1, Pzplt_data_fltd_2, Pzplt_data_fltd_3, Pzplt_data_fltd_4, Pzplt_data_fltd_5 = band_pass(database[i][:-4], Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, lowCutoff_FM=1, highCutoff_FM=128, Fs_sensor=512) #L_0.54/0.81 H_14
#     # Non_max_Suppression(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, Fs_sensor=512)
#     print("SNR using band pass filtered signal---------------->")
#     SNR_dB(Pzplt_data_fltd_1, Pzplt_data_fltd_2, Pzplt_data_fltd_3, Pzplt_data_fltd_4, Pzplt_data_fltd_5, Fs_sensor=512)
#     SNR_dB_AKG(Pzplt_data_fltd_1, Pzplt_data_fltd_2, Pzplt_data_fltd_3, Pzplt_data_fltd_4, Pzplt_data_fltd_5, Fs_sensor=512)
#     # print("SNR using background mean normalized signal---------------->")
#     # SNR_dB_bgnm(Pzplt_data_1, Pzplt_data_2, Pzplt_data_3, Pzplt_data_4, Pzplt_data_5, Fs_sensor=512)

# Pzplt_data_1, Pzplt_data_2 = process_DAQ_data(f'{database_dir}')
# visual_sensor_data(Pzplt_data_1, Pzplt_data_2)
# FFT(Pzplt_data_1[0], Pzplt_data_2[0], 1000)
# band_pass(Pzplt_data_1, Pzplt_data_2,lowCutoff_FM=1, highCutoff_FM=20, Fs_sensor=1000) #L_0.54/0.81 H_14
