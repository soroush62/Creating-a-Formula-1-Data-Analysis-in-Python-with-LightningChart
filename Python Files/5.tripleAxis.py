import lightningchart as lc
import fastf1
import pandas as pd

with open('D:/Computer Aplication/WorkPlacement/Projects/shared_variable.txt', 'r') as f:
    mylicensekey = f.read().strip()
lc.set_license(mylicensekey)

fastf1.Cache.enable_cache('Dataset/cache')

session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()

# Select the driver (e.g., Max Verstappen, 'VER') and the fastest lap
laps = session.laps.pick_driver('VER')
fastest_lap = laps.pick_fastest()

# Extract telemetry data for the fastest lap
telemetry = fastest_lap.get_telemetry()

telemetry['Timestamp_ms'] = (telemetry['Date'] - telemetry['Date'].min()).dt.total_seconds() * 1000  # Time in milliseconds from session start

timestamps = telemetry['Timestamp_ms']
rpm = telemetry['RPM']
speed = telemetry['Speed']
throttle = telemetry['Throttle']

time_origin = telemetry['Timestamp_ms'].min()

chart = lc.ChartXY(
    theme=lc.Themes.Light,
    title="RPM, Speed, and Throttle Over Time (Best Lap - Max Verstappen)"
)

x_axis = chart.get_default_x_axis()
x_axis.set_title("Time")
x_axis.set_tick_strategy("Time", time_origin=time_origin)

y_axis_rpm = chart.get_default_y_axis()
y_axis_rpm.set_title("Engine RPM")
rpm_series = chart.add_line_series(x_axis=x_axis, y_axis=y_axis_rpm)
rpm_series.set_name("Engine RPM")
rpm_series.set_line_color(lc.Color(51, 255, 51))
rpm_series.add(x=timestamps, y=rpm)

y_axis_speed = chart.add_y_axis(stack_index=1)
y_axis_speed.set_title("Speed (km/h)")
speed_series = chart.add_line_series(x_axis=x_axis, y_axis=y_axis_speed)
speed_series.set_name("Speed")
speed_series.set_line_color(lc.Color('blue'))
speed_series.add(x=timestamps, y=speed)

y_axis_throttle = chart.add_y_axis(stack_index=2)
y_axis_throttle.set_title("Throttle (%)")
throttle_series = chart.add_line_series(x_axis=x_axis, y_axis=y_axis_throttle)
throttle_series.set_name("Throttle")
throttle_series.set_line_color(lc.Color(255, 0, 0))
throttle_series.add(x=timestamps, y=throttle)

legend = chart.add_legend()
legend.add(rpm_series).add(speed_series).add(throttle_series)

chart.open()
