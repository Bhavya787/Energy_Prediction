# backend.py
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score
import pulp
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
from cryptography.fernet import Fernet

# Encryption for sensitive data
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_data(data):
    return cipher.encrypt(data.encode())

def decrypt_data(encrypted_data):
    return cipher.decrypt(encrypted_data).decode()

# Load dataset
def load_dataset():
    df = pd.read_csv('datasets/daily_dataset.csv')
    df['day'] = pd.to_datetime(df['day'], format='%d-%m-%Y')
    df['day_of_week'] = df['day'].dt.dayofweek
    df['month'] = df['day'].dt.month
    df['day_of_month'] = df['day'].dt.day
    df['year'] = df['day'].dt.year
    df['LCLid'] = df['LCLid'].astype('category').cat.codes
    df.dropna(inplace=True)
    return df

# Train model
def train_model(df):
    X = df[['LCLid', 'day_of_week', 'month', 'day_of_month', 'year']]
    y = df['energy_median']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=150, learning_rate=0.2)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print(f'RMSE: {np.sqrt(mean_squared_error(y_test, y_pred))}')
    return model

# Solar energy prediction
def predict_solar_energy(rooftop_area, orientation, climate_data):
    solar_irradiance = climate_data.get('solar_irradiance', 5.5)  # Default placeholder
    efficiency = 0.15
    factor = {'south': 1.0, 'east': 0.75, 'west': 0.75, 'north': 0.5, 'flat': 0.8}.get(orientation.lower(), 0.8)
    return rooftop_area * solar_irradiance * efficiency * factor

# Wind energy prediction
def predict_wind_energy(wind_speed, rotor_diameter):
    rotor_area = np.pi * (rotor_diameter / 2) ** 2
    air_density = 1.225
    efficiency = 0.4
    return 0.5 * air_density * rotor_area * (wind_speed ** 3) * efficiency / 1000  # kWh

# Recommendation
def recommend_energy_source(solar_energy, wind_energy):
    if solar_energy > wind_energy:
        return "Solar"
    elif wind_energy > solar_energy:
        return "Wind"
    return "Both are equally viable."

# Get climate data (API Integration)
def get_climate_data(location):
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid=786a86a194de913c2af825ae5145edeb"
    response = requests.get(api_url)
    data = response.json()
    return {
        "solar_irradiance": data['main'].get('solar_irradiance', 5.5),  # Placeholder
        "wind_speed": data['wind']['speed']
    }
