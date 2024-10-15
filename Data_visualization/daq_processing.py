# import numpy as np
# import logging
# from concurrent.futures import ThreadPoolExecutor

# def process_multiple_daqs(daq_files, fs_sensor):
#     """
#     Processes multiple DAQ files concurrently using ThreadPoolExecutor.
#     """
#     with ThreadPoolExecutor() as executor:
#         sensor_data_list = list(executor.map(lambda file: process_daq_data(file, fs_sensor), daq_files))
#     return sensor_data_list

# def process_daq_data(sd_file, fs_sensor):
#     """
#     Processes DAQ data file, converts to voltage, and extracts sensor data.
#     """
#     try:
#         logging.info(f"Processing DAQ data from {sd_file}")
#         # Read binary data
#         with open(sd_file, "rb") as f:
#             sd_data_original = np.fromfile(f, dtype=np.int32)

#         # Reshape data
#         n = 17  # Number of columns in converted data
#         m = len(sd_data_original) // n
#         sd_data = sd_data_original.reshape((m, n))

#         # Create sensor data structure
#         sensor_data = extract_sensor_data(sd_data)

#         logging.info(f"Data processing successful for {sd_file}")
#         return sensor_data

#     except Exception as e:
#         logging.error(f"Error processing DAQ data from {sd_file}: {e}")
#         return None

# def extract_sensor_data(sd_data):
#     """
#     Extracts and converts sensor data from raw DAQ data.
#     Processes IMU sensor data to skip consecutive zeros based on the rules.
#     """
#     sensor_data = {
#         "A0": [], "A1": [], "A2": [], "A3": [], "A4": [],
#         "A5": [], "A6": [], "A7": [], "Aclm_X": [], "Aclm_Y": [], "Aclm_Z": [],
#         "Gyro_X": [], "Gyro_Y": [], "Gyro_Z": [], "Mag_X": [],
#         "Mag_Y": [], "Mag_Z": []
#     }

#     adc_resolutions = {
#         "A0": 13, "A1": 13, "A2": 13, "A3": 13, "A4": 13,
#         "A5": 13, "A6": 13, "A7": 13,
#         "Aclm_X": 16, "Aclm_Y": 16, "Aclm_Z": 16,
#         "Gyro_X": 16, "Gyro_Y": 16, "Gyro_Z": 16,
#         "Mag_X": 16, "Mag_Y": 16, "Mag_Z": 16
#     }

#     imu_channels = ["Aclm_X", "Aclm_Y", "Aclm_Z", "Gyro_X", "Gyro_Y", "Gyro_Z", "Mag_X", "Mag_Y", "Mag_Z"]

#     # Process IMU channels with custom zero-skipping logic
#     for i, sensor_name in enumerate(imu_channels, start=8):
#         adc_resolution = adc_resolutions[sensor_name]
#         max_adc_value = 2**adc_resolution - 1
#         slope = 3.3 / max_adc_value
#         raw_imu_data = sd_data[:, i] * slope

#         # Apply the custom zero-skipping logic to the IMU sensor data
#         sensor_data[sensor_name] = process_imu_data(raw_imu_data)
        
#     IMU_aclm_x = sensor_data["Aclm_X"]
#     IMU_aclm_y = sensor_data["Aclm_Y"]

#     # Get the last 3 values from imu_aclm_x and imu_aclm_y
#     imu_aclm_x_last3 = IMU_aclm_x[-3:]
#     imu_aclm_y_last3 = IMU_aclm_y[-3:]
    
#     # Count the number of common zeros in the last 3 positions of imu_aclm_x and imu_aclm_y
#     common_trailing_zeros = 0
#     for x_val, y_val in zip(imu_aclm_x_last3, imu_aclm_y_last3):
#         if x_val == 0 and y_val == 0:
#             common_trailing_zeros += 1
#     print("\nCommon trailing zeros:", common_trailing_zeros)
#     # Extract and convert sensor data for MMG sensors (A0 to A7)
#     # Remove first two data points for MMG data, and trim trailing points based on common trailing zeros
#     for i, sensor_name in enumerate(list(sensor_data.keys())[:8]):
#         adc_resolution = adc_resolutions[sensor_name]
#         max_adc_value = 2**adc_resolution - 1
#         slope = 3.3 / max_adc_value
        
