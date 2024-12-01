# main.py
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import pandas as pd
from tkinter import filedialog
from backend_analysis import (
    load_dataset,
    train_model, 
    calculate_predicted_demand,
    distribute_energy,
    generate_prediction_map,
    generate_distribution_map
)

# Load dataset and train model
df = load_dataset()
model = train_model(df)

# Create the main application window
root = tk.Tk()
root.title("Energy Distribution and Prediction")

# Maximize the window
root.state('zoomed')

# Define font sizes
font_size_large = 14  # For labels and buttons
font_size_small = 12  # For Entry and DateEntry
large_font = font.Font(size=font_size_large)
title_font = font.Font(size=18, weight='bold')  # Title font size
small_font = font.Font(size=font_size_small)  # Smaller font size for Entry and DateEntry

# Color palette
taskbar_color = '#003366'  # Dark Blue
background_color = '#F5F5F5'  # White Smoke
frame_color = '#F9F9F9'  # Off White
button_color = '#004d40'  # Dark Teal
button_hover_color = '#00796b'  # Teal Hover
text_color = '#333333'  # Charcoal
title_color = '#FFFFFF'  # White for title text

# Create a top taskbar frame
taskbar_frame = tk.Frame(root, bg=taskbar_color, height=50)
taskbar_frame.pack(fill='x', side='top')

# Add a title to the taskbar frame
title_label = tk.Label(taskbar_frame, text="Energy Predictor and Distributor", font=title_font, bg=taskbar_color, fg=title_color)
title_label.pack(pady=10)

# Create the prediction and distribution frames
main_frame = tk.Frame(root, bg=background_color)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Set equal weight to the columns in main_frame
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Set equal weight to the rows in main_frame
main_frame.grid_rowconfigure(0, weight=1)

# Create the left frame for prediction
left_frame = tk.Frame(main_frame, bg=frame_color, relief='flat')
left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
left_frame.grid_rowconfigure(3, weight=1)
left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_columnconfigure(1, weight=1)
left_frame.grid_columnconfigure(2, weight=1)  # Added column for download button

# Create the right frame for distribution
right_frame = tk.Frame(main_frame, bg=frame_color, relief='flat')
right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
right_frame.grid_rowconfigure(3, weight=1)
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_columnconfigure(1, weight=1)
right_frame.grid_columnconfigure(2, weight=1)  # Added column for download button

# Function to handle button hover effects
def on_enter(e):
    e.widget['background'] = button_hover_color

def on_leave(e):
    e.widget['background'] = button_color

# Function to crop and update prediction map image
def update_prediction_map(image_path):
    img = Image.open(image_path)
    
    # Crop the image to remove whitespace (adjust the cropping box as needed)
    left = 50
    top = 80
    right = img.width - 75
    bottom = img.height - 65
    img = img.crop((left, top, right, bottom))
    
    # Resize the cropped image
    img = img.resize((650, 480), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)

    if hasattr(update_prediction_map, "prediction_img_label"):
        update_prediction_map.prediction_img_label.config(image=img)
        update_prediction_map.prediction_img_label.image = img
    else:
        update_prediction_map.prediction_img_label = tk.Label(left_frame, image=img, bg=frame_color)
        update_prediction_map.prediction_img_label.image = img
        update_prediction_map.prediction_img_label.grid(row=3, column=0, columnspan=3, pady=10, sticky="nsew")

    # Show download button for prediction result
    download_button = tk.Button(left_frame, text="Download Result", command=download_prediction_result, font=large_font, bg=button_color, fg='white', relief='flat')
    download_button.grid(row=1, column=1, pady=10, padx=0, sticky='ew')
    download_button.bind("<Enter>", on_enter)
    download_button.bind("<Leave>", on_leave)

# Function to crop and update distribution map image
def update_distribution_map(image_path):
    img = Image.open(image_path)
    
    # Crop the image to remove whitespace (adjust the cropping box as needed)
    left = 50
    top = 80
    right = img.width - 75
    bottom = img.height - 65
    img = img.crop((left, top, right, bottom))
    
    # Resize the cropped image
    img = img.resize((650, 480), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)

    if hasattr(update_distribution_map, "distribution_img_label"):
        update_distribution_map.distribution_img_label.config(image=img)
        update_distribution_map.distribution_img_label.image = img
    else:
        update_distribution_map.distribution_img_label = tk.Label(right_frame, image=img, bg=frame_color)
        update_distribution_map.distribution_img_label.image = img
        update_distribution_map.distribution_img_label.grid(row=3, column=0, columnspan=3, pady=10, sticky="nsew")

    # Show download button for distribution result
    download_button = tk.Button(right_frame, text="Download Result", command=download_distribution_result, font=large_font, bg=button_color, fg='white', relief='flat')
    download_button.grid(row=1, column=1, pady=10, padx=0, sticky='ew')
    download_button.bind("<Enter>", on_enter)
    download_button.bind("<Leave>", on_leave)

