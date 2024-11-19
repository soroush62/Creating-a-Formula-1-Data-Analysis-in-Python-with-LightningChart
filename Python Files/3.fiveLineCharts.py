import lightningchart as lc
import fastf1
import pandas as pd

lc.set_license('my-license-key')

fastf1.Cache.enable_cache('Dataset/cache')

session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()

# Select the driver (e.g., Max Verstappen, 'VER')
laps = session.laps.pick_driver('VER')

# Filter the first 5 laps
first_5_laps = laps.iloc[:5]

telemetry_data = []
for _, lap in first_5_laps.iterrows():
    telemetry = lap.get_telemetry()  
    telemetry['LapNumber'] = lap['LapNumber']
    telemetry_data.append(telemetry)

df = pd.concat(telemetry_data, ignore_index=True)

df['Timestamp_ms'] = (df['Date'] - df['Date'].min()).dt.total_seconds() * 1000 

# Columns to visualize
columns_to_visualize = [
    'Speed',        # Speed (km/h)
    'RPM',          # Engine RPM
    'Brake',        # Brake intensity (binary: 0 or 1)
    'nGear',        # Gear
    'Throttle'      # Acceleration/Throttle (0-100%)
]

lap_colors = {
    1: lc.Color('red'),
    2: lc.Color('orange'),
    3: lc.Color('green'),
    4: lc.Color('blue'),
    5: lc.Color(255, 102, 102)
}

chart = lc.ChartXY(
    theme=lc.Themes.Light,
    title='Top 5 Data Columns for First 5 Laps (Bahrain 2023)'
)
chart.get_default_y_axis().dispose() 

legend = chart.add_legend()
laps_in_legend = set()

for i, column in enumerate(columns_to_visualize):
    axis_y = chart.add_y_axis(stack_index=i)
    axis_y.set_margins(15 if i > 0 else 0, 15 if i < 4 else 0)
    axis_y.set_title(title=column.replace('_', ' ').title())
    
    for lap_number in df['LapNumber'].unique():
        lap_data = df[df['LapNumber'] == lap_number]
        series = chart.add_line_series(y_axis=axis_y, data_pattern='ProgressiveX')
        
        series.add(
            lap_data['Timestamp_ms'].tolist(), 
            lap_data[column].tolist()
        )
        
        series.set_name(f'{column.title()} (Lap {lap_number})')
        color = lap_colors.get(lap_number, lc.Color('grey'))
        series.set_line_color(color=color)
        series.set_line_thickness(2)
        
        if lap_number not in laps_in_legend:
            legend.add(series)
            laps_in_legend.add(lap_number)

x_axis = chart.get_default_x_axis().set_tick_strategy('Time')
x_axis.set_title('Time (ms)')
x_axis.set_interval(0, df['Timestamp_ms'].max())  

chart.open()
