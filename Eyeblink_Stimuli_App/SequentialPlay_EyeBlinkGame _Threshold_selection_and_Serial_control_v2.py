import serial  # Import serial for reading data from COM5 port
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageSequence
import os
import re  # Import re for regular expressions
import time
from datetime import timedelta
import cv2
from threading import Thread, Lock
import csv

# Set up the serial connection (replace 'COM5' with your port)
ser = serial.Serial('COM5', 115200, timeout=1)  # Adjust the COM port and baudrate as needed

# Global variables for Eyeblink press duration
eyeblink_start_time = None

# Global variables
display_img_gif=True
running = False
counter = 0
current_image_index = 0
images = []
gif_animation = False
gif_frames = []
gif_index = 0
image_view_count = {}
file_create = False
running_video = False
preload_flag = False
preloaded_gifs = {}  # Dictionary to store pre-loaded GIF frames


# create a lock object to prevent multiple threads to access the main thread
lock = Lock()


def capture_video():
    global running_video
    cam = cv2.VideoCapture(0)
    frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))



    global dat_file_name
    ground_truth_folder = "Video_Files"

    # Ensure the "Ground_Truth" folder exists
    if not os.path.exists(ground_truth_folder):
        os.makedirs(ground_truth_folder)

    # Get a list of existing .dat files in the "Ground_Truth" folder
    existing_files = [f for f in os.listdir(ground_truth_folder) if f.startswith("Sequential_Play") and f.endswith(".mp4")]


    # # Get a list of existing .dat files
    # existing_files = [f for f in os.listdir() if f.startswith("Sequential_Play") and f.endswith(".csv")]
    
    # Use regex to extract the numbers and find the next number
    max_number = -1
    for file in existing_files:
        match = re.search(r"Sequential_Play_(\d+)\.mp4", file)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
    
    # Create the new file with the next number
    new_file_number = max_number + 1
    dat_file_name = os.path.join(ground_truth_folder, f"Sequential_Play_{new_file_number}.mp4")



    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # output_path = 'G:/Study design/Gestures/Video_Files/output.mp4'
    out = cv2.VideoWriter(dat_file_name, fourcc, 30.0, (frame_width, frame_height))

    while running_video:
        ret, frame = cam.read()
        if not ret:
            break
        # Write the frame to the output file
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
        

        # Display the captured frame
        # text = "Time: 00:00:00" # Text to display on the frame
        org = (50, 50)  # The bottom-left corner of the text string in the image
        font = cv2.FONT_HERSHEY_SIMPLEX  # Font type
        fontScale = 1  # Font scale (font size)
        color = (255, 0, 0)  # Color of the text (BGR)
        thickness = 2  # Thickness of the lines used to draw the text

        global counter, running, reset_once, time_str
        if running:
            # elapsed_time = timedelta(seconds=counter)  
            # time_str = str(elapsed_time)  # Convert to string to display the time
            text="Time: " + time_str
            # Call update_time again after 1000 milliseconds (1 second)
            # root.after(1000, update_time)
            # counter += 1  # Increment the counter by 1 second (1000 ms for each second)
        else:
            text="Time: 00:00:00"

        
        # Put the text on the frame
        cv2.putText(frame, text, org, font, fontScale, color, thickness, cv2.LINE_AA)
        out.write(frame)
        cv2.imshow('Camera', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    out.release()
    cv2.destroyAllWindows()

def stop_capture():
    global running_video
    running_video = False # Stop the video capture

def update_progress(value):
    progress_bar['value'] = value
    percentage_label.config(text=f"{value}%")


def left_theshold_press(event):
    global left_threshold_start_time, dat_file_name, file_create
    left_threshold_start_time = time.time()  # Record the time when the button is pressed
    if not file_create:
        create_dat_file()
        file_create = True

    with open(dat_file_name, "a") as file:
        file.write(f"Left_EyeBlink_threshold_time_window,{time_str},")

def left_threshold_release(event):
    global left_threshold_start_time, dat_file_name, file_create
    
    if left_threshold_start_time:
        # Calculate duration of the button press
        # press_duration = time.time() - left_threshold_start_time
        left_threshold_start_time = None  # Reset the start time
        
        # Ensure the .dat file is created if not already done
        if not file_create:
            create_dat_file()
            file_create = True

        # Store the press duration in the .dat file
        with open(dat_file_name, "a") as file:
            file.write(f"{time_str},\n")

    disable_left_threshold_button()
    enable_right_threshold_button()

def right_theshold_press(event):
    global right_threshold_start_time, dat_file_name, file_create
    right_threshold_start_time = time.time()  # Record the time when the button is pressed
    if not file_create:
        create_dat_file()
        file_create = True

    with open(dat_file_name, "a") as file:
        file.write(f"Right_EyeBlink_threshold_time_window,{time_str},")

def right_threshold_release(event):
    global right_threshold_start_time, dat_file_name, file_create
    
    if right_threshold_start_time:
        # Calculate duration of the button press
        # press_duration = time.time() - left_threshold_start_time
        right_threshold_start_time = None  # Reset the start time
        
        # Ensure the .dat file is created if not already done
        if not file_create:
            create_dat_file()
            file_create = True
            
        # Store the press duration in the .dat file
        with open(dat_file_name, "a") as file:
            file.write(f"{time_str},\n")

    disable_right_threshold_button()
    if images:
        current_image_index = 0
        display_image(images[current_image_index])
    else:
        messagebox.showwarning("No Images", "No image files found in the selected folder.")
    game_start_label.config(text="Game Start")  # Show "Game Start" message
    root.after(100, GameStart_label_blink)  # Delay for 1 second before restarting
    # print("Right Eye Threshold Released")



def enable_left_threshold_button():
    left_threshold_button.config(state=tk.NORMAL)

def disable_left_threshold_button():
    left_threshold_button.config(state=tk.DISABLED)

def enable_right_threshold_button():
    right_threshold_button.config(state=tk.NORMAL)

def disable_right_threshold_button():
    right_threshold_button.config(state=tk.DISABLED)

# Function to start tracking Eyeblink button press
def on_eyeblink_press(event):
    global eyeblink_start_time, dat_file_name, file_create,time_str
    eyeblink_start_time = time.time()  # Record the time when the button is pressed
    current_image_name = os.path.basename(images[current_image_index])
    image_name_without_ext = os.path.splitext(current_image_name)[0]

    if not file_create:
        create_dat_file()
        file_create = True
        
    with open(dat_file_name, "a") as file:
        file.write(f"{image_name_without_ext},{time_str},")

def on_eyeblink_release(event):
    global eyeblink_start_time, dat_file_name, file_create,time_str
    
    if eyeblink_start_time:
        # Calculate duration of the button press
        press_duration = time.time() - eyeblink_start_time
        eyeblink_start_time = None  # Reset the start time
        
        # Ensure the .dat file is created if not already done
        if not file_create:
            create_dat_file()
            file_create = True


        # Store the press duration in the .dat file
        with open(dat_file_name, "a") as file:
            file.write(f"{time_str},\n")

        
        # Trigger the next image function when the Eyeblink button is released
        #Blank screen between each image
        # image_label.config(image='')
        # image_name_label.config(text='')
        # root.after(5000, next_image)
        next_image()


# Function to start the stopwatch
def start_stopwatch():
    global running
    if not running:
        running = True
        start_button.config(state=tk.DISABLED)  # Disable the Start button after pressing
        update_time()
        enable_left_threshold_button()  # Enable the Left Threshold buttons after starting the stopwatch

# Global variable to control the reset behavior
# reset_once = False

# Function to update the stopwatch time
def update_time():
    global counter, running, reset_once, time_str
    if running:
        elapsed_time = timedelta(seconds=counter)  
        time_str = str(elapsed_time)  # Convert to string to display the time
        time_label.config(text="Time: " + time_str)
        # Call update_time again after 1000 milliseconds (1 second)
        root.after(1000, update_time)
        counter += 1  # Increment the counter by 1 second (1000 ms for each second)




        # counter += 1  # Increment counter by 1 second (1000 ms for each second)

        # # Reset the stopwatch after 10 seconds (1000 centiseconds, or 10 seconds)
        # if counter >= 10 and not reset_once:
        #     running = False  # Temporarily stop the stopwatch
        #     reset_once = True  # Prevent further resets
        #     counter = 0  # Reset the counter
        #     time_label.config(text="Time: 00:00:00")  # Reset time display
            # game_start_label.config(text="Game Start")  # Show "Game Start" message
            # root.after(1000, restart_stopwatch)  # Delay for 1 second before restarting
        # else:
        #     # Format the time using timedelta for HH:MM:SS display
        #     elapsed_time = timedelta(seconds=counter)  
        #     time_str = str(elapsed_time)  # Convert to string to display the time

        #     # Update the label with the formatted time
        #     time_label.config(text="Time: " + time_str)

        #     # Call update_time again after 1000 milliseconds (1 second)
        #     root.after(1000, update_time)

# Function to enable the "Start" button after folder selection
def enable_start_button():
    start_button.config(state=tk.NORMAL)

# Function to enable "Next" and "EyeBlink" buttons after "Game Start"
def enable_game_buttons():
    next_button.config(state=tk.NORMAL)
    blink_button.config(state=tk.NORMAL)

# Function to enable the "Save and Exit" button at the end of the game and disable all buttons
def enable_exit_button():
    quit_button.config(state=tk.NORMAL)
    # Disable all buttons once the "Save and Exit" button is enabled
    start_button.config(state=tk.DISABLED)
    next_button.config(state=tk.DISABLED)
    blink_button.config(state=tk.DISABLED)
    img_button.config(state=tk.DISABLED)

# Function to restart the stopwatch after a 1-second delay and show "Game Start"
def GameStart_label_blink():
    blink_count = 0  # Initialize the blink counter

    def blink_text():
        nonlocal blink_count
        global running
        if blink_count < 6:  # 3 blinks = 6 toggles (on/off)
            current_text = game_start_label.cget("text")
            game_start_label.config(text="" if current_text == "Game Start" else "Game Start")
            blink_count += 1
            root.after(150, blink_text)  # Continue blinking every 500ms
        else:
            game_start_label.config(text="")  # Hide the text after blinking
            enable_game_buttons()  # Enable "Next" and "EyeBlink" buttons after blinking

    blink_text()  # Start the blinking process


def preload_dialog():
    blink_count = 0  # Initialize the blink counter

    def blink_text():
        nonlocal blink_count
        global running
        if blink_count < 1:  # 3 blinks = 6 toggles (on/off)
            current_text = preload_label.cget("text")
            preload_label.config(text="" if current_text == "Preloading Done" else "Preloading Done")
            blink_count += 1
            root.after(3000, blink_text)  # Continue blinking every 500ms
        else:
            preload_label.config(text="")  # Hide the text after blinking

    blink_text()  # Start the blinking process



# Function to select a folder and load images
def select_folder():
    global images, current_image_index, gif_animation, image_view_count, full_path, preloaded_gifs, preload_flag
    folder_path = filedialog.askdirectory(title="Select Image Folder")
    if folder_path:
        images = []
        gif_animation = False
        image_view_count = {}  # Reset the view count dictionary
        preloaded_gifs = {}  # Dictionary to store preloaded GIF frames
        for file in os.listdir(folder_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                full_path = os.path.join(folder_path, file)
                images.append(full_path)
                image_view_count[full_path] = 0  # Initialize view count for each image

                # Preload GIF frames
                if file.lower().endswith('.gif'):
                    img = Image.open(full_path)
                    if img.format == 'GIF' and getattr(img, "is_animated", False):
                        frames = [ImageTk.PhotoImage(frame.copy().convert('RGBA').resize((750, 450), Image.Resampling.LANCZOS))
                                  for frame in ImageSequence.Iterator(img)]
                        preloaded_gifs[full_path] = frames
                        preload_flag = True
                        # if preload_flag:
                        preload_label.config(text="Preloading Done")
                        root.after(500, preload_dialog)
                            # preload_flag = False
                        # root.after(2000, preload_dialog)
                            # preload_flag = False

        # if images:
        #     current_image_index = 0
        #     display_image(images[current_image_index])
        # else:
        #     messagebox.showwarning("No Images", "No image files found in the selected folder.")
    else:
        messagebox.showwarning("No Selection", "No folder selected.")

def display_image(image_path):
    global gif_frames, gif_index, gif_animation, image_name_without_ext, display_img_gif, preloaded_gifs
    if display_img_gif:
        try:
            # Open the image file
            img = Image.open(image_path)
            
            # Get the image name without the extension
            current_image_name = os.path.basename(image_path)
            image_name_without_ext = os.path.splitext(current_image_name)[0]
            
            # Check if the image is an animated GIF and use preloaded frames if available
            if image_path in preloaded_gifs:
                gif_frames = preloaded_gifs[image_path]
                gif_index = 0
                gif_animation = True
                animate_gif()
            else:
                gif_animation = False
                # Convert the image to RGBA
                img = img.convert('RGBA')
                img = img.resize((500, 400), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                image_label.config(image=img_tk)
                image_label.image = img_tk  # Keep a reference to avoid garbage collection
            
            # Display the image name without extension below the image
            image_name_label.config(text=image_name_without_ext)
        
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open image file: {e}")

def animate_gif():
    global gif_index, gif_animation
    if gif_animation and gif_frames:
        gif_index = (gif_index + 1) % len(gif_frames)
        image_label.config(image=gif_frames[gif_index])
        image_label.image = gif_frames[gif_index]
        root.after(20, animate_gif)  # Adjust the delay for the GIF animation speed

# Function to generate a sequentially numbered .dat file
def create_dat_file():
    global dat_file_name
    ground_truth_folder = "Ground_Truth"

    # Ensure the "Ground_Truth" folder exists
    if not os.path.exists(ground_truth_folder):
        os.makedirs(ground_truth_folder)

    # Get a list of existing .dat files in the "Ground_Truth" folder
    existing_files = [f for f in os.listdir(ground_truth_folder) if f.startswith("Sequential_Play") and f.endswith(".csv")]


    # # Get a list of existing .dat files
    # existing_files = [f for f in os.listdir() if f.startswith("Sequential_Play") and f.endswith(".csv")]
    
    # Use regex to extract the numbers and find the next number
    max_number = -1
    for file in existing_files:
        match = re.search(r"Sequential_Play_(\d+)\.csv", file)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
    
    # Create the new file with the next number
    new_file_number = max_number + 1
    dat_file_name = os.path.join(ground_truth_folder, f"Sequential_Play_{new_file_number}.csv")
    # dat_file_name = f"Sequential_Play_{new_file_number}.csv"
    with open(dat_file_name, "w") as file:
        file.write("Gesture,Pressed,Released\n")  # Write header

# Function to go to the next image in the folder
def next_image():
    global current_image_index, gif_animation, image_view_count, file_create,display_img_gif
    if images:
        # Get the current image name
        current_image_name = os.path.basename(images[current_image_index])
        if file_create == False:
            create_dat_file()
            file_create = True

        # Increase the view count for the current image
        image_view_count[images[current_image_index]] += 1

        # Check if the current image has been viewed twice/once
        if image_view_count[full_path] >= 1:
            enable_exit_button()  # Enable the "Save and Exit" button after the game ends
            messagebox.showinfo("End", "Ending the Sequential Game session.")
            return
        

        #Blank screen between each image
        image_label.config(image='')
        image_name_label.config(text='')

        # Proceed to the next image
        display_img_gif = False
        # load_next_image()
        root.after(5000, load_next_image)
        current_image_index = (current_image_index) % len(images)
        gif_animation = False
        # display_image(images[current_image_index])
    else:
        messagebox.showwarning("No Images", "No images loaded. Please select a folder with images.")

def load_next_image():
    global current_image_index, gif_animation,display_img_gif
    display_img_gif = True
    current_image_index = (current_image_index + 1) % len(images)
    gif_animation = False
    display_image(images[current_image_index])

# Function to stop and reset the stopwatch, and close the window
def quit_application():
    global running, counter, reset_once,running_video, video_thread
    running = False
    counter = 0
    reset_once = False  # Reset the flag
    ser.close()  # Close the serial connection
    root.destroy()  # Close the application
    stop_capture()  # Stop the video capture
    running_video = False
    video_thread.join()  # Wait for the video thread to finish

# Function to switch from the welcome screen to the game screen
def load_game_screen():
    # Clear the window by removing all existing widgets
    global dat_file_name, file_create, running_video, video_thread
    for widget in root.winfo_children():
        widget.destroy()

    # Title Label
    title_label = tk.Label(root, text="Eye Blink Stimuli APP", font=("Arial", 14))
    title_label.place(relx=0.5, rely=0.05, anchor='center')

    # Level label
    level_label = tk.Label(root, text="Level-1\nSequential Play", font=("Arial", 12), borderwidth=2, relief="solid")
    level_label.place(relx=0.13, rely=0.2, anchor='center', relwidth=0.25, relheight=0.15)

    # Stopwatch label
    global time_label
    time_label = tk.Label(root, text="Time: 00:00:00", font=("Arial", 12), borderwidth=2, relief="solid")
    time_label.place(relx=0.87, rely=0.2, anchor='center', relwidth=0.25, relheight=0.15)

    # Game Start label (hidden initially)
    global game_start_label
    game_start_label = tk.Label(root, text="", font=("OCR A Extended", 30), fg="green")
    game_start_label.place(relx=0.5, rely=0.2, anchor='center')

    global preload_label
    preload_label = tk.Label(root, text="", font=("OCR A Extended", 30), fg="green")
    preload_label.place(relx=0.5, rely=0.2, anchor='center')

    # Image name label (hidden initially before selecting a folder)
    global image_name_label
    image_name_label = tk.Label(root, text="", font=("Arial", 20, "bold"), fg="blue")
    image_name_label.place(relx=0.5, rely=0.3, anchor='center')  # Position below the image in the center

    # Main image or task area
    task_frame = tk.Frame(root, borderwidth=2, relief="solid")
    task_frame.place(relx=0.5, rely=0.65, anchor='center', relwidth=0.5, relheight=0.6)

    # Image label to display the selected image
    global image_label
    image_label = tk.Label(task_frame)
    image_label.pack(expand=True)

    # Select Image Folder button
    global img_button
    img_button = tk.Button(root, text="Select Folder", font=("Arial", 12), borderwidth=4, relief="raised", command=select_folder, bg="#6FC954", activebackground="gray")
    img_button.place(relx=0.12, rely=0.4, anchor='center', relwidth=0.15, relheight=0.1)

    # Save and Exit button (initially disabled)
    global quit_button
    quit_button = tk.Button(root, text="Save and Exit", font=("Arial", 12), borderwidth=4, relief="raised", command=quit_application, bg="#FF0000", activebackground="gray", state=tk.DISABLED)
    quit_button.place(relx=0.12, rely=0.9, anchor='center', relwidth=0.15, relheight=0.1)

    # Start button (initially disabled)
    global start_button
    start_button = tk.Button(root, text="START", font=("Arial", 12), borderwidth=4, relief="raised", command=start_stopwatch, bg="#6FC954", activebackground="gray", state=tk.DISABLED)
    start_button.place(relx=0.88, rely=0.4, anchor='center', relwidth=0.15, relheight=0.1)

    # Next button (initially disabled)
    global next_button
    next_button = tk.Button(root, text="Next >>", font=("Arial", 12), borderwidth=4, relief="raised", command=next_image, bg="#6FC954", activebackground="gray", state=tk.DISABLED)
    next_button.place(relx=0.88, rely=0.9, anchor='center', relwidth=0.15, relheight=0.1)

    # Blink and Head movement window detection button (initially disabled)
    global blink_button
    blink_button = tk.Button(root, text="EyeBlink", font=("Arial", 12), borderwidth=4, relief="raised", bg="#6FC954", activebackground="gray", state=tk.DISABLED)
    blink_button.place(relx=0.88, rely=0.65, anchor='center', relwidth=0.15, relheight=0.1)

    # Left and Right Eye Threshold button (initially disabled before selecting folder and starting the stopwatch) for calibration
    global left_threshold_button
    left_threshold_button = tk.Button(root, text="Left Eye Threshold", font=("Arial", 12), borderwidth=4, relief="raised", bg="#6FC954", activebackground="gray", state=tk.DISABLED,wraplength=100)
    left_threshold_button.place(relx=0.12, rely=0.567, anchor='center', relwidth=0.15, relheight=0.1)

    global right_threshold_button
    right_threshold_button = tk.Button(root, text="Right Eye Threshold", font=("Arial", 12), borderwidth=4, relief="raised", bg="#6FC954", activebackground="gray", state=tk.DISABLED,wraplength=100)
    right_threshold_button.place(relx=0.12, rely=0.734, anchor='center', relwidth=0.15, relheight=0.1)

    left_threshold_button.bind("<ButtonPress-1>", left_theshold_press)
    left_threshold_button.bind("<ButtonRelease-1>", left_threshold_release)

    right_threshold_button.bind("<ButtonPress-1>", right_theshold_press)
    right_threshold_button.bind("<ButtonRelease-1>", right_threshold_release)

    # Bind the button press and release events to track the duration
    blink_button.bind("<ButtonPress-1>", on_eyeblink_press)
    blink_button.bind("<ButtonRelease-1>", on_eyeblink_release)

    # select_folder()  # Automatically select the image folder

    with lock:
        if not running_video:
            running_video = True
            video_thread = Thread(target=capture_video)
            video_thread.start()

    if not file_create:
        select_folder()
        create_dat_file()
        img_button.config(state=tk.DISABLED)
        file_create = True

    # Start reading serial data
    root.after(100, read_serial)  # Periodically check for serial data

# Function to read serial data and trigger the game start
def read_serial():
    global dat_file_name, file_create, running_video, video_thread
    if ser.in_waiting > 0:  # Check if data is available in the serial buffer
        serial_data = ser.readline().decode('utf-8').strip()  # Read and decode the serial data
        if serial_data == "StartEyeblinkGame":  # If the correct command is received
            start_stopwatch()  # Trigger the game start by calling the stopwatch function
            # with lock:
            #     if not running_video:
            #         running_video = True
            #         video_thread = Thread(target=capture_video)
            #         video_thread.start()
            
            # if not file_create:
            #     select_folder()
            #     create_dat_file()
            #     img_button.config(state=tk.DISABLED)
            #     file_create = True
            

    # Schedule the function to be called again after 100 ms
    root.after(100, read_serial)

# Create the main window
root = tk.Tk()
root.geometry("800x600")
root.title("Eye Blink Stimuli App")

welcome_image = ImageTk.PhotoImage(Image.open("G:\Illustator Wearable Design\Wearable design_v2.jpg").resize((300, 300), Image.Resampling.LANCZOS))

# Display the welcome message
welcome_label = tk.Label(root, text="EYEBLINK Stimuli APP !", font=("OCR A Extended", 30), fg="Black", borderwidth=2, relief="solid")
welcome_label.place(relx=0.5, rely=0.2, anchor="center", relwidth=0.9, relheight=0.15)
welcome_label.config(bg="orange", compound="center")

wel_image_label = tk.Label(root, image=welcome_image)
wel_image_label.place(relx=0.51, rely=0.6, anchor="center", relwidth=0.9, relheight=0.5)

# Create a ttk Progressbar widget
progress_bar = ttk.Progressbar(root, orient='horizontal', length=800, mode='determinate')
progress_bar.place(relx=0.5, rely=0.98, anchor='center')

# Label to show percentage
percentage_label = tk.Label(root, text="0%", font=("OCR A Extended", 20))
percentage_label.place(relx=0.5, rely=0.9, anchor='center')

# Update the progress bar
for i in range(101):
    root.after(i*50, lambda v=i: update_progress(v))  # Simulate progress over time

# Switch to the main game screen after a 3-second delay
root.after(5000, load_game_screen)

# Run the application
root.mainloop()
# Ensure the video thread stops when the tkinter window is closed
running_video = False
# video_thread.join()
# Close the serial connection when the application exits
ser.close()
