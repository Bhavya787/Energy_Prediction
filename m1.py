import tkinter as tk
from tkinter import ttk, font, filedialog
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import pandas as pd

# Import backend functions
from backend_analysis import (
    load_dataset as load_analysis_dataset,
    train_model as train_analysis_model,
    calculate_predicted_demand,
    distribute_energy,
    generate_prediction_map,
    generate_distribution_map
)
from backend import (
    load_dataset as load_renewable_dataset,
    train_model as train_renewable_model,
    predict_solar_energy,
    predict_wind_energy,
    recommend_energy_source
)

# Load datasets and train models
analysis_df = load_analysis_dataset()
analysis_model = train_analysis_model(analysis_df)

renewable_df = load_renewable_dataset()
renewable_model = train_renewable_model(renewable_df)

# Create main application window
root = tk.Tk()
root.title("Energy Management System")
root.geometry("1400x900")

# Create tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Fonts and colors
font_large = font.Font(size=14)
font_small = font.Font(size=12)
title_font = font.Font(size=18, weight='bold')
bg_color = "#F5F5F5"
frame_color = "#F9F9F9"
button_color = "#004d40"
button_hover_color = "#00796b"
text_color = "#333333"

# Button hover effect
def on_enter(e):
    e.widget["background"] = button_hover_color

def on_leave(e):
    e.widget["background"] = button_color

# -------------------- City-Wide Energy Distribution Tab -------------------- #
distribution_tab = tk.Frame(notebook, bg=bg_color)
notebook.add(distribution_tab, text="City-Wide Energy Distribution")

# Left Frame (Prediction)
left_frame = tk.Frame(distribution_tab, bg=frame_color)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

tk.Label(left_frame, text="Select Date:", font=font_large, bg=frame_color, fg=text_color).pack(pady=10)
date_picker = DateEntry(left_frame, width=15, font=font_small)
date_picker.pack(pady=5)

def update_image(image_path, parent_frame, row, col_span):
    img = Image.open(image_path)
    img = img.resize((650, 480), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    label = tk.Label(parent_frame, image=img, bg=frame_color)
    label.image = img
    label.grid(row=row, column=0, columnspan=col_span, pady=10)

def predict_energy_usage():
    selected_date = date_picker.get_date()
    predicted_demand_df = calculate_predicted_demand(analysis_df, selected_date, analysis_model)
    prediction_map_path = generate_prediction_map(predicted_demand_df)
    update_image(prediction_map_path, left_frame, row=4, col_span=2)
    predict_energy_usage.result_df = predicted_demand_df

tk.Button(left_frame, text="Predict Energy Usage", bg=button_color, fg="white", command=predict_energy_usage).pack(pady=10)

def download_prediction():
    if hasattr(predict_energy_usage, "result_df"):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            predict_energy_usage.result_df.to_excel(file_path, index=False)

tk.Button(left_frame, text="Download Prediction", bg=button_color, fg="white", command=download_prediction).pack(pady=10)

# Right Frame (Distribution)
right_frame = tk.Frame(distribution_tab, bg=frame_color)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

tk.Label(right_frame, text="Enter Generated Energy:", font=font_large, bg=frame_color, fg=text_color).pack(pady=10)
energy_input = tk.Entry(right_frame, font=font_small)
energy_input.pack(pady=5)

def distribute_energy_usage():
    generated_energy = float(energy_input.get())
    selected_date = date_picker.get_date()
    predicted_demand_df = calculate_predicted_demand(analysis_df, selected_date, analysis_model)
    allocation_result_df = distribute_energy(generated_energy, predicted_demand_df)
    distribution_map_path = generate_distribution_map(allocation_result_df)
    update_image(distribution_map_path, right_frame, row=4, col_span=2)
    distribute_energy_usage.result_df = allocation_result_df

tk.Button(right_frame, text="Distribute Energy", bg=button_color, fg="white", command=distribute_energy_usage).pack(pady=10)

def download_distribution():
    if hasattr(distribute_energy_usage, "result_df"):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            distribute_energy_usage.result_df.to_excel(file_path, index=False)

tk.Button(right_frame, text="Download Distribution", bg=button_color, fg="white", command=download_distribution).pack(pady=10)

# ------------------- Solar and Wind Energy Estimation Tab ------------------- #
renewable_tab = tk.Frame(notebook, bg=bg_color)
notebook.add(renewable_tab, text="Solar & Wind Energy Estimation")

# Solar Energy Frame
solar_frame = tk.Frame(renewable_tab, bg=frame_color)
solar_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

tk.Label(solar_frame, text="Solar Energy Prediction", font=font_large, bg=frame_color).pack(pady=10)
tk.Label(solar_frame, text="Rooftop Area (m²):", bg=frame_color).pack(anchor="w")
rooftop_area_entry = tk.Entry(solar_frame)
rooftop_area_entry.pack(pady=5)

def calculate_solar():
    area = float(rooftop_area_entry.get())
    orientation = "South"  # Assume fixed for simplicity
    climate_data = {"solar_irradiance": 5.5}
    energy = predict_solar_energy(area, orientation, climate_data)
    tk.Label(solar_frame, text=f"Predicted Solar Energy: {energy:.2f} kWh", bg=frame_color).pack(pady=10)

tk.Button(solar_frame, text="Predict Solar Energy", bg=button_color, fg="white", command=calculate_solar).pack(pady=10)

# Wind Energy Frame
wind_frame = tk.Frame(renewable_tab, bg=frame_color)
wind_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

tk.Label(wind_frame, text="Wind Energy Prediction", font=font_large, bg=frame_color).pack(pady=10)
tk.Label(wind_frame, text="Wind Speed (m/s):", bg=frame_color).pack(anchor="w")
wind_speed_entry = tk.Entry(wind_frame)
wind_speed_entry.pack(pady=5)

def calculate_wind():
    speed = float(wind_speed_entry.get())
    diameter = 100  # Assume fixed rotor diameter
    energy = predict_wind_energy(speed, diameter)
    tk.Label(wind_frame, text=f"Predicted Wind Energy: {energy:.2f} kWh", bg=frame_color).pack(pady=10)

tk.Button(wind_frame, text="Predict Wind Energy", bg=button_color, fg="white", command=calculate_wind).pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
