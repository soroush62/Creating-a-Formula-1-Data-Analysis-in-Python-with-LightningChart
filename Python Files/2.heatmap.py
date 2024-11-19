import pandas as pd
import numpy as np
import lightningchart as lc
import fastf1

lc.set_license('my-license-key')

fastf1.Cache.enable_cache('Dataset/cache')

session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()

# Select driver (e.g., Max Verstappen, 'VER') and fastest lap
laps = session.laps.pick_driver('VER')
fastest_lap = laps.pick_fastest()

# Extract telemetry data
telemetry = fastest_lap.get_telemetry()

# Preprocess telemetry data
df = telemetry[['X', 'Y', 'Speed', 'nGear']].dropna()
df.rename(columns={'X': 'position_x', 'Y': 'position_y', 'Speed': 'speed', 'nGear': 'gear'}, inplace=True)

# Bin position data
df['position_x_binned'] = pd.cut(df['position_x'], bins=100, labels=False)
df['position_y_binned'] = pd.cut(df['position_y'], bins=100, labels=False)

# Create heatmaps for speed and gear usage
heatmap_data_speed = df.pivot_table(
    values='speed',
    index='position_x_binned',
    columns='position_y_binned',
    aggfunc='mean'
).fillna(0).values.tolist()

heatmap_data_gear = df.pivot_table(
    values='gear',
    index='position_x_binned',
    columns='position_y_binned',
    aggfunc='mean'
).fillna(0).values.tolist()

with open('D:/Computer Aplication/WorkPlacement/Projects/shared_variable.txt', 'r') as f:
    mylicensekey = f.read().strip()

dashboard = lc.Dashboard(
    columns=1,
    rows=2,
    theme=lc.Themes.Light
)

speed_chart = dashboard.ChartXY(
    row_index=0,
    column_index=0,
    title='Bahrain 2023: Track Position vs. Speed Heatmap'
)
legend = speed_chart.add_legend()
speed_series = speed_chart.add_heatmap_grid_series(
    columns=len(heatmap_data_speed[0]),
    rows=len(heatmap_data_speed)
)
speed_series.hide_wireframe()
speed_series.set_intensity_interpolation(False)
speed_series.invalidate_intensity_values(heatmap_data_speed)

speed_series.set_palette_coloring(
    steps=[
        {'value': np.min(heatmap_data_speed), 'color': lc.Color('white')},
        {'value': np.percentile(heatmap_data_speed, 96), 'color': lc.Color(255, 255, 0)},
        {'value': np.max(heatmap_data_speed), 'color': lc.Color(255, 0, 0)}
    ],
    look_up_property='value',
    percentage_values=False
)
legend.add(speed_series).set_title('Average Speed (km/h)')
x_axis_speed = speed_chart.get_default_x_axis()
x_axis_speed.set_title('Position Y (Binned)')
x_axis_speed.set_interval(0, 100)

y_axis_speed = speed_chart.get_default_y_axis()
y_axis_speed.set_title('Position X (Binned)')
y_axis_speed.set_interval(0, 100)

# --- Heatmap 2: Track Position vs. Gear Usage ---
gear_chart = dashboard.ChartXY(
    row_index=1,
    column_index=0,
    title='Bahrain 2023: Track Position vs. Gear Usage Heatmap'
)
legend = gear_chart.add_legend()
gear_series = gear_chart.add_heatmap_grid_series(
    columns=len(heatmap_data_gear[0]),
    rows=len(heatmap_data_gear)
)
gear_series.hide_wireframe()
gear_series.set_intensity_interpolation(False)
gear_series.invalidate_intensity_values(heatmap_data_gear)

gear_series.set_palette_coloring(
    steps=[
        {'value': np.min(heatmap_data_gear), 'color': lc.Color('white')},
        {'value': np.percentile(heatmap_data_gear, 96), 'color': lc.Color(255, 255, 0)},
        {'value': np.max(heatmap_data_gear), 'color': lc.Color(255, 0, 0)}
    ],
    look_up_property='value',
    percentage_values=False
)
legend.add(gear_series).set_title('Average Gear Used')
x_axis_gear = gear_chart.get_default_x_axis()
x_axis_gear.set_title('Position Y (Binned)')
x_axis_gear.set_interval(0, 100)

y_axis_gear = gear_chart.get_default_y_axis()
y_axis_gear.set_title('Position X (Binned)')
y_axis_gear.set_interval(0, 100)

dashboard.open()
