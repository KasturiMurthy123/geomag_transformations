# examples/run_time_test.py
from geomag_transformations import times

# Location: Bengaluru, India
bengaluru_lat = 12.9716
bengaluru_lon = 77.5946

print(f"Calculating geomagnetic times for Bengaluru (Lat: {bengaluru_lat}, Lon: {bengaluru_lon})")
print("-" * 60)
    
geo_times = times.calculate_geomagnetic_times(bengaluru_lat, bengaluru_lon)
    
for name, time_str in geo_times.items():
    print(f"🕒 {name:<25}: {time_str}")