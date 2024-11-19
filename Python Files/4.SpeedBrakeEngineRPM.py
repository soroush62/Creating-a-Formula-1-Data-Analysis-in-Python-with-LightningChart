import lightningchart as lc
import fastf1
import pandas as pd

fastf1.Cache.enable_cache('Dataset/cache')

# Load Bahrain Grand Prix race session
session = fastf1.get_session(2023, 'Bahrain', 'R')  # Year, Event, and Session ('R' for race)
session.load()

# Select telemetry data for a driver (e.g., Max Verstappen, 'VER')
laps = session.laps.pick_driver('VER').iloc[:5]  # Limit to the first 5 laps
all_laps_data = []

# Collect telemetry data for the first 5 laps
for _, lap in laps.iterlaps(): 
    telemetry = lap.get_telemetry()
    telemetry['LapNumber'] = lap['LapNumber']
    all_laps_data.append(telemetry)

df = pd.concat(all_laps_data, ignore_index=True)

df.rename(columns={'Speed': 'speed', 'RPM': 'current_engine_rpm', 'Brake': 'brake', 'LapNumber': 'lap_number'}, inplace=True)

with open('D:/Computer Aplication/WorkPlacement/Projects/shared_variable.txt', 'r') as f:
    mylicensekey = f.read().strip()
lc.set_license(mylicensekey)

lap_colors = {
    1: lc.Color('red'),
    2: lc.Color('orange'),
    3: lc.Color('green'),
    4: lc.Color('blue'),
    5: lc.Color(255, 102, 102)
}

# --- Chart 1: Speed vs. Engine RPM ---
chart1 = lc.ChartXY(theme=lc.Themes.Light)
chart1.set_title('Bahrain 2023: Speed vs. Engine RPM (Per Lap)')
chart1.get_default_x_axis().set_title('Speed (km/h)')
chart1.get_default_y_axis().set_title('Engine RPM')
chart1_legend = chart1.add_legend()

for lap in df['lap_number'].unique():
    lap_data = df[df['lap_number'] == lap]
    scatter_series = chart1.add_point_series()
    scatter_series.add(lap_data['speed'].tolist(), lap_data['current_engine_rpm'].tolist())
    scatter_series.set_point_shape('circle').set_point_size(5)
    scatter_series.set_point_color(color=lap_colors.get(lap, lc.Color('grey')))
    scatter_series.set_name(f'Lap {lap}')
    chart1_legend.add(scatter_series)

chart1.open()
