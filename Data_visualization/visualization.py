import matplotlib.pyplot as plt
import os
import logging
import numpy as np

def visualize_sensor_data(sensor_data, database_name, fs_mmg=256, fs_imu=64):
    """
    Visualizes sensor data from the provided dictionary.
    Separates MMG and IMU sensor data visualization and saves the plots.
    
    MMG sensors are assumed to have a sampling frequency of 256 Hz (fs_mmg).
    IMU sensors are assumed to have a sampling frequency of 64 Hz (fs_imu).
    """
    try:
        logging.info(f"Visualizing sensor data for {database_name}")
        
        # Create the visual directory if it doesn't exist
        os.makedirs('visual', exist_ok=True)

        # MMG Sensors: first 8 sensors
        mmg_sensor_names = list(sensor_data.keys())[:8]
        fig, axs = plt.subplots(len(mmg_sensor_names), 1, figsize=(15, 15))
        for i, sensor_name in enumerate(mmg_sensor_names):
            sensor_length = len(sensor_data[sensor_name])
            time_vector = np.arange(sensor_length) / fs_mmg  # Use MMG sampling frequency (256 Hz)
            axs[i].plot(time_vector, sensor_data[sensor_name], label=sensor_name)
            axs[i].set_title(f'{sensor_name} MMG Sensor Data')
            axs[i].set_xlabel('Time (s)')
            axs[i].set_ylabel('Sensor Output (a.u.)')
            axs[i].legend()
            axs[i].grid(True)

        plt.tight_layout()
        plt.savefig(f'./visual/{database_name}_MMG_sensors.png', dpi=300)
        plt.clf()  # Clear the figure for the next plot

        logging.info(f"MMG sensor data visualization saved for {database_name}")

        # IMU Sensors: last 9 sensors (check if IMU data exists)
        imu_sensor_names = list(sensor_data.keys())[8:]
        imu_data_present = all(len(sensor_data[name]) > 0 for name in imu_sensor_names)

        if imu_data_present:
            fig, axs = plt.subplots(len(imu_sensor_names), 1, figsize=(15, 18))
            for i, sensor_name in enumerate(imu_sensor_names):
                sensor_length = len(sensor_data[sensor_name])
                time_vector = np.arange(sensor_length) / fs_imu  # Use IMU sampling frequency (64 Hz)
                axs[i].plot(time_vector, sensor_data[sensor_name], label=sensor_name)
                axs[i].set_title(f'{sensor_name} IMU Sensor Data')
                axs[i].set_xlabel('Time (s)')
                axs[i].set_ylabel('Sensor Output (a.u.)')
                axs[i].legend()
                axs[i].grid(True)

            plt.tight_layout()
            plt.savefig(f'./visual/{database_name}_IMU_sensors.png', dpi=300)
            plt.clf()

            logging.info(f"IMU sensor data visualization saved for {database_name}")
        else:
            logging.info(f"No IMU data present for {database_name}, skipping IMU plot.")

    except Exception as e:
        logging.error(f"Error visualizing sensor data for {database_name}: {e}")
