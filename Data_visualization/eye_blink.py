import numpy as np
import pandas as pd

def eye_blink_detection(filtered_data_dict, excel_file_path, fs_mmg=256):
    """
    Detects eye blinks in MMG sensor data (DAQ_1_A0 to DAQ_1_A5 and DAQ_2_A0 to DAQ_2_A5),
    and compares the detection with the ground truth in the Excel file.
    
    Args:
        filtered_data_dict (dict): Dictionary containing all sensor data.
        excel_file_path (str): Path to the Excel file that contains the time windows and ground truth for detection.
        fs_mmg (int): Sampling frequency for MMG sensors (default is 256Hz).
        
    Returns:
        result_df (pd.DataFrame): DataFrame containing the detection results and whether they match the ground truth.
    """
    
    # Load the Excel file
    df = pd.read_excel(excel_file_path)
    
    detection_results = []
    
    # Loop through each time window in the Excel file (assumes "Pressed", "Released", and "Eye_blink" columns exist)
    for i, row in df.iterrows():
        start_time = row['Pressed']
        end_time = row['Released']
        ground_truth = row['Eye_blink']
        
        # Convert times to sample indices
        start_sample = int(start_time * fs_mmg)
        end_sample = int(end_time * fs_mmg)
        
        # Extract DAQ1 and DAQ2 sensor data (A0 to A5)
        daq1_sensors = [filtered_data_dict[f'DAQ_1_A{i}'][start_sample:end_sample] for i in range(6)]
        daq2_sensors = [filtered_data_dict[f'DAQ_2_A{i}'][start_sample:end_sample] for i in range(6)]
        
        # Detect eye blinks in DAQ_1 and DAQ_2
        daq1_blink_detected = detect_eye_blink_in_daq(daq1_sensors, fs_mmg, 1)
        daq2_blink_detected = detect_eye_blink_in_daq(daq2_sensors, fs_mmg, 2)
        
        # Determine the final detection result
        if daq1_blink_detected and daq2_blink_detected:
            detected_eye_blink = 0  # Both eyes
        elif daq1_blink_detected:
            detected_eye_blink = 1  # Left eye
        elif daq2_blink_detected:
            detected_eye_blink = 2  # Right eye
        else:
            detected_eye_blink = None  # No blink detected
        
        # Check if the detected result matches the ground truth
        match = detected_eye_blink == ground_truth
        
        # Append the result for this window
        detection_results.append({
            "Start Time": start_time,
            "End Time": end_time,
            "Ground Truth": ground_truth,
            "Detected Eye Blink": detected_eye_blink,
            "Match": match
        })
    
    # Create a DataFrame from the results
    result_df = pd.DataFrame(detection_results)
    
    return result_df


def detect_eye_blink_in_daq(sensors_data, fs_mmg, daq_number):
    """
    Detects if there is an eye blink signal in the DAQ sensor data for A0 to A5.
    Uses data from a window (e.g., 2 to 8 seconds) to calculate the threshold.
    
    Args:
        sensors_data (list): List of sensor data arrays (A0 to A5) for one DAQ.
        fs_mmg (int): Sampling frequency of the MMG sensors.
        
    Returns:
        bool: True if an eye blink is detected (at least 3 sensors show an eye blink), False otherwise.
    """
    daq_number = int(daq_number)
    # Extract 2 to 8 seconds window (for threshold calculation)
    start_sample = int(2 * fs_mmg)
    end_sample = int(8 * fs_mmg)
    window_size = 2  # Window size in seconds
    fs_mmg = 256     # Sampling frequency of MMG sensors (in Hz)

    # Calculate sample indices for the 2-8 second window
    start_sample = int(2 * fs_mmg)
    end_sample = int(8 * fs_mmg)

    # Calculate adaptive threshold for each sensor within the 2-8 second window
    # thresholds = [adaptive_threshold(sensor[start_sample:end_sample], window_size, fs_mmg) 
    #             for sensor in sensors_data]
    thresholds = [calculate_threshold(sensor[start_sample:end_sample]) for sensor in sensors_data]
    if daq_number == '1':
        print("DAQ 1 thresholds: ", thresholds)
    else:
        print("DAQ 2 thresholds: ", thresholds)
    
    # Detect eye blink using the calculated thresholds
    blink_signals = []
    for i, sensor_data in enumerate(sensors_data):
        blink_detected = np.any(sensor_data > thresholds[i])
        blink_signals.append(blink_detected)
    
    # Check if at least 3 sensors detect an eye blink
    if np.sum(blink_signals) >= 2:
        return True  # Eye blink detected
    else:
        return False  # No eye blink detected


def calculate_threshold(sensor_data, std_multiplier=0.5):
    """
    Calculates the threshold for eye blink detection using a modified approach.
    Uses mean + (a fraction of the standard deviation) as the threshold.
    
    Args:
        sensor_data (np.ndarray): Sensor data for the 2-8 second window.
        std_multiplier (float): Multiplier for the standard deviation. Default is 0.5.
        
    Returns:
        float: Calculated threshold for the sensor.
    """
    mean_value = np.mean(sensor_data)
    std_value = np.std(sensor_data)
    value = (mean_value + std_multiplier * std_value)*0.5
    # Return threshold as mean + (fraction of standard deviation)
    return value

def adaptive_threshold(sensor_data, window_size, fs_mmg):
    """
    Apply adaptive thresholding using a sliding window approach.
    
    Args:
        sensor_data (np.ndarray): Sensor data for one sensor.
        window_size (int): Size of the sliding window (in seconds).
        fs_mmg (int): Sampling frequency of the MMG sensors.
        
    Returns:
        threshold (float): Adaptive threshold based on the sliding window.
    """
    window_samples = window_size * fs_mmg  # Convert window size to samples
    num_windows = len(sensor_data) // window_samples
    
    thresholds = []
    for i in range(num_windows):
        start_idx = i * window_samples
        end_idx = (i + 1) * window_samples
        window_data = sensor_data[start_idx:end_idx]
        
        # Calculate the adaptive threshold for the current window
        mean_value = np.mean(window_data)
        std_value = np.std(window_data)
        threshold = mean_value + std_value
        thresholds.append(threshold)
    
    # Return the overall threshold (or modify to be dynamic over time)
    return np.mean(thresholds)