#         # Remove first two points, then trim based on common trailing zeros
#         if common_trailing_zeros > 0:
#             raw_mmg_data = sd_data[2:-common_trailing_zeros, i] * slope
#         else:
#             raw_mmg_data = sd_data[2:, i] * slope  # No trimming if no trailing zeros
        
#         sensor_data[sensor_name] = raw_mmg_data

#     return sensor_data

# def process_imu_data(data):
#     """
#     Process IMU sensor data by finding the first non-zero value and then skipping the next 3 values 
#     and counting the 4th value repeatedly.
    
#     Args:
#         data: The raw IMU data as a NumPy array.
    
#     Returns:
#         Processed IMU data where after finding the first value, the next 3 values are skipped and 
#         every 4th value is counted.
#     """
#     processed_data = []
#     found_first_non_zero = False
#     i = 0
    
#     while i < len(data):
#         if not found_first_non_zero:
#             # Find and append the first non-zero value
#             if data[i] != 0:
#                 processed_data.append(data[i])
#                 found_first_non_zero = True
#         else:
#             # After the first value, skip the next 3 values and take the 4th
#             if i + 3 < len(data):
#                 processed_data.append(data[i + 3])
#             i += 3  # Skip 3 values
            
#         # Increment the counter to continue checking the data
#         i += 1

#     print("\nProcessed sensor data:", np.sum(processed_data))
#     return np.array(processed_data)

import numpy as np
import logging

def process_multiple_daqs(daq_files, fs_sensor):
    """
    Processes multiple DAQ files sequentially.
    DAQ1 is used to determine the common_trailing_zeros from the IMU data, 
    which is then used in DAQ2 for trimming MMG data.
    """
    sensor_data_list = []
    common_trailing_zeros = None  # Variable to store trailing zeros from DAQ1

    for idx, daq_file in enumerate(daq_files):
        if idx == 0:
            # Process DAQ1 and calculate common_trailing_zeros from IMU data
            sensor_data, common_trailing_zeros = process_daq_data(daq_file, fs_sensor, calculate_trailing_zeros=True)
        else:
            # For other DAQ files, use the common_trailing_zeros from DAQ1 to trim MMG data
            sensor_data, _ = process_daq_data(daq_file, fs_sensor, calculate_trailing_zeros=False, common_trailing_zeros=common_trailing_zeros)
        
        sensor_data_list.append(sensor_data)

    return sensor_data_list

def process_daq_data(sd_file, fs_sensor, calculate_trailing_zeros=False, common_trailing_zeros=None):
    """
    Processes DAQ data file, converts to voltage, and extracts sensor data.
    If calculate_trailing_zeros is True, it calculates common_trailing_zeros from IMU data.
    If common_trailing_zeros is provided, it trims MMG data based on this value.
    """
    try:
        logging.info(f"Processing DAQ data from {sd_file}")
        # Read binary data
        with open(sd_file, "rb") as f:
            sd_data_original = np.fromfile(f, dtype=np.int32)

        # Reshape data
        n = 17  # Number of columns in converted data
        m = len(sd_data_original) // n
        sd_data = sd_data_original.reshape((m, n))

        # Extract sensor data and potentially calculate common_trailing_zeros from IMU data
        sensor_data, trailing_zeros = extract_sensor_data(sd_data, calculate_trailing_zeros, common_trailing_zeros)

        logging.info(f"Data processing successful for {sd_file}")
        return sensor_data, trailing_zeros

    except Exception as e:
        logging.error(f"Error processing DAQ data from {sd_file}: {e}")
        return None, None

