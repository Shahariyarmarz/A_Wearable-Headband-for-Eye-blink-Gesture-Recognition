import numpy as np
from scipy.signal import butter, sosfiltfilt
import logging
import matplotlib.pyplot as plt
import os

def band_pass(database_name, sensor_data, low_cutoff, high_cutoff, fs_mmg, fs_imu, filter_order=10):
    """
    Apply a bandpass filter to MMG and IMU sensor data arrays separately and visualize the results.
    
    Args:
        database_name (str): Name of the database for saving visualizations.
        sensor_data (dict): Dictionary containing all sensor data, where the first 3 entries are the XYZ axes of 
                            the same accelerometer, and the next 5 are individual MMG sensors.
        low_cutoff (float): Low cutoff frequency for the bandpass filter.
        high_cutoff (float): High cutoff frequency for the bandpass filter.
        fs_mmg (int): Sampling frequency for MMG sensor data.
        fs_imu (int): Sampling frequency for IMU sensor data.
        filter_order (int): Order of the filter (default is 10).
        
    Returns:
        filtered_mmg_data (list): List of filtered MMG sensor data arrays.
        filtered_imu_data (list): List of filtered IMU sensor data arrays (if IMU data exists).
    """
    try:
        logging.info(f"Applying bandpass filter to MMG and IMU sensors for {database_name}")

        # ===================== Compute RMS of A5 to A7 (accelerometer XYZ) =====================
        aclm_x = sensor_data["A5"]
        aclm_y = sensor_data["A6"]
        aclm_z = sensor_data["A7"]
        
        # Compute RMS for A5, A6, A7 (treated as the same accelerometer)
        A5_rms = np.sqrt((aclm_x**2 + aclm_y**2 + aclm_z**2) / 3)

        # Use this new RMS signal as the new A0 sensor
        mmg_sensor_data_list = [A5_rms]  # Start the list with the RMS of A5 to A7

        # Add the remaining MMG sensors (A3 to A7)
        mmg_sensor_data_list.extend([sensor_data[f"A{i}"] for i in range(5)])  # A0 to A4

        # ===================== IMU Sensor Data =====================
        imu_sensor_data_list = [sensor_data.get(key) for key in ["Aclm_X", "Aclm_Y", "Aclm_Z", "Gyro_X", "Gyro_Y", "Gyro_Z", "Mag_X", "Mag_Y", "Mag_Z"]]
        imu_sensor_data_list = [data for data in imu_sensor_data_list if data is not None and len(data) > 0]  # Filter out any missing or empty IMU data

        # ===================== Filter for MMG sensors =====================
        sos_mmg = butter(filter_order // 2, [low_cutoff, high_cutoff], btype='bandpass', fs=fs_mmg, output='sos')
        filtered_mmg_data = [sosfiltfilt(sos_mmg, sensor_data) for sensor_data in mmg_sensor_data_list]
        logging.info(f"Bandpass filtering for MMG sensors completed for {database_name}")

        # ===================== Filter for IMU sensors (if available) =====================
        filtered_imu_data = []
        if imu_sensor_data_list:  # Check if IMU data exists
            sos_imu = butter(filter_order // 2, [low_cutoff, high_cutoff], btype='bandpass', fs=fs_imu, output='sos')
            filtered_imu_data = [sosfiltfilt(sos_imu, sensor_data) for sensor_data in imu_sensor_data_list]
            logging.info(f"Bandpass filtering for IMU sensors completed for {database_name}")
        else:
            logging.info(f"No IMU data found for {database_name}, skipping IMU filtering.")

        # ===================== Visualization of Filtered Data =====================
        os.makedirs('visual', exist_ok=True)

        # Visualize MMG sensors (recalculate time vector based on filtered data length)
        for i, filtered_data in enumerate(filtered_mmg_data):
            time_vector_mmg = np.arange(len(filtered_data)) / fs_mmg  # Ensure the time vector matches filtered data length
            plt.figure(figsize=(10, 4))
            plt.plot(time_vector_mmg, filtered_data, label=f'MMG Sensor A{i}')
            plt.title(f'Filtered MMG Sensor A{i} Data')
            plt.xlabel('Time (s)')
            plt.ylabel('Sensor Output (a.u.)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f'./visual/{database_name}_MMG_A{i}_filtered.png', dpi=300)
            plt.clf()

        logging.info(f"MMG sensor data visualization saved for {database_name}")

        # # Visualize IMU sensors (if available)
        # if filtered_imu_data:
        #     for i, filtered_data in enumerate(filtered_imu_data):
        #         time_vector_imu = np.arange(len(filtered_data)) / fs_imu  # Ensure the time vector matches filtered data length
        #         plt.figure(figsize=(10, 4))
        #         plt.plot(time_vector_imu, filtered_data, label=f'IMU Sensor {i+1}')
        #         plt.title(f'Filtered IMU Sensor {i+1} Data')
        #         plt.xlabel('Time (s)')
        #         plt.ylabel('Sensor Output (a.u.)')
        #         plt.legend()
        #         plt.grid(True)
        #         plt.tight_layout()
        #         plt.savefig(f'./visual/{database_name}_IMU_Sensor_{i+1}_filtered.png', dpi=300)
        #         plt.clf()

        #     logging.info(f"IMU sensor data visualization saved for {database_name}")
        # else:
        #     logging.info(f"No IMU data available for visualization in {database_name}")

        return filtered_mmg_data, filtered_imu_data

    except Exception as e:
        logging.error(f"Error during bandpass filtering or visualization for {database_name}: {e}")
        raise
