import logging
import os
from daq_processing import process_multiple_daqs
from visualization import visualize_sensor_data
from config import get_daq_file_paths, get_fs_MMG_sensor, get_fs_IMU_sensor, get_excel_file_path
from band_pass_filter import band_pass
from kalman_filter import imu_to_roll_pitch_yaw_ekf
import pandas as pd
from datetime import timedelta, datetime, time
from head_movement import load_gesture_data_from_excel, process_gestures, plot_imu_data
from eye_blink_v2 import process_eye_blinks, plot_mmg_data

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to orchestrate DAQ processing and visualization.
    """
    try:
        # Get DAQ file paths from config
        daq_file_paths = get_daq_file_paths()

        if not daq_file_paths:
            logging.error("No DAQ file paths provided. Exiting.")
            return

        # Sampling frequency
        fs_mmg = get_fs_MMG_sensor()
        fs_imu = get_fs_IMU_sensor()


        # Process DAQs
        sensor_data_list = process_multiple_daqs(daq_file_paths, fs_mmg)

        # Visualize the sensor data
        # for i, sensor_data in enumerate(sensor_data_list):
        #     if sensor_data:
        #         visualize_sensor_data(sensor_data, f"DAQ_{i+1}", fs_mmg, fs_imu)

        # Filter parameters
        low_cutoff = 1.0
        high_cutoff = 30.0
    
        # Apply bandpass filter
        # Dictionary to hold the filtered MMG data for each sensor in each DAQ
        filtered_data_dict = {}

        # Apply bandpass filter for each DAQ's MMG data
        for i, sensor_data in enumerate(sensor_data_list):
            daq_label = f"DAQ_{i+1}"
            
            # Pass the entire MMG data (A0 to A7) to the band_pass function
            filtered_mmg_data, _ = band_pass(daq_label, sensor_data, low_cutoff, high_cutoff, fs_mmg, fs_imu)
            
            # Filtered MMG data is expected to be a list with 8 arrays corresponding to A0 to A5
            sensor_names = ["A0", "A1", "A2", "A3", "A4", "A5"]
            # A0 = accelerometer RMS, A1 to A5 = piezo sensors
            
            # Store each filtered sensor's data into filtered_data_dict
            for j, sensor_name in enumerate(sensor_names):
                key = f"{daq_label}_{sensor_name}"
                filtered_data_dict[key] = filtered_mmg_data[j]

        # kalman filter 
        IMU_RPY_data = imu_to_roll_pitch_yaw_ekf(sensor_data_list[0], fs_imu, "DAQ_1")
        filtered_data_dict["DAQ_1_r"] = IMU_RPY_data[:, 0]
        filtered_data_dict["DAQ_1_p"] = IMU_RPY_data[:, 1]
        filtered_data_dict["DAQ_1_y"] = IMU_RPY_data[:, 2]

        # Define thresholds for detecting gestures based on IMU data
        PITCH_THRESHOLD = 0.4  # Front head movement
        YAW_THRESHOLD_RIGHT = 0.15  # Right head movement
        YAW_THRESHOLD_LEFT = -0.15  # Left head movement

        # Example usage:

        # Load gesture data from Excel
        # excel_file_path = "./modified_gesture_data_in_seconds.xlsx"
        excel_file_path = get_excel_file_path()
        gesture_data = load_gesture_data_from_excel(excel_file_path)
        MIN_COUNT = 5  # Minimum number of values above threshold to detect a gesture
        # Process the gestures
        results = process_gestures(
            filtered_data_dict, 
            gesture_data, 
            PITCH_THRESHOLD, 
            YAW_THRESHOLD_RIGHT, 
            YAW_THRESHOLD_LEFT,
            fs_imu,
            MIN_COUNT  # Minimum number of samples above threshold for detection
        )

        # Print the results
        print(results)

        # Call the plotting function
        plot_imu_data(
            filtered_data_dict, 
            gesture_data, 
            PITCH_THRESHOLD, 
            YAW_THRESHOLD_RIGHT, 
            YAW_THRESHOLD_LEFT, 
            results, 
            fs_imu,  # Example sampling rate
            output_file='imu_data_with_gestures.png'  # Custom output file name
        )

        # Eye Blink Detection

        blink_data = load_gesture_data_from_excel(excel_file_path)  # Load blink gesture data from Excel

        # Process eye blink detection
        eye_blink_results = process_eye_blinks(filtered_data_dict, blink_data, fs_mmg, min_count=50)

        print("Eye Blink Detection Results:")
        print(eye_blink_results)

        # Optionally, save the results to an Excel file
        eye_blink_results.to_excel('eye_blink_detection_results.xlsx', index=False)

        # Plot MMG data with blink detection visualization for DAQ 1 and DAQ 2
        plot_mmg_data(filtered_data_dict, blink_data, fs_mmg, eye_blink_results, 
                            output_file_daq1='mmg_data_daq1_with_blinks.png', 
                            output_file_daq2='mmg_data_daq2_with_blinks.png')
                
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
