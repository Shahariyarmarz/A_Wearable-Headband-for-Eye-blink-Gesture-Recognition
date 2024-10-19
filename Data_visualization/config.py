import os

def get_daq_file_paths():
    """
    Fetch DAQ file paths from environment variables or configuration files.
    """
    return [
        os.getenv("DAQ_FILE_1", "./Data_files/DAQ1_IMU_Data07.dat"),
        os.getenv("DAQ_FILE_2", "./Data_files/DAQ2_Data07.dat")
    ]

def get_fs_MMG_sensor():
    """
    Returns the sampling frequency of the sensors.
    """
    return 256  # Can be fetched from environment or config if variable

def get_fs_IMU_sensor():
    """
    Returns the sampling frequency of the sensors.
    """
    return 64  # Can be fetched from environment or config if variable
def get_excel_file_path():
    """
    Fetch the path of the Excel file containing gesture data.
    """
    return os.getenv("EXCEL_FILE_PATH", "./modified_Sequential_Play_8.xlsx")