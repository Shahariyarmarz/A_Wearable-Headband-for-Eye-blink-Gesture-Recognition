import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def detect_head_movement(gesture_window_data):
    """
    Detects front, left, and right head movements within a given time window based on IMU data.
    
    Args:
        gesture_window_data (dict): Contains the windowed IMU data (pitch, yaw, roll) for the gesture.

    Returns:
        detected_movement (int): 
            0 for front, 
            1 for left, 
            2 for right head movements, 
            None if no movement detected.
    """
    roll_data = gesture_window_data["roll"]
    pitch_data = gesture_window_data["pitch"]
    yaw_data = gesture_window_data["yaw"]

    # Initialize crossing variables
    pitch_cross_low = []
    pitch_cross_high = []
    yaw_cross_low = []
    yaw_cross_high = []

    # 1. Detect Front Head Movement
    if np.all(roll_data < 0.1) and np.all(pitch_data < 0.2) and np.all(yaw_data < 0.1):
        return 0  # Front

    # 2. Detect Left Head Movement
    elif np.any(roll_data >= 0):  # Roll condition
        # Check the pitch condition
        pitch_cross_low = np.where(pitch_data <= -0.2)[0]  # Indices where pitch is <= -0.2
        yaw_cross_high = np.where(yaw_data >= 0.08)[0]      # Indices where yaw is >= 0.08

        if len(pitch_cross_low) > 0:
            # Check if pitch goes back up after going low
            pitch_cross_high = np.where(pitch_data[pitch_cross_low[0]:] >= 0.2)[0]
            if len(pitch_cross_high) > 0:
                return 1  # Left, Roll + Pitch conditions met

        if len(yaw_cross_high) > 0:
            # Check if yaw goes back down after going high
            yaw_cross_low = np.where(yaw_data[yaw_cross_high[0]:] <= -0.08)[0]
            if len(yaw_cross_low) > 0:
                return 1  # Left, Roll + Yaw conditions met

    # Check if two out of (pitch and yaw) are met, without requiring roll
    if len(pitch_cross_low) > 0 and len(yaw_cross_high) > 0:
        return 1  # Left, Pitch + Yaw conditions met

    # 3. Detect Right Head Movement
    elif np.any(roll_data <= -0.1):  # Roll condition
        # Check the pitch condition
        pitch_cross_high = np.where(pitch_data >= 0.2)[0]  # Indices where pitch is >= 0.2
        yaw_cross_low = np.where(yaw_data <= -0.08)[0]     # Indices where yaw is <= -0.08

        if len(pitch_cross_high) > 0:
            # Check if pitch goes back down after going high
            pitch_cross_low = np.where(pitch_data[pitch_cross_high[0]:] <= -0.2)[0]
            if len(pitch_cross_low) > 0:
                return 2  # Right, Roll + Pitch conditions met

        if len(yaw_cross_low) > 0:
            # Check if yaw goes back up after going low
            yaw_cross_high = np.where(yaw_data[yaw_cross_low[0]:] >= 0.08)[0]
            if len(yaw_cross_high) > 0:
                return 2  # Right, Roll + Yaw conditions met

    # Check if two out of (pitch and yaw) are met, without requiring roll
    if len(pitch_cross_high) > 0 and len(yaw_cross_low) > 0:
        return 2  # Right, Pitch + Yaw conditions met

    # No movement detected
    return None



def extract_gesture_data(filtered_data_dict, start_time, end_time, fs):
    """
    Extracts the relevant IMU data within the specified time window for gesture detection.
    
    Args:
        filtered_data_dict (dict): Contains roll, pitch, yaw arrays.
        start_time (float): Start time of the gesture window.
        end_time (float): End time of the gesture window.
        fs (float): Sampling frequency of the sensor (samples per second).

    Returns:
        gesture_window_data (dict): Contains windowed IMU data for the gesture.
    """
    # Calculate the sample indices corresponding to the time window
    start_index = int(start_time * fs)
    end_index = int(end_time * fs)
    
    gesture_window_data = {
        "roll": filtered_data_dict["DAQ_1_r"][start_index:end_index],
        "pitch": filtered_data_dict["DAQ_1_p"][start_index:end_index],
        "yaw": filtered_data_dict["DAQ_1_y"][start_index:end_index],
    }
    
    return gesture_window_data

def process_gestures(filtered_data_dict, gesture_data, pitch_threshold, yaw_threshold_right, yaw_threshold_left, fs, min_count=32):
    """
    Processes a list of gestures and applies the movement detection for each gesture window.
    
    Args:
        filtered_data_dict (dict): Contains roll, pitch, yaw arrays.
        gesture_data (pd.DataFrame): DataFrame containing gesture, pressed, released times, and head movement (0: front, 1: left, 2: right).
        pitch_threshold (float): Threshold for detecting front head movement.
        yaw_threshold_right (float): Threshold for detecting right head movement.
        yaw_threshold_left (float): Threshold for detecting left head movement.
        fs (float): Sampling frequency of the sensor (samples per second).
        min_count (int): Minimum number of samples that must exceed the threshold to detect a gesture.

    Returns:
        results (pd.DataFrame): DataFrame containing gesture, detected movements, and comparison with ground truth.
    """
    results = []
    
    for i, row in gesture_data.iterrows():
        start_time = row['Pressed']
        end_time = row['Released']
        gesture_name = row['Gesture']
        ground_truth = row['Head_movement']  # 0: front, 1: left, 2: right
        
        # Extract gesture window data based on the time window from the Excel file
        gesture_window_data = extract_gesture_data(filtered_data_dict, start_time, end_time, fs)
        
        # Detect movements with the updated condition
        detected_movement = detect_head_movement(gesture_window_data)
        
        # Compare detected movement with ground truth
        if detected_movement is None:
            result = "No Movement Detected"
        elif detected_movement == ground_truth:
            result = "Match"
        else:
            result = "No Match"
        
        # Store result
        results.append({
            "Gesture": gesture_name,
            "Ground_Truth": ground_truth,
            "Detected_Movement": detected_movement,
            "Result": result
        })
    
    return pd.DataFrame(results)

