import pandas as pd
from datetime import timedelta, time

# Load the Excel file
file_path = './Data_files/Sequential_Play_8.xlsx'
file_name = (file_path.split('.')[1]).split('/')[-1]  # Extract the file name

df = pd.read_excel(file_path)  # Read the Excel file

# Function to convert datetime.time and string formats to timedelta
def time_to_timedelta(time_val):
    if isinstance(time_val, str):
        # Try parsing time as a string (e.g., "00:00:06")
        return pd.to_timedelta(time_val, errors='coerce')
    elif isinstance(time_val, time):
        # Convert datetime.time to timedelta since midnight
        return timedelta(hours=time_val.hour, minutes=time_val.minute, seconds=time_val.second)
    else:
        return pd.NaT  # Return NaT if it doesn't match either

# Apply the conversion function to the "Pressed" and "Released" columns
df['Pressed'] = df['Pressed'].apply(time_to_timedelta)
df['Released'] = df['Released'].apply(time_to_timedelta)

# Add 13 seconds to both "Pressed" and "Released" times (only if they are valid)
df['Pressed'] = df['Pressed'].apply(lambda x: x + timedelta(seconds=13) if pd.notna(x) else x)
df['Released'] = df['Released'].apply(lambda x: x + timedelta(seconds=13) if pd.notna(x) else x)

# Convert Pressed and Released columns to total seconds
df['Pressed'] = df['Pressed'].apply(lambda x: x.total_seconds() if pd.notna(x) else x)
df['Released'] = df['Released'].apply(lambda x: x.total_seconds() if pd.notna(x) else x)

# Add the 'Head_movement' column to the DataFrame
# Assuming you already have the 'Head_movement' data in a list or can compute it
# Here, we manually define a list of head movements as an example
head_movement_data = [0, 1, 2, 2, 1, 0, 1, 2, 2, 1]  # Example data
df['Head_movement'] = head_movement_data  # Add the new column

# save the updated dataframe to a new Excel file
output_file = f'modified_{file_name}.xlsx'
df.to_excel(output_file, index=False)

print(f"DataFrame saved to {output_file}")
