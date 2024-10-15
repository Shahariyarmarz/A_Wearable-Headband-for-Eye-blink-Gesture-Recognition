import logging
import os
from daq_processing import process_multiple_daqs
from visualization import visualize_sensor_data
from config import get_daq_file_paths, get_fs_MMG_sensor, get_fs_IMU_sensor
from band_pass_filter import band_pass
from kalman_filter import imu_to_roll_pitch_yaw_ekf
import pandas as pd
from datetime import timedelta, datetime, time

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
            
            # Filtered MMG data is expected to be a list with 8 arrays corresponding to A0 to A7
            sensor_names = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"]
            
            # Store each filtered sensor's data into filtered_data_dict
            for j, sensor_name in enumerate(sensor_names):
                key = f"{daq_label}_{sensor_name}"
                filtered_data_dict[key] = filtered_mmg_data[j]

        # kalman filter 
        IMU_RPY_data = imu_to_roll_pitch_yaw_ekf(sensor_data_list[0], fs_imu, "DAQ_1")
        filtered_data_dict["DAQ_1_r"] = IMU_RPY_data[:, 0]
        filtered_data_dict["DAQ_1_p"] = IMU_RPY_data[:, 1]
        filtered_data_dict["DAQ_1_y"] = IMU_RPY_data[:, 2]

        # file_path = './Data_files/Sequential_Play_9.xlsx'
        # df = pd.read_excel(file_path)

        # # Inspect the raw data types of 'Pressed' and 'Released' columns
        # print("Data types before processing:")
        # print(df.dtypes)
        # print("Raw 'Pressed' and 'Released' values:")
        # print(df[['Pressed', 'Released']].head())

        # # Function to convert datetime.time and string formats to timedelta
        # def time_to_timedelta(time_val):
        #     if isinstance(time_val, str):
        #         # Try parsing time as a string (e.g., "00:00:06")
        #         return pd.to_timedelta(time_val, errors='coerce')
        #     elif isinstance(time_val, time):
        #         # Convert datetime.time to timedelta since midnight
        #         return timedelta(hours=time_val.hour, minutes=time_val.minute, seconds=time_val.second)
        #     else:
        #         return pd.NaT  # Return NaT if it doesn't match either

        # # Apply the conversion function to the "Pressed" and "Released" columns
        # df['Pressed'] = df['Pressed'].apply(time_to_timedelta)
        # df['Released'] = df['Released'].apply(time_to_timedelta)

        # # Check for any NaT values (to detect conversion issues)
        # print("Rows with NaT (non-converted values):")
        # print(df[df.isna().any(axis=1)])  # Display rows that have NaT values

        # # Add 14 seconds to both "Pressed" and "Released" times (only if they are valid)
        # df['Pressed'] = df['Pressed'].apply(lambda x: x + timedelta(seconds=14) if pd.notna(x) else x)
        # df['Released'] = df['Released'].apply(lambda x: x + timedelta(seconds=14) if pd.notna(x) else x)

        # # Convert Pressed and Released columns to total seconds
        # df['Pressed'] = df['Pressed'].apply(lambda x: x.total_seconds() if pd.notna(x) else x)
        # df['Released'] = df['Released'].apply(lambda x: x.total_seconds() if pd.notna(x) else x)

        # # Display the updated dataframe to check the results
        # print(df)

        # Optionally, save the updated dataframe to a new Excel file
        # df.to_excel('updated_gesture_data_in_seconds.xlsx', index=False)
                
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