def plot_imu_data(filtered_data_dict, gesture_data, pitch_threshold, yaw_threshold_right, yaw_threshold_left, results, fs, output_file='imu_data_plot.png'):
    """
    Plots roll, pitch, and yaw data with threshold lines and highlights the ground truth
    and matched areas for gestures.
    
    Args:
        filtered_data_dict (dict): Contains roll, pitch, yaw arrays.
        gesture_data (pd.DataFrame): DataFrame containing gesture, pressed, released times, and head movement.
        pitch_threshold (float): Threshold for detecting front head movement.
        yaw_threshold_right (float): Threshold for detecting right head movement.
        yaw_threshold_left (float): Threshold for detecting left head movement.
        results (pd.DataFrame): DataFrame containing the detection results (match/no match).
        fs (float): Sampling frequency of the sensor (samples per second).
        output_file (str): File name to save the plot (default: 'imu_data_plot.png').
    """
    
    roll = filtered_data_dict["DAQ_1_r"]
    pitch = filtered_data_dict["DAQ_1_p"]
    yaw = filtered_data_dict["DAQ_1_y"]

    # Create time array based on the sampling frequency (fs)
    time = np.arange(len(roll)) / fs
    
    plt.figure(figsize=(12, 8))
    
    # Plot Roll Data
    plt.subplot(311)
    plt.plot(time, roll, 'r-', label='Roll')
    plt.title('Roll over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Roll (rad)')
    
    # Plot Ground Truth and Detected Matched Area for Roll
    for i, row in gesture_data.iterrows():
        start_time = row['Pressed']
        end_time = row['Released']
        ground_truth = row['Head_movement']
        
        # Highlight the ground truth area
        plt.axvspan(start_time, end_time, color='yellow', alpha=0.3, label='Ground Truth' if i == 0 else "")
        
        # Highlight the matched area (if result is "Match")
        if results.iloc[i]['Result'] == 'Match':
            plt.axvspan(start_time, end_time, color='green', alpha=0.5, label='Matched' if i == 0 else "")
    
    plt.legend()

    # Plot Pitch Data
    plt.subplot(312)
    plt.plot(time, pitch, 'g-', label='Pitch')
    plt.axhline(pitch_threshold, color='gray', linestyle='--', label='Pitch Threshold')
    plt.title('Pitch over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Pitch (rad)')
    
    # Plot Ground Truth and Detected Matched Area for Pitch
    for i, row in gesture_data.iterrows():
        start_time = row['Pressed']
        end_time = row['Released']
        
        # Highlight the ground truth area
        plt.axvspan(start_time, end_time, color='yellow', alpha=0.3, label='Ground Truth' if i == 0 else "")
        
        # Highlight the matched area (if result is "Match")
        if results.iloc[i]['Result'] == 'Match':
            plt.axvspan(start_time, end_time, color='green', alpha=0.5, label='Matched' if i == 0 else "")
    
    plt.legend()

    # Plot Yaw Data
    plt.subplot(313)
    plt.plot(time, yaw, 'b-', label='Yaw')
    plt.axhline(yaw_threshold_right, color='gray', linestyle='--', label='Yaw Right Threshold')
    plt.axhline(yaw_threshold_left, color='gray', linestyle='--', label='Yaw Left Threshold')
    plt.title('Yaw over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Yaw (rad)')
    
    # Plot Ground Truth and Detected Matched Area for Yaw
    for i, row in gesture_data.iterrows():
        start_time = row['Pressed']
        end_time = row['Released']
        
        # Highlight the ground truth area
        plt.axvspan(start_time, end_time, color='yellow', alpha=0.3, label='Ground Truth' if i == 0 else "")
        
        # Highlight the matched area (if result is "Match")
        if results.iloc[i]['Result'] == 'Match':
            plt.axvspan(start_time, end_time, color='green', alpha=0.5, label='Matched' if i == 0 else "")
    
    plt.legend()

    # Adjust layout and save plot to file
    plt.tight_layout()
    plt.savefig('imu_data_with_gestures.png')
    plt.close()

# Load gesture data from Excel
def load_gesture_data_from_excel(file_path):
    """
    Loads gesture data from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file.
    
    Returns:
        gesture_data (pd.DataFrame): DataFrame with gesture names, pressed times, and released times.
    """
    gesture_data = pd.read_excel(file_path)
    return gesture_data