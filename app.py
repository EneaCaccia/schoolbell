import tkinter as tk
from tkinter import messagebox
from tkinter.simpledialog import askstring
import pygame
import os
import logging
from datetime import datetime, timedelta
import time

# Initialize pygame mixer for playing sound
pygame.mixer.init()

# Constants
CONFIG_FILE = 'bell_times.txt'
SOUND_FILE = 'school_bell.mp3'

# A dictionary to track which times have been played today
played_times = {}

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load times from the configuration file
def load_times():
    if not os.path.exists(CONFIG_FILE):
        logging.debug(f"{CONFIG_FILE} not found, returning an empty list.")
        return []
    with open(CONFIG_FILE, 'r') as file:
        times = file.read().splitlines()
    times_sorted = sorted(times)
    logging.debug(f"Loaded times: {times_sorted}")
    return times_sorted

# Function to save times to the configuration file
def save_times(times):
    with open(CONFIG_FILE, 'w') as file:
        file.write("\n".join(times))
    logging.debug(f"Saved times: {times}")

# Function to play the bell sound 3 times
def play_bell():
    if os.path.exists(SOUND_FILE):
        # Load the sound file to calculate its duration
        sound = pygame.mixer.Sound(SOUND_FILE)
        sound_length = sound.get_length()  # Duration of the sound in seconds
        
        for _ in range(5):  # Play the bell seven times
            pygame.mixer.music.load(SOUND_FILE)
            pygame.mixer.music.play()
            time.sleep(sound_length)  # Wait for the length of the sound before playing again
        logging.info("Bell played 7 times.")
    else:
        messagebox.showerror("Error", "Bell sound file not found.")
        logging.error(f"Sound file {SOUND_FILE} not found.")

# Function to add a new bell time (separate fields for hour, minute, and AM/PM)
def add_time():
    def submit_time():
        # Get values from input fields
        hour = hour_entry.get()
        minute = minute_entry.get()
        ampm = ampm_var.get()

        # Validate hour and minute inputs
        if not hour.isdigit() or not minute.isdigit():
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for hour and minute.")
            logging.warning(f"Invalid hour ({hour}) or minute ({minute}) entered.")
            return
        
        hour = int(hour)
        minute = int(minute)

        if hour < 1 or hour > 12:
            messagebox.showerror("Invalid Hour", "Please enter an hour between 1 and 12.")
            logging.warning(f"Invalid hour entered: {hour}")
            return
        if minute < 0 or minute > 59:
            messagebox.showerror("Invalid Minute", "Please enter a minute between 0 and 59.")
            logging.warning(f"Invalid minute entered: {minute}")
            return
        
        # Format time as HH:MM AM/PM
        time_str = f"{hour:02d}:{minute:02d} {ampm}"

        # Load existing times and add the new time if it's not already in the list
        times = load_times()
        if time_str not in times:
            times.append(time_str)
            times.sort()
            save_times(times)
            update_times_list()
            new_window.destroy()  # Close the add-time window
            logging.info(f"Added new time: {time_str}")
        else:
            messagebox.showwarning("Duplicate Time", "This time is already added.")
            logging.info(f"Duplicate time attempt: {time_str}")

    # Create a new window to input hour, minute, and AM/PM
    new_window = tk.Toplevel(root)
    new_window.title("Add Time")

    # Hour input
    hour_label = tk.Label(new_window, text="Hour (1-12):")
    hour_label.grid(row=0, column=0)
    hour_entry = tk.Entry(new_window)
    hour_entry.grid(row=0, column=1)

    # Minute input
    minute_label = tk.Label(new_window, text="Minute (0-59):")
    minute_label.grid(row=1, column=0)
    minute_entry = tk.Entry(new_window)
    minute_entry.grid(row=1, column=1)

    # AM/PM radio buttons
    ampm_label = tk.Label(new_window, text="AM/PM:")
    ampm_label.grid(row=2, column=0)

    # Create a variable to store the AM/PM selection
    ampm_var = tk.StringVar(value="AM")

    # Create the AM radio button
    am_radio = tk.Radiobutton(new_window, text="AM", variable=ampm_var, value="AM")
    am_radio.grid(row=2, column=1)

    # Create the PM radio button
    pm_radio = tk.Radiobutton(new_window, text="PM", variable=ampm_var, value="PM")
    pm_radio.grid(row=2, column=2)

    # Submit Button
    submit_button = tk.Button(new_window, text="Submit", command=submit_time)
    submit_button.grid(row=3, columnspan=3)

    # Focus on the hour input field
    hour_entry.focus()

