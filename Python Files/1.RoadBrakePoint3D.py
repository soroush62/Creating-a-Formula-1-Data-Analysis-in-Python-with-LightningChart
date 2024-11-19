import fastf1
import lightningchart as lc
import numpy as np
from scipy.interpolate import interp1d

lc.set_license('my-license-key')

fastf1.Cache.enable_cache('Dataset/cache')

session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()

laps = session.laps.pick_driver('VER')
fastest_lap = laps.pick_fastest()

# Extract telemetry data
telemetry = fastest_lap.get_telemetry()

# Extract telemetry data directly
x_coords = telemetry['X'].astype(float).values
y_coords = telemetry['Y'].astype(float).values
z_coords = telemetry['Z'].astype(float).values
speed = telemetry['Speed'].astype(float).values
brake = telemetry['Brake'].astype(float).values 

def interpolate_track(x, y, z, speed, num_points=5000):
   
    distances = np.cumsum(np.sqrt(np.diff(x)**2 + np.diff(y)**2 + np.diff(z)**2))
    distances = np.insert(distances, 0, 0)

    interp_func_x = interp1d(distances, x, kind='linear')
    interp_func_y = interp1d(distances, y, kind='linear')
    interp_func_z = interp1d(distances, z, kind='linear')
    interp_func_speed = interp1d(distances, speed, kind='linear')

    new_distances = np.linspace(0, distances[-1], num_points)

    new_x = interp_func_x(new_distances)
    new_y = interp_func_y(new_distances)
    new_z = interp_func_z(new_distances)
    new_speed = interp_func_speed(new_distances)

    return new_x, new_y, new_z, new_speed

interpolated_x, interpolated_y, interpolated_z, interpolated_speed = interpolate_track(
    x_coords, y_coords, z_coords, speed
)

braking_areas = telemetry[telemetry['Brake'] > 0]
braking_x = braking_areas['X'].astype(float).values
braking_y = braking_areas['Y'].astype(float).values
braking_z = braking_areas['Z'].astype(float).values

chart = lc.Chart3D(theme=lc.Themes.Dark)

chart.set_title("Bahrain 2023: 3D Track and Braking Areas")
chart.get_default_x_axis().set_title("X Coordinate")
chart.get_default_y_axis().set_title("Y Coordinate")
chart.get_default_z_axis().set_title("Z Coordinate")
chart.set_bounding_box(20, 7, 1)
data = []
for i in range(len(interpolated_x)):
    data.append({
        "x": interpolated_x[i],
        "y": interpolated_y[i],
        "z": interpolated_z[i],
        "value": interpolated_speed[i]
    })

track_series = chart.add_point_series(individual_lookup_values_enabled=True)
track_series.add_dict_data(data)

color_steps = [
    {'value': min(speed), 'color': lc.Color(0, 0, 255)},   # Blue
    {'value': (min(speed) + max(speed)) / 2, 'color': lc.Color(0, 255, 0)},  # Green
    {'value': max(speed), 'color': lc.Color(255, 0, 0)}   # Red
]
track_series.set_palette_point_colors(
    steps=color_steps,
    look_up_property='value',
    interpolate=True
)

braking_series = chart.add_point_series()
braking_series.add(braking_x, braking_y, braking_z)
braking_series.set_point_color(lc.Color('blue'))
braking_series.set_point_size(15)

legend = chart.add_legend(data=track_series)
legend.set_title("Speed")

chart.open()