def extract_sensor_data(sd_data, calculate_trailing_zeros=False, common_trailing_zeros=None):
    """
    Extracts and converts sensor data from raw DAQ data.
    If calculate_trailing_zeros is True, it calculates the trailing zeros from IMU data (Aclm_X and Aclm_Y).
    If common_trailing_zeros is provided, it trims MMG data based on this value.
    """
    sensor_data = {
        "A0": [], "A1": [], "A2": [], "A3": [], "A4": [],
        "A5": [], "A6": [], "A7": [], "Aclm_X": [], "Aclm_Y": [], "Aclm_Z": [],
        "Gyro_X": [], "Gyro_Y": [], "Gyro_Z": [], "Mag_X": [],
        "Mag_Y": [], "Mag_Z": []
    }

    adc_resolutions = {
        "A0": 13, "A1": 13, "A2": 13, "A3": 13, "A4": 13,
        "A5": 13, "A6": 13, "A7": 13,
        "Aclm_X": 16, "Aclm_Y": 16, "Aclm_Z": 16,
        "Gyro_X": 16, "Gyro_Y": 16, "Gyro_Z": 16,
        "Mag_X": 16, "Mag_Y": 16, "Mag_Z": 16
    }

    imu_channels = ["Aclm_X", "Aclm_Y", "Aclm_Z", "Gyro_X", "Gyro_Y", "Gyro_Z", "Mag_X", "Mag_Y", "Mag_Z"]
    trailing_zeros = 0

    if calculate_trailing_zeros:
        # Process IMU channels for DAQ1 to calculate the trailing zeros
        for i, sensor_name in enumerate(imu_channels, start=8):
            adc_resolution = adc_resolutions[sensor_name]
            max_adc_value = 2**adc_resolution - 1
            slope = 3.3 / max_adc_value
            raw_imu_data = sd_data[:, i] * slope

            if sensor_name == "Aclm_X":
                IMU_aclm_x = raw_imu_data
                
            if sensor_name == "Aclm_Y":
                IMU_aclm_y = raw_imu_data

            sensor_data[sensor_name] = process_imu_data(raw_imu_data)

        

        # Get the last 3 values from imu_aclm_x and imu_aclm_y
        imu_aclm_x_last3 = IMU_aclm_x[-3:]
        imu_aclm_y_last3 = IMU_aclm_y[-3:]

        # Count the number of common zeros in the last 3 positions of imu_aclm_x and imu_aclm_y
        trailing_zeros = 0
        for x_val, y_val in zip(imu_aclm_x_last3, imu_aclm_y_last3):
            if x_val == 0 and y_val == 0:
                trailing_zeros += 1
        print("\nCommon trailing zeros:", trailing_zeros)

    # Process MMG sensors (A0 to A7)
    for i, sensor_name in enumerate(list(sensor_data.keys())[:8]):
        adc_resolution = adc_resolutions[sensor_name]
        max_adc_value = 2**adc_resolution - 1
        slope = 3.3 / max_adc_value

        # Trim MMG data using common_trailing_zeros from DAQ1 if available
        if common_trailing_zeros is not None:
            raw_mmg_data = sd_data[2:-common_trailing_zeros, i] * slope
        else:
            raw_mmg_data = sd_data[2:, i] * slope  # No trimming if no trailing zeros

        sensor_data[sensor_name] = raw_mmg_data

    return sensor_data, trailing_zeros

def process_imu_data(data):
    """
    Process IMU sensor data by finding the first non-zero value and then skipping the next 3 values 
    and counting the 4th value repeatedly.
    
    Args:
        data: The raw IMU data as a NumPy array.
    
    Returns:
        Processed IMU data where after finding the first value, the next 3 values are skipped and 
        every 4th value is counted.
    """
    processed_data = []
    found_first_non_zero = False
    i = 0
    
    while i < len(data):
        if not found_first_non_zero:
            # Find and append the first non-zero value
            if data[i] != 0:
                processed_data.append(data[i])
                found_first_non_zero = True
        else:
            # After the first value, skip the next 3 values and take the 4th
            if i + 3 < len(data):
                processed_data.append(data[i + 3])
            i += 3  # Skip 3 values
            
        # Increment the counter to continue checking the data
        i += 1

    print("\nProcessed sensor data:", np.sum(processed_data))
    return np.array(processed_data)
