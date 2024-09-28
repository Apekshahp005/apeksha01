import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar
from tkcalendar import Calendar
import datetime
import time
import threading
import winsound  # Import winsound for playing beep sound

# Data structure to hold events
events = []
selected_dates = []  # List to hold selected dates

# Function to add an event with selected dates
def add_event():
    event_name = event_name_entry.get().strip()

    if not selected_dates:
        messagebox.showerror("Invalid Input", "Please select at least one date for the event.")
        return

    event_time = event_time_entry.get().strip()

    # Validate time format
    try:
        event_datetime = datetime.datetime.strptime(f"{selected_dates[0]} {event_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        messagebox.showerror("Invalid Input", "Invalid time format. Please use HH:MM in 24-hour format.")
        return

    # Check if any event datetime is in the future
    for event_date in selected_dates:
        if datetime.datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M") <= datetime.datetime.now():
            messagebox.showerror("Invalid Input", "Event date and time must be in the future. Please try again.")
            return

    # Add event to the list for each selected date
    for event_date in selected_dates:
        events.append({
            'name': event_name,
            'date': event_date,
            'time': event_time,
            'recurrence': get_selected_recurrence()
        })

    messagebox.showinfo("Success", f"Event '{event_name}' added successfully for multiple dates!")
    show_events()  # Update event list display

# Function to show all events
def show_events():
    event_listbox.delete(0, tk.END)
    if not events:
        event_listbox.insert(tk.END, "No events found.")
    else:
        for idx, event in enumerate(events, start=1):
            event_listbox.insert(tk.END, f"{idx}. Event: {event['name']} | Date: {event['date']} | Time: {event['time']} | Recurrence: {event['recurrence']}")

# Function to get selected recurrence options
def get_selected_recurrence():
    selected_options = [recurrence_listbox.get(i) for i in recurrence_listbox.curselection()]
    return ', '.join(selected_options) if selected_options else 'None'

# Function to set a reminder for an event
def set_reminder():
    if not events:
        messagebox.showinfo("No Events", "No events to set reminders for.")
        return

    try:
        selected_idx = event_listbox.curselection()[0]
    except IndexError:
        messagebox.showinfo("Selection Error", "Please select an event to set a reminder for.")
        return

    selected_event = events[selected_idx]

    try:
        reminder_minutes = int(reminder_minutes_entry.get().strip())
        if reminder_minutes < 0:
            messagebox.showerror("Invalid Input", "Reminder time cannot be negative.")
            return
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for reminder minutes.")
        return

    # Calculate reminder time for the selected date
    event_date = selected_event['date']
    event_datetime = datetime.datetime.strptime(f"{event_date} {selected_event['time']}", "%Y-%m-%d %H:%M")
    reminder_datetime = event_datetime - datetime.timedelta(minutes=reminder_minutes)

    if reminder_datetime <= datetime.datetime.now():
        messagebox.showerror("Invalid Time", f"Reminder time for {event_date} is in the past. Skipping.")
        return

    # Calculate time to wait in seconds
    wait_seconds = (reminder_datetime - datetime.datetime.now()).total_seconds()

    messagebox.showinfo("Reminder Set", f"Reminder set for '{selected_event['name']}' on {event_date} at {reminder_datetime.strftime('%Y-%m-%d %H:%M')}.")

    # Start a thread to wait and then play the reminder sound
    reminder_thread = threading.Thread(target=reminder_worker, args=(wait_seconds,))
    reminder_thread.daemon = True  # Daemon thread will exit when main program exits
    reminder_thread.start()

# Function to play a reminder sound
def reminder_worker(wait_seconds):
    # Wait until the reminder time
    time.sleep(wait_seconds)
    winsound.Beep(1000, 1000)  # Beep at 1000 Hz for 1 second
    messagebox.showinfo("Reminder", "Time to attend your event!")

# Function to select a date and add it to the list
def select_date():
    selected_date = calendar.get_date()
    if selected_date not in selected_dates:
        selected_dates.append(selected_date)
        selected_dates_label.config(text=", ".join(selected_dates))
    else:
        messagebox.showinfo("Date Already Selected", "This date has already been selected.")

# Creating the main window
root = tk.Tk()
root.title("Academic Calendar Manager")

# Create and place widgets
tk.Label(root, text="Event Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
event_name_entry = tk.Entry(root)
event_name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Select Date:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
calendar = Calendar(root, date_pattern='yyyy-mm-dd')
calendar.grid(row=1, column=1, padx=10, pady=5)

select_date_button = tk.Button(root, text="Add Date", command=select_date)
select_date_button.grid(row=2, column=0, columnspan=2, pady=10)

tk.Label(root, text="Selected Dates:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
selected_dates_label = tk.Label(root, text="")
selected_dates_label.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

tk.Label(root, text="Event Time (HH:MM):").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
event_time_entry = tk.Entry(root)
event_time_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Recurrence Options:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)

# Listbox for recurrence options
recurrence_listbox = Listbox(root, selectmode='multiple', height=4)
recurrence_options = ['None', 'Weekly', 'Monthly']
for option in recurrence_options:
    recurrence_listbox.insert(tk.END, option)

recurrence_listbox.grid(row=5, column=1, padx=10, pady=5)

add_event_button = tk.Button(root, text="Add Event", command=add_event)
add_event_button.grid(row=6, column=0, columnspan=2, pady=10)

tk.Label(root, text="Event List:").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
event_listbox = tk.Listbox(root, width=80, height=10)
event_listbox.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

tk.Label(root, text="Reminder Time (minutes before event):").grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
reminder_minutes_entry = tk.Entry(root)
reminder_minutes_entry.grid(row=9, column=1, padx=10, pady=5)

set_reminder_button = tk.Button(root, text="Set Reminder", command=set_reminder)
set_reminder_button.grid(row=10, column=0, columnspan=2, pady=10)

# Run the GUI loop
root.mainloop()