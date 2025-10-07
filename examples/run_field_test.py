#examples/run_field_test.py

from geomag_transformations import field

# Location: Bengaluru, India
bengaluru_lat = 12.9716
bengaluru_lon = 77.5946

print(f"Calculating geomagnetic field for Bengaluru (Lat: {bengaluru_lat}, Lon: {bengaluru_lon})")
print("-" * 65)

field_data = field.calculate_geomagnetic_field(bengaluru_lat, bengaluru_lon)

for name, value in field_data.items():
    print(f"🔹 {name:<25}: {value:.2f}")