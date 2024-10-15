import numpy as np
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
import os
import logging

def initialize_ekf(fs_imu):
    """
    Initializes an Extended Kalman Filter for sensor fusion (9-axis IMU).
    
    Args:
        fs_imu (int): Sampling frequency of the IMU.
        
    Returns:
        KalmanFilter: Initialized Kalman filter object.
    """
    dt = 1.0 / fs_imu  # Time step based on sampling rate

    # Kalman Filter Initialization
    ekf = KalmanFilter(dim_x=6, dim_z=9)
    
    # State vector [roll, pitch, yaw, roll_rate, pitch_rate, yaw_rate]
    ekf.x = np.zeros(6)

    # State transition matrix (linearized system dynamics)
    ekf.F = np.eye(6)
    ekf.F[0, 3] = dt  # Roll depends on roll_rate
    ekf.F[1, 4] = dt  # Pitch depends on pitch_rate
    ekf.F[2, 5] = dt  # Yaw depends on yaw_rate

    # Process noise covariance
    ekf.Q = np.eye(6) * 0.1  # Tune this for better results

    # Measurement function (maps state to measurements)
    ekf.H = np.zeros((9, 6))
    ekf.H[0:3, 0:3] = np.eye(3)  # Accelerometer provides roll, pitch, yaw
    ekf.H[3:6, 3:6] = np.eye(3)  # Gyroscope provides roll_rate, pitch_rate, yaw_rate
    ekf.H[6:9, 0:3] = np.eye(3)  # Magnetometer also contributes to roll, pitch, yaw

    # Measurement noise covariance
    ekf.R = np.eye(9) * 0.5  # Tune this based on sensor characteristics

    # State covariance matrix
    ekf.P = np.eye(6) * 1.0  # Initial uncertainty

    return ekf

def ekf_update(ekf, accel, gyro, mag):
    """
    Updates the Kalman filter with accelerometer, gyroscope, and magnetometer data.
    
    Args:
        ekf (KalmanFilter): Kalman filter object.
        accel (np.ndarray): Accelerometer data [ax, ay, az].
        gyro (np.ndarray): Gyroscope data [gx, gy, gz].
        mag (np.ndarray): Magnetometer data [mx, my, mz].
    
    Returns:
        np.ndarray: Updated state vector [roll, pitch, yaw, roll_rate, pitch_rate, yaw_rate].
    """
    # Measurement vector (accelerometer, gyroscope, magnetometer)
    z = np.hstack((accel, gyro, mag))

    # Prediction step (Kalman filter uses the motion model)
    ekf.predict()

    # Update step (Kalman filter uses sensor measurements)
    ekf.update(z)

    # Return the estimated roll, pitch, and yaw
    return ekf.x[:3]  # Return roll, pitch, yaw

def imu_to_roll_pitch_yaw_ekf(sensor_data, fs_imu, database_name):
    """
    Convert 9-axis IMU data into roll, pitch, and yaw using Kalman filter and visualize the results.

    Args:
        sensor_data (dict): Dictionary containing IMU sensor data in time series format for Aclm, Gyro, and Mag.
        fs_imu (int): Sampling frequency of the IMU sensors.
        database_name (str): Name of the database to save the visualizations.

    Returns:
        np.ndarray: Numpy array with shape (N, 3), where N is the number of time points and 3 corresponds to roll, pitch, and yaw.
    """
 
    # Extract and trim accelerometer data to the shortest length across X, Y, Z axes
    acc_len = min(len(sensor_data["Aclm_X"]), len(sensor_data["Aclm_Y"]), len(sensor_data["Aclm_Z"]))
    acc_data = np.vstack([sensor_data["Aclm_X"][:acc_len], sensor_data["Aclm_Y"][:acc_len], sensor_data["Aclm_Z"][:acc_len]]).T  # Shape: (N, 3)

    # Extract and trim gyroscope data to the shortest length across X, Y, Z axes
    gyro_len = min(len(sensor_data["Gyro_X"]), len(sensor_data["Gyro_Y"]), len(sensor_data["Gyro_Z"]))
    gyro_data = np.vstack([sensor_data["Gyro_X"][:gyro_len], sensor_data["Gyro_Y"][:gyro_len], sensor_data["Gyro_Z"][:gyro_len]]).T  # Shape: (N, 3)

    # Extract and trim magnetometer data to the shortest length across X, Y, Z axes
    mag_len = min(len(sensor_data["Mag_X"]), len(sensor_data["Mag_Y"]), len(sensor_data["Mag_Z"]))
    mag_data = np.vstack([sensor_data["Mag_X"][:mag_len], sensor_data["Mag_Y"][:mag_len], sensor_data["Mag_Z"][:mag_len]]).T  # Shape: (N, 3)

    min_length = min(acc_data.shape[0], gyro_data.shape[0], mag_data.shape[0])

    # Trim all sensor data to the minimum length
    acc_data = acc_data[:min_length]
    gyro_data = gyro_data[:min_length]
    mag_data = mag_data[:min_length]

    # Initialize EKF
    ekf = initialize_ekf(fs_imu)

    num_samples = acc_data.shape[0]
    rpy_data = np.zeros((num_samples, 3))  # Array to store roll, pitch, yaw values for each time step

    # Apply EKF to each time step of IMU data
    for t in range(num_samples):
        roll, pitch, yaw = ekf_update(ekf, acc_data[t], gyro_data[t], mag_data[t])
        rpy_data[t, 0] = roll
        rpy_data[t, 1] = pitch
        rpy_data[t, 2] = yaw

    # =================== Visualization and Saving ===================
    time_vector = np.arange(num_samples) / fs_imu  # Create time vector

    # Create output directory if it doesn't exist
    os.makedirs('visual', exist_ok=True)

    # Plot roll, pitch, and yaw
    fig, axs = plt.subplots(3, 1, figsize=(12, 8))

    axs[0].plot(time_vector, rpy_data[:, 0], label='Roll', color='r')
    axs[0].set_title('Roll over Time')
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('Roll (rad)')
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(time_vector, rpy_data[:, 1], label='Pitch', color='g')
    axs[1].set_title('Pitch over Time')
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Pitch (rad)')
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(time_vector, rpy_data[:, 2], label='Yaw', color='b')
    axs[2].set_title('Yaw over Time')
    axs[2].set_xlabel('Time (s)')
    axs[2].set_ylabel('Yaw (rad)')
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()

    # Save the figure
    plt.savefig(f'./visual/{database_name}_roll_pitch_yaw_ekf.png', dpi=300)
    plt.clf()

    logging.info(f"Roll, pitch, and yaw visualization saved as {database_name}_roll_pitch_yaw_ekf.png")

    return rpy_data
