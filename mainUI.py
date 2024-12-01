# mainUI.py
import tkinter as tk
from tkinter import ttk, font, filedialog
from tkcalendar import DateEntry
from backend import (
    load_dataset, train_model, predict_solar_energy, predict_wind_energy,
    recommend_energy_source, get_climate_data
)

# Load data and model
df = load_dataset()
model = train_model(df)

# Create main window
root = tk.Tk()
root.title("Renewable Energy Prediction")
root.geometry("1200x800")

font_large = font.Font(size=14)
font_small = font.Font(size=12)
bg_color = "#F5F5F5"
frame_color = "#F9F9F9"
button_color = "#004d40"

root.configure(bg=bg_color)

# Left frame for solar energy
left_frame = tk.Frame(root, bg=frame_color)
left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

tk.Label(left_frame, text="Solar Energy Prediction", font=font_large, bg=frame_color).pack(pady=10)
tk.Label(left_frame, text="Rooftop Area (m²):", bg=frame_color).pack(anchor="w")
rooftop_area_entry = tk.Entry(left_frame)
rooftop_area_entry.pack(pady=5)

tk.Label(left_frame, text="Orientation:", bg=frame_color).pack(anchor="w")
orientation_combo = ttk.Combobox(left_frame, values=["South", "East", "West", "North", "Flat"])
orientation_combo.set("South")
orientation_combo.pack(pady=5)

solar_result_label = tk.Label(left_frame, text="", bg=frame_color)
solar_result_label.pack(pady=20)

def calculate_solar():
    area = float(rooftop_area_entry.get())
    orientation = orientation_combo.get()
    climate_data = {"solar_irradiance": 5.5}  # Replace with API call
    energy = predict_solar_energy(area, orientation, climate_data)
    solar_result_label.config(text=f"Predicted Solar Energy: {energy:.2f} kWh")

tk.Button(left_frame, text="Predict Solar Energy", bg=button_color, fg="white", command=calculate_solar).pack(pady=10)

# Right frame for wind energy
right_frame = tk.Frame(root, bg=frame_color)
right_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

tk.Label(right_frame, text="Wind Energy Prediction", font=font_large, bg=frame_color).pack(pady=10)
tk.Label(right_frame, text="Wind Speed (m/s):", bg=frame_color).pack(anchor="w")
wind_speed_entry = tk.Entry(right_frame)
wind_speed_entry.pack(pady=5)

tk.Label(right_frame, text="Rotor Diameter (m):", bg=frame_color).pack(anchor="w")
rotor_diameter_entry = tk.Entry(right_frame)
rotor_diameter_entry.pack(pady=5)

wind_result_label = tk.Label(right_frame, text="", bg=frame_color)
wind_result_label.pack(pady=20)

def calculate_wind():
    speed = float(wind_speed_entry.get())
    diameter = float(rotor_diameter_entry.get())
    energy = predict_wind_energy(speed, diameter)
    wind_result_label.config(text=f"Predicted Wind Energy: {energy:.2f} kWh")

tk.Button(right_frame, text="Predict Wind Energy", bg=button_color, fg="white", command=calculate_wind).pack(pady=10)

# Recommendation
def recommend():
    solar_energy = float(solar_result_label.cget("text").split(": ")[1].split()[0])
    wind_energy = float(wind_result_label.cget("text").split(": ")[1].split()[0])
    recommendation = recommend_energy_source(solar_energy, wind_energy)
    tk.Label(root, text=f"Recommended Source: {recommendation}", font=font_large, bg=bg_color).pack(pady=10)

tk.Button(root, text="Recommend Energy Source", bg=button_color, fg="white", command=recommend).pack(pady=20)

root.mainloop()