# Function to delete a selected time
def delete_time():
    selected_time = times_listbox.curselection()
    if selected_time:
        time = times_listbox.get(selected_time)
        times = load_times()
        times.remove(time)
        save_times(times)
        update_times_list()
        logging.info(f"Deleted time: {time}")
    else:
        messagebox.showwarning("Selection Error", "Please select a time to delete.")
        logging.warning("Delete time attempt with no selection.")

# Function to update the times listbox
def update_times_list():
    times = load_times()
    times_listbox.delete(0, tk.END)
    for time in times:
        times_listbox.insert(tk.END, time)
    logging.debug("Updated times list in UI.")

# Function to update the current time in the label
def update_current_time():
    current_time = datetime.now().strftime("%I:%M:%S %p")  # Format in HH:MM:SS AM/PM
    current_time_label.config(text=current_time)
    root.after(1000, update_current_time)  # Update every 1 second
    # logging.debug(f"Updated current time: {current_time}")

# Function to check if the bell should ring
def check_bell_time():
    current_time = datetime.now().strftime("%I:%M %p")  # Current time in HH:MM AM/PM format
    current_date = datetime.now().strftime("%Y-%m-%d")  # Current date in YYYY-MM-DD format
    times = load_times()

    # Ensure the times in the configuration file are in the same format
    if current_date not in played_times:
        played_times[current_date] = set()
    logging.debug(f"Played times for today: {played_times[current_date]}")

    # If the current time matches a saved time and hasn't been played today
    if current_time in times and current_time not in played_times[current_date]:
        play_bell()  # Play the bell sound if the time matches
        played_times[current_date].add(current_time)  # Mark this time as played
        logging.info(f"Bell played for time: {current_time}")

    root.after(1000, check_bell_time)  # Check every second

# Function to reset played times at midnight
def reset_played_times():
    current_time = datetime.now()
    next_midnight = datetime.combine(current_time + timedelta(days=1), datetime.min.time())
    time_to_sleep = (next_midnight - current_time).total_seconds()

    # Schedule resetting played_times at midnight
    root.after(int(time_to_sleep * 1000), reset_played_times)
    played_times.clear()  # Clear played times for the new day
    logging.info("Played times cleared for the new day.")