# Define functions to integrate with backend
def predict_energy_usage():
    selected_date = date_picker.get_date()
    predicted_demand_df = calculate_predicted_demand(df, selected_date, model)
    prediction_map_path = generate_prediction_map(predicted_demand_df)
    update_prediction_map(prediction_map_path)
    # Save prediction result to a global variable
    predict_energy_usage.result_df = predicted_demand_df
    total=predicted_demand_df['predicted_energy'].sum()
    tot_energy = tk.Label(left_frame, text="Total Energy Required= "+str(total), font=large_font, bg=frame_color, fg=text_color)
    tot_energy.grid(row=2, column=0, columnspan=3, pady=10, padx=0, sticky='ew')

def distribute_energy_usage():
    generated_energy = float(energy_input.get())
    selected_date = date_picker.get_date()
    selected_date = pd.to_datetime(selected_date)
    # Use the model to predict demand instead of calculating historical demand
    predicted_demand_df = calculate_predicted_demand(df, selected_date, model)
    allocation_result_df = distribute_energy(generated_energy, predicted_demand_df)
    distribution_map_path = generate_distribution_map(allocation_result_df)
    update_distribution_map(distribution_map_path)
    # Save distribution result to a global variable
    distribute_energy_usage.result_df = allocation_result_df
    total=predicted_demand_df['predicted_energy'].sum()
    if total<generated_energy:
        suff="Sufficient energy"
    else:
        suff="Insufficient energy"
    sufficiency = tk.Label(right_frame, text=suff, font=large_font, bg=frame_color, fg=text_color)
    sufficiency.grid(row=2, column=0, columnspan=3, pady=10, padx=0, sticky='ew')

def download_prediction_result():
    if hasattr(predict_energy_usage, 'result_df'):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            predict_energy_usage.result_df.to_excel(file_path, index=False)

def download_distribution_result():
    if hasattr(distribute_energy_usage, 'result_df'):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            distribute_energy_usage.result_df.to_excel(file_path, index=False)

# Add widgets to the left frame (prediction)
date_label = tk.Label(left_frame, text="Select Date:", font=large_font, bg=frame_color, fg=text_color)
date_label.grid(row=0, column=0, pady=10, padx=5, sticky='e')
date_picker = DateEntry(left_frame, width=15, background=button_color, foreground='white', borderwidth=1, font=small_font, relief='solid')
date_picker.grid(row=0, column=1, pady=10, padx=5, sticky='w')

predict_button = tk.Button(left_frame, text="Predict", command=predict_energy_usage, font=large_font, bg=button_color, fg='white', relief='flat')
predict_button.grid(row=1, column=0, pady=20, padx=100, sticky='ew')
predict_button.bind("<Enter>", on_enter)
predict_button.bind("<Leave>", on_leave)

# Add widgets to the right frame (distribution)
energy_label = tk.Label(right_frame, text="Enter Generated Energy:", font=large_font, bg=frame_color, fg=text_color)
energy_label.grid(row=0, column=0, pady=10, padx=5, sticky='e')
energy_input = tk.Entry(right_frame, font=small_font, relief='solid', borderwidth=1)
energy_input.grid(row=0, column=1, pady=10, padx=5, sticky='w')

distribute_button = tk.Button(right_frame, text="Distribute", command=distribute_energy_usage, font=large_font, bg=button_color, fg='white', relief='flat')
distribute_button.grid(row=1, column=0, pady=20, padx=100, sticky='ew')
distribute_button.bind("<Enter>", on_enter)
distribute_button.bind("<Leave>", on_leave)

# Fix the frame size and prevent them from resizing
left_frame.grid_propagate(False)
right_frame.grid_propagate(False)

# Ensure both frames expand equally
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Set the width of both frames explicitly to ensure they are equal
left_frame.config(width=800)  # Adjust width as needed
right_frame.config(width=800)  # Adjust width as needed

# Start the Tkinter event loop
root.mainloop()