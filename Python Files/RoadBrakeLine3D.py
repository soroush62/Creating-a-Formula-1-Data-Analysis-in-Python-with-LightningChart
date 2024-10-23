import pandas as pd
import lightningchart as lc

lc.set_license(open('../license-key').read())

file_path = 'Dataset/telemetry-rio-5-laps.csv'
df = pd.read_csv(file_path)

# Extract coordinates for the track
x_coords = df['position_x'].values
y_coords = df['position_y'].values
z_coords = df['position_z'].values

# Extract braking areas data
braking_areas = df[df['brake'] > 0]
braking_x = braking_areas['position_x'].values
braking_y = braking_areas['position_y'].values
braking_z = braking_areas['position_z'].values

chart = lc.Chart3D(
    theme=lc.Themes.Dark 
)

# Configure axes labels and limits
chart.set_title("3D Track and Braking Areas")
chart.get_default_x_axis().set_title("X Coordinate")
chart.get_default_y_axis().set_title("Y Coordinate")
chart.get_default_z_axis().set_title("Z Coordinate")

# Add the track line
track_series = chart.add_line_series().set_line_thickness(3)
track_series.add(x_coords, y_coords, z_coords)
track_series.set_line_color(lc.Color(32, 190, 255))  # Light blue

# Add the braking areas
braking_series = chart.add_point_series()
braking_series.add(braking_x, braking_y, braking_z)
braking_series.set_point_color(lc.Color('red')) 
braking_series.set_point_size(10)

chart.open()

