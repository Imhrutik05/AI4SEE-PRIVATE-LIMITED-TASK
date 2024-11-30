import wmi
import psutil
import pandas as pd
import datetime
import time
import random
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest

# Step 1: Settings
duration_minutes = 500  # Increase to generate more data (adjust for 1 GB)
sampling_rate_hz = 10  # Sampling rate (samples per second)
num_samples = duration_minutes * 60 * sampling_rate_hz  # Total number of samples

# Step 2: Start time
start_time = datetime.datetime.now()

# Step 3: Initialize WMI client
w = wmi.WMI(namespace="root\\OpenHardwareMonitor")

# Step 4: Initialize lists to store data
timestamps = []
cpu_temperatures = []
cpu_usages = []
cpu_loads = []
memory_usages = []
battery_levels = []
cpu_powers = []

# Step 5: Collect data
for i in range(num_samples):
    try:
        # Get current time
        current_time = datetime.datetime.now()
        timestamps.append(current_time)

        # Get CPU temperature
        sensor_info = w.Sensor()
        cpu_temp = None
        cpu_power = None
        for sensor in sensor_info:
            if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                cpu_temp = sensor.Value
            if sensor.SensorType == 'Power' and 'CPU Package' in sensor.Name:
                cpu_power = sensor.Value
        cpu_temperatures.append(cpu_temp)
        cpu_powers.append(cpu_power)

        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1 / sampling_rate_hz)
        cpu_usages.append(cpu_usage)

        # Get CPU load (1 minute average)
        cpu_load = psutil.getloadavg()[0]
        cpu_loads.append(cpu_load)

        # Get memory usage
        memory_usage = psutil.virtual_memory().percent
        memory_usages.append(memory_usage)

        # Get battery level
        battery = psutil.sensors_battery()
        battery_level = battery.percent if battery else None
        battery_levels.append(battery_level)

        # Introduce anomalies randomly (e.g., 10% chance)
        if random.random() < 0.1:  # 10% chance to introduce anomaly
            # Introduce high CPU usage
            cpu_usages[-1] = random.uniform(90, 100)
            if random.random() < 0.1:
                # Introduce high temperature
                cpu_temperatures[-1] = random.uniform(90, 105)
            if random.random() < 0.1:
                # Introduce high memory usage
                memory_usages[-1] = random.uniform(95, 100)
            if random.random() < 0.1:
                # Introduce low battery level
                battery_levels[-1] = random.uniform(0, 10)
            if random.random() < 0.1:
                # Introduce high CPU power
                cpu_powers[-1] = random.uniform(50, 100)

    except Exception as e:
        print(f"Error collecting data: {e}")
        cpu_temperatures.append(None)
        cpu_usages.append(None)
        cpu_loads.append(None)
        memory_usages.append(None)
        battery_levels.append(None)
        cpu_powers.append(None)

    # Step 6: Create DataFrame
    data = {
        'timestamp': timestamps,
        'cpu_temperature': cpu_temperatures,
        'cpu_usage': cpu_usages,
        'cpu_load': cpu_loads,
        'memory_usage': memory_usages,
        'battery_level': battery_levels,
        'cpu_power': cpu_powers
    }
    df_real = pd.DataFrame(data)

    # Step 7: Save to CSV (append mode)
    # Step 7: Save to CSV (append mode)
    df_real.to_csv(r'C:\Users\Hrutik M Chaudhari\OneDrive\Desktop\Internship task\hardware_monitor_data.csv', mode='a', index=False)

    # Step 8: Wait for the next sample
    time.sleep(1 / sampling_rate_hz)

# Step 9: Display the first few rows of the DataFrame
print(df_real.head())

# --- Anomaly Detection with Isolation Forest ---
# Step 10: Apply Isolation Forest for anomaly detection
model = IsolationForest(contamination=0.1)  # Adjust contamination rate for anomaly threshold
df_real['anomaly'] = model.fit_predict(df_real[['cpu_usage', 'cpu_temperature', 'memory_usage', 'battery_level']])

# Step 11: Plot detected anomalies
plt.figure(figsize=(10, 6))
sns.scatterplot(x=df_real['timestamp'], y=df_real['cpu_usage'], hue=df_real['anomaly'], palette='coolwarm')
plt.title('Anomaly Detection: CPU Usage')
plt.xlabel('Timestamp')
plt.ylabel('CPU Usage (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