# Function to edit a selected time
def edit_time():
    selected_time = times_listbox.curselection()
    if selected_time:
        old_time = times_listbox.get(selected_time)
        
        # Extract hour, minute, and AM/PM from the old time
        hour, minute_ampm = old_time.split(":")
        minute, ampm = minute_ampm.split()
        
        def submit_edit():
            new_hour = hour_entry.get()
            new_minute = minute_entry.get()
            new_ampm = ampm_var.get()

            # Validate new input
            if not new_hour.isdigit() or not new_minute.isdigit():
                messagebox.showerror("Invalid Input", "Please enter valid numeric values for hour and minute.")
                logging.warning(f"Invalid hour ({new_hour}) or minute ({new_minute}) entered in edit.")
                return

            new_hour = int(new_hour)
            new_minute = int(new_minute)

            if new_hour < 1 or new_hour > 12:
                messagebox.showerror("Invalid Hour", "Please enter an hour between 1 and 12.")
                logging.warning(f"Invalid hour entered in edit: {new_hour}")
                return
            if new_minute < 0 or new_minute > 59:
                messagebox.showerror("Invalid Minute", "Please enter a minute between 0 and 59.")
                logging.warning(f"Invalid minute entered in edit: {new_minute}")
                return

            # Format the new time
            new_time_str = f"{new_hour:02d}:{new_minute:02d} {new_ampm}"

            # Load times and replace the old time
            times = load_times()
            times[times.index(old_time)] = new_time_str
            save_times(times)
            update_times_list()
            edit_window.destroy()
            logging.info(f"Edited time: {old_time} to {new_time_str}")

        # Open a new window for editing the selected time
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Time")

        # Hour input
        hour_label = tk.Label(edit_window, text="Hour (1-12):")
        hour_label.grid(row=0, column=0)
        hour_entry = tk.Entry(edit_window)
        hour_entry.insert(0, hour)
        hour_entry.grid(row=0, column=1)

        # Minute input
        minute_label = tk.Label(edit_window, text="Minute (0-59):")
        minute_label.grid(row=1, column=0)
        minute_entry = tk.Entry(edit_window)
        minute_entry.insert(0, minute)
        minute_entry.grid(row=1, column=1)

        # AM/PM radio buttons
        ampm_label = tk.Label(edit_window, text="AM/PM:")
        ampm_label.grid(row=2, column=0)

        # Create a variable to store the AM/PM selection
        ampm_var = tk.StringVar(value=ampm)

        # Create the AM radio button
        am_radio = tk.Radiobutton(edit_window, text="AM", variable=ampm_var, value="AM")
        am_radio.grid(row=2, column=1)

        # Create the PM radio button
        pm_radio = tk.Radiobutton(edit_window, text="PM", variable=ampm_var, value="PM")
        pm_radio.grid(row=2, column=2)

        # Submit Button
        submit_button = tk.Button(edit_window, text="Submit", command=submit_edit)
        submit_button.grid(row=3, columnspan=3)

        # Focus on the hour input field
        hour_entry.focus()

    else:
        messagebox.showwarning("Selection Error", "Please select a time to edit.")
        logging.warning("Edit time attempt with no selection.")

# Creating the main application window
root = tk.Tk()
root.title("New Marigold School Bell System")
root.geometry("400x450")
root.attributes('-fullscreen', True)

# Title label
title_label = tk.Label(root, text="New Marigold School Bell System", font=("Helvetica", 14, "bold"))
title_label.pack(pady=10)

# Current Time label (updates every second)
current_time_label = tk.Label(root, font=("Helvetica", 12), fg="red")
current_time_label.pack(pady=5)

# Frame for Times Listbox and Scrollbar
times_frame = tk.Frame(root)
times_frame.pack(pady=10)

# Scrollbar
scrollbar = tk.Scrollbar(times_frame, orient=tk.VERTICAL)

# Times Listbox
times_listbox = tk.Listbox(times_frame, height=10, width=30, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set)
times_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

# Configure scrollbar to work with the listbox
scrollbar.config(command=times_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Buttons Frame
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)

# Add time button
add_button = tk.Button(buttons_frame, text="Add Time", command=add_time)
add_button.grid(row=0, column=0, padx=5)

# Delete time button
delete_button = tk.Button(buttons_frame, text="Delete Time", command=delete_time)
delete_button.grid(row=0, column=1, padx=5)

# Edit time button
edit_button = tk.Button(buttons_frame, text="Edit Time", command=edit_time)
edit_button.grid(row=0, column=2, padx=5)

# Play bell now button
play_button = tk.Button(root, text="Play Bell Now", command=play_bell)
play_button.pack(pady=10)

# Initialize times list and start the time check
update_times_list()

# Start checking the bell times and updating the current time
update_current_time()
check_bell_time()

# Reset played times at midnight
reset_played_times()

# Start the main loop
root.mainloop()