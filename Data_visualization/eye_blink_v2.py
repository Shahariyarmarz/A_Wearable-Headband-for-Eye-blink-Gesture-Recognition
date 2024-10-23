import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def detect_eye_blink(gesture_window_data, thresholds, min_points_above_threshold=4):
    """
    Detects eye blink signals within a given time window based on MMG sensor data.
    
    Args:
        gesture_window_data (dict): Contains the windowed MMG data for the gesture (A0 to A5).
        thresholds (list): Thresholds for each sensor to detect eye blinks.
        min_points_above_threshold (int): Minimum number of data points that must exceed the threshold 
                                          to detect a blink (default is 50).
        
    Returns:
        detected_blink (int): 
            0 for both eyes blink (if both DAQ 1 and DAQ 2 detect),
            1 for left eye blink (DAQ 1),
            2 for right eye blink (DAQ 2),
            None if no blink is detected.
    """
    sensors_data = [gesture_window_data[f"A{i}"] for i in range(6)]
    
    blink_signals = []
    for i, sensor_data in enumerate(sensors_data):
        # Count the number of data points that exceed the threshold
        count_above_threshold = np.sum(sensor_data > thresholds[i])
        # Check if enough data points exceed the threshold (min_points_above_threshold)
        blink_detected = count_above_threshold >= min_points_above_threshold
        blink_signals.append(blink_detected)
    
    # Check if at least 3 sensors detect a blink
    if np.sum(blink_signals) >= 4:
    # if blink_detected:
        return True  # Blink detected
    else:
        return False  # No blink detected



# def extract_blink_data(filtered_data_dict, start_time, end_time, fs, daq_label):
#     """
#     Extracts the relevant MMG data within the specified time window for blink detection.
    
#     Args:
#         filtered_data_dict (dict): Contains MMG data for each DAQ sensor.
#         start_time (float): Start time of the blink window.
#         end_time (float): End time of the blink window.
#         fs (float): Sampling frequency of the sensor (samples per second).
#         daq_label (str): Label for DAQ ("DAQ_1" or "DAQ_2").
        
#     Returns:
#         gesture_window_data (dict): Contains windowed MMG data for the blink gesture (A0 to A5).
#     """
#     # Calculate the sample indices corresponding to the time window
#     start_index = int(start_time * fs)
#     end_index = int(end_time * fs)

#     # Extract MMG data for A0 to A5 for the given DAQ
#     gesture_window_data = {f"A{i}": filtered_data_dict[f"{daq_label}_A{i}"][start_index:end_index] for i in range(6)}
    
#     return gesture_window_data
def extract_blink_data(filtered_data_dict, start_time, end_time, fs, daq_label):
    """
    Extracts the relevant MMG data within the specified time window for blink detection.
    
    Args:
        filtered_data_dict (dict): Contains MMG data for each DAQ sensor.
        start_time (float): Start time of the blink window.
        end_time (float): End time of the blink window.
        fs (float): Sampling frequency of the sensor (samples per second).
        daq_label (str): Label for DAQ ("DAQ_1" or "DAQ_2").
        
    Returns:
        gesture_window_data (dict): Contains windowed MMG data for the blink gesture (A0 to A5).
    """
    # Calculate the sample indices corresponding to the time window
    start_index = int(start_time * fs)
    end_index = int(end_time * fs)

    # Extract MMG data for A0 to A5 for the given DAQ and make the values absolute
    gesture_window_data = {
        f"A{i}": [abs(value) for value in filtered_data_dict[f"{daq_label}_A{i}"][start_index:end_index]]
        for i in range(6)
    }
    
    return gesture_window_data

