import fastf1
import pandas as pd
import lightningchart as lc
import numpy as np
import math
import asyncio

lc.set_license('my-license-key')

fastf1.Cache.enable_cache('Dataset/cache')

# Load Bahrain Grand Prix race session
session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()

# Select telemetry for the main driver (e.g., Max Verstappen, 'VER')
ver_laps = session.laps.pick_driver('VER').iloc[:5]
ver_telemetry = ver_laps.get_telemetry()

ver_telemetry['X'] = pd.to_numeric(ver_telemetry['X'], errors='coerce')
ver_telemetry['Y'] = pd.to_numeric(ver_telemetry['Y'], errors='coerce')
ver_telemetry['Z'] = pd.to_numeric(ver_telemetry['Z'], errors='coerce')
ver_telemetry.dropna(subset=['X', 'Y', 'Z'], inplace=True)

ver_speed = ver_telemetry['Speed'].astype(float).tolist()
ver_rpm = ver_telemetry['RPM'].astype(float).tolist()
ver_gear = ver_telemetry['nGear'].astype(int).tolist()
ver_x = ver_telemetry['X'].tolist()
ver_y = ver_telemetry['Y'].tolist()
ver_z = ver_telemetry['Z'].tolist()
ver_time = ver_telemetry['Time'].dt.total_seconds().tolist()

driver_telemetry = {}
for driver in session.laps['DriverNumber'].unique():
    if driver != 'VER':
        laps = session.laps.pick_driver(driver)
        telemetry = laps.get_telemetry()
        telemetry['X'] = pd.to_numeric(telemetry['X'], errors='coerce')
        telemetry['Y'] = pd.to_numeric(telemetry['Y'], errors='coerce')
        telemetry['Z'] = pd.to_numeric(telemetry['Z'], errors='coerce')
        telemetry.dropna(subset=['X', 'Y', 'Z'], inplace=True)
        driver_telemetry[driver] = {
            'X': telemetry['X'].tolist(),
            'Y': telemetry['Y'].tolist(),
            'Z': telemetry['Z'].tolist(),
            'Time': telemetry['Time'].dt.total_seconds().tolist(),
        }



dashboard = lc.Dashboard(rows=2, columns=3, theme=lc.Themes.Dark)

# RPM gauge
rpm_chart = dashboard.GaugeChart(row_index=0, column_index=0)
rpm_chart.set_interval(0, 12000)
rpm_chart.set_angle_interval(start=225, end=-45)
rpm_chart.set_value_indicators([
    {'start': 0, 'end': 4000, 'color': lc.Color('green')},
    {'start': 4000, 'end': 8000, 'color': lc.Color('yellow')},
    {'start': 8000, 'end': 12000, 'color': lc.Color('red')}
])
rpm_chart.set_bar_thickness(30)
rpm_chart.set_value_indicator_thickness(15)
rpm_chart.set_title("Current Engine RPM").set_title_font(20, weight='bold')
rpm_chart.set_unit_label("(RPM)").set_unit_label_font(18, weight='bold')
rpm_chart.set_value_label_font(35)

# Speed gauge
speed_chart = dashboard.GaugeChart(row_index=0, column_index=2)
speed_chart.set_interval(0, 350)
speed_chart.set_angle_interval(start=225, end=-45)
speed_chart.set_value_indicators([
    {'start': 0, 'end': 100, 'color': lc.Color('green')},
    {'start': 100, 'end': 250, 'color': lc.Color('yellow')},
    {'start': 250, 'end': 350, 'color': lc.Color('red')}
])
speed_chart.set_bar_thickness(30)
speed_chart.set_value_indicator_thickness(15)
speed_chart.set_title("Speed (km/h)").set_value_label_font(30).set_title_font(20, weight='bold')

# Gear gauge
gear_gauge_chart = dashboard.GaugeChart(row_index=0, column_index=1)
gear_gauge_chart.set_interval(0, 8)
gear_gauge_chart.set_angle_interval(start=180, end=0)
gear_gauge_chart.set_title("Gear").set_value_decimals(0).set_title_font(20, weight='bold')
gear_gauge_chart.set_bar_color(lc.Color('#001F3F'))
gear_gauge_chart.set_needle_color(lc.Color('orange'))
gear_gauge_chart.set_bar_thickness(30)
gear_gauge_chart.set_value_indicator_thickness(15)

# 3D Chart for track visualization
track_chart = dashboard.Chart3D(row_index=1, column_index=0, column_span=3, title="3D Track with Moving Car and Driver Ahead/Behind")
track_chart.set_title_font(20, weight='bold')
track_chart.get_default_x_axis().set_title("X")
track_chart.get_default_y_axis().set_title("Y")
track_chart.get_default_z_axis().set_title("Z")
track_chart.set_bounding_box(20, 7, 1)

# Add line series for the track
track_series = track_chart.add_line_series()
track_series.add(ver_x, ver_y, ver_z)

# Add car model (red sphere for VER)
car_model = track_chart.add_mesh_model()
sphere_radius = 5
sphere_segments = 16
sphere_vertices, sphere_indices = [], []

# Generate vertices and indices for a sphere model
for i in range(sphere_segments + 1):
    lat = math.pi * (-0.5 + float(i) / sphere_segments)
    y_sphere = sphere_radius * math.sin(lat)
    zr = sphere_radius * math.cos(lat)

    for j in range(sphere_segments + 1):
        lng = 2 * math.pi * float(j) / sphere_segments
        x_sphere = zr * math.cos(lng)
        z_sphere = zr * math.sin(lng)
        sphere_vertices.extend([x_sphere, y_sphere, z_sphere])

for i in range(sphere_segments):
    for j in range(sphere_segments):
        first = i * (sphere_segments + 1) + j
        second = first + sphere_segments + 1
        sphere_indices.extend([first, second, first + 1, second, second + 1, first + 1])

car_model.set_model_geometry(vertices=sphere_vertices, indices=sphere_indices)
car_model.set_color(lc.Color('red')).set_scale(0.002)
car_model.set_model_location(ver_x[0], ver_y[0], ver_z[0])

# Add yellow sphere for the driver ahead/behind
driver_sphere = track_chart.add_mesh_model()
driver_sphere.set_model_geometry(vertices=sphere_vertices, indices=sphere_indices)
driver_sphere.set_color(lc.Color('yellow')).set_scale(0.002)

# Function to find the nearest driver's position
def get_nearest_driver_position(ver_x, ver_y, ver_z, ver_time, driver_telemetry):
    min_distance = float('inf')
    nearest_position = None

    for driver, data in driver_telemetry.items():
        if len(data['Time']) == 0: 
            continue
        driver_x = np.interp(ver_time, data['Time'], data['X'])
        driver_y = np.interp(ver_time, data['Time'], data['Y'])
        driver_z = np.interp(ver_time, data['Time'], data['Z'])
        distance = math.sqrt((ver_x - driver_x) ** 2 + (ver_y - driver_y) ** 2 + (ver_z - driver_z) ** 2)
        if distance < min_distance:
            min_distance = distance
            nearest_position = (driver_x, driver_y, driver_z)

    return nearest_position

async def update_dashboard():
    step_size = 5
    lap_changes = np.linspace(0, len(ver_x), len(ver_laps) + 1, dtype=int) 
    current_lap = 1

    for i in range(0, len(ver_x) - 1, step_size):
        rpm_chart.set_value(ver_rpm[i])
        speed_chart.set_value(ver_speed[i])
        gear_gauge_chart.set_value(ver_gear[i])

        car_model.set_model_location(ver_x[i], ver_y[i], ver_z[i])
        dx = ver_x[i + step_size] - ver_x[i]
        dz = ver_z[i + step_size] - ver_z[i]
        angle = math.degrees(math.atan2(dz, dx))
        car_model.set_model_rotation(0, angle, 0)

        nearest_position = get_nearest_driver_position(ver_x[i], ver_y[i], ver_z[i], ver_time[i], driver_telemetry)
        if nearest_position:
            driver_sphere.set_model_location(*nearest_position)

        if i >= lap_changes[current_lap]:
            current_lap += 1
            track_chart.set_title(f"3D Track with Moving Car - Lap {current_lap}")


        await asyncio.sleep(0.1)

dashboard.open(live=True)
asyncio.run(update_dashboard())