def process_eye_blinks(filtered_data_dict, thresholds_daq1, thresholds_daq2, blink_data, fs, min_count=4):
    """
    Processes a list of eye blink gestures and applies the blink detection for each blink window.
    
    Args:
        filtered_data_dict (dict): Contains MMG data for DAQ 1 and DAQ 2 sensors.
        blink_data (pd.DataFrame): DataFrame containing gesture, pressed, released times, and eye blink ground truth.
        fs (float): Sampling frequency of the sensor (samples per second).
        min_count (int): Minimum number of data points that must exceed the threshold to detect a blink.

    Returns:
        results (pd.DataFrame): DataFrame containing gesture, detected blinks, and comparison with ground truth.
    """
    results = []
    
    for i, row in blink_data.iterrows():
        start_time = row['Pressed']
        end_time = row['Released']
        gesture_name = row['Gesture']
        ground_truth = row['Eye_blink']  # 0: both eyes, 1: left eye, 2: right eye
        
        # Extract MMG data for DAQ 1 and DAQ 2
        # if i == 0 or i ==1:
        #     continue
        gesture_window_data_daq1 = extract_blink_data(filtered_data_dict, start_time, end_time, fs, "DAQ_1")
        gesture_window_data_daq2 = extract_blink_data(filtered_data_dict, start_time, end_time, fs, "DAQ_2")
        # # Define thresholds for each sensor in DAQ 1 and DAQ 2
        # thresholds_daq1 = [0.08, 0.125, 0.1, 0.06, 0.1, 0.4]  # Manual thresholds for DAQ 1
        # thresholds_daq2 = [0.03, 0.02, 0.09, 0.05, 0.02, 0.5]  # Manual thresholds for DAQ 2

        # # calculate thresholds for each sensor in DAQ 1 and DAQ 2
        # thresholds_daq1 = [calculate_threshold(gesture_window_data_daq1[f"A{i}"]) for i in range(6)]
        # thresholds_daq2 = [calculate_threshold(gesture_window_data_daq2[f"A{i}"]) for i in range(6)]
        
        # Detect blinks for DAQ 1 and DAQ 2
        daq1_blink_detected = detect_eye_blink(gesture_window_data_daq1, thresholds_daq1, min_points_above_threshold=min_count)
        daq2_blink_detected = detect_eye_blink(gesture_window_data_daq2, thresholds_daq2, min_points_above_threshold=min_count)
        
        # Determine the final detection result
        if daq1_blink_detected and daq2_blink_detected:
            detected_blink = 0  # Both eyes
        elif daq1_blink_detected:
            detected_blink = 1  # Left eye
        elif daq2_blink_detected:
            detected_blink = 2  # Right eye
        else:
            detected_blink = None  # No blink detected
        
        # Compare detected blink with ground truth
        if detected_blink is None:
            result = "No Blink Detected"
        elif detected_blink == ground_truth:
            result = "Match"
        else:
            result = "No Match"
        
        # Store result
        results.append({
            "Gesture": gesture_name,
            "Ground_Truth": ground_truth,
            "Detected_Blink": detected_blink,
            "Result": result
        })
    
    return pd.DataFrame(results)


def calculate_threshold(filtered_data_dict, blink_data, fs, quantile = 0.6):
    """
    Calculates the threshold for eye blink detection using a modified approach.
    Uses mean + (a fraction of the standard deviation) as the threshold.
    
    Args:
        sensor_data (np.ndarray): Sensor data for the 2-8 second window.
        std_multiplier (float): Multiplier for the standard deviation. Default is 0.5.
        
    Returns:
        float: Calculated threshold for the sensor, or 0 if the data is empty.
    """
    thresholds_daq1 = []
    thresholds_daq2 = []

    for i, row in blink_data.iterrows():
        start_time = row['Pressed']
        end_time = row['Released']
        
        # Extract MMG data for DAQ 1 and DAQ 2
        if i == 0:
            gesture_window_data_daq1 = extract_blink_data(filtered_data_dict, start_time, end_time, fs, "DAQ_1")
            for j in range(6):
                sensor_data = gesture_window_data_daq1[f"A{j}"]
                if len(sensor_data) == 0 or np.all(np.isnan(sensor_data)):
                    thresholds_daq1.append(0)
     
                thresh = np.quantile(sensor_data, quantile)
                thresholds_daq1.append(thresh)
        if i == 1:
            gesture_window_data_daq2 = extract_blink_data(filtered_data_dict, start_time, end_time, fs, "DAQ_2")
            for j in range(6):
                sensor_data = gesture_window_data_daq2[f"A{j}"]
                if len(sensor_data) == 0 or np.all(np.isnan(sensor_data)):
                    thresholds_daq2.append(0)

                thresh = np.quantile(sensor_data, quantile)
                thresholds_daq2.append(thresh)
        if i>=2:
            break
        
    # # Define thresholds for each sensor in DAQ 1 and DAQ 2
    # thresholds_daq1 = [0.08, 0.125, 0.1, 0.06, 0.1, 0.4]  # Manual thresholds for DAQ 1
    # thresholds_daq2 = [0.03, 0.02, 0.09, 0.05, 0.02, 0.5]  # Manual thresholds for DAQ 2

    # Return threshold as mean + (fraction of standard deviation)
    return thresholds_daq1, thresholds_daq2


def plot_mmg_data(filtered_data_dict, blink_data, fs, results, output_file_daq1='mmg_data_daq1_with_blinks.png', output_file_daq2='mmg_data_daq2_with_blinks.png'):
    """
    Plots MMG sensor data from DAQ 1 and DAQ 2 in two separate plots with threshold lines 
    and highlights the ground truth and matched areas for blinks.
    
    Args:
        filtered_data_dict (dict): Contains MMG data for each DAQ sensor.
        blink_data (pd.DataFrame): DataFrame containing gesture, pressed, released times, and eye blink ground truth.
        fs (float): Sampling frequency of the sensor (samples per second).
        results (pd.DataFrame): DataFrame containing the detection results (match/no match).
        output_file_daq1 (str): File name to save the plot for DAQ 1 (default: 'mmg_data_daq1_with_blinks.png').
        output_file_daq2 (str): File name to save the plot for DAQ 2 (default: 'mmg_data_daq2_with_blinks.png').
    """

    # Plot DAQ 1
    sensors_daq1 = [f"DAQ_1_A{i}" for i in range(6)]
    time = np.arange(len(filtered_data_dict[sensors_daq1[0]])) / fs

    plt.figure(figsize=(12, 10))
    for i, sensor in enumerate(sensors_daq1):
        plt.subplot(6, 1, i + 1)
        plt.plot(time, filtered_data_dict[sensor], label=f'Sensor {sensor}')

        # Plot Ground Truth and Matched Area for Each Gesture
        for j, row in blink_data.iterrows():
            start_time = row['Pressed']
            end_time = row['Released']

            # Highlight the ground truth area
            plt.axvspan(start_time, end_time, color='yellow', alpha=0.3, label='Ground Truth' if j == 0 else "")

            # Highlight the matched area (if result is "Match")
            if results.iloc[j]['Result'] == 'Match':
                plt.axvspan(start_time, end_time, color='green', alpha=0.5, label='Matched' if j == 0 else "")

        plt.title(f'{sensor} Data')
        plt.xlabel('Time (s)')
        plt.ylabel('MMG Signal')
        plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_file_daq1)
    plt.close()

    # Plot DAQ 2
    sensors_daq2 = [f"DAQ_2_A{i}" for i in range(6)]
    time = np.arange(len(filtered_data_dict[sensors_daq2[0]])) / fs

    plt.figure(figsize=(12, 10))
    for i, sensor in enumerate(sensors_daq2):
        plt.subplot(6, 1, i + 1)
        plt.plot(time, filtered_data_dict[sensor], label=f'Sensor {sensor}')

        # Plot Ground Truth and Matched Area for Each Gesture
        for j, row in blink_data.iterrows():
            start_time = row['Pressed']
            end_time = row['Released']

            # Highlight the ground truth area
            plt.axvspan(start_time, end_time, color='yellow', alpha=0.3, label='Ground Truth' if j == 0 else "")

            # Highlight the matched area (if result is "Match")
            if results.iloc[j]['Result'] == 'Match':
                plt.axvspan(start_time, end_time, color='green', alpha=0.5, label='Matched' if j == 0 else "")

        plt.title(f'{sensor} Data')
        plt.xlabel('Time (s)')
        plt.ylabel('MMG Signal')
        plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_file_daq2)
    plt.close()