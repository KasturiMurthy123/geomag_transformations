# examples/run_coordinate_test.py
from geomag_transformations import coordinates
import numpy as np

import numpy as np
from geomag_transformations import parameters, coordinates

def main():
    """
    Runs a full, step-by-step test of the coordinate transformation functions.
    """
    
    # --- 1. Use the centralized constants from the parameters module ---
    # The IGRF coefficients and radius are now imported, not redefined here.
    g1_0, g1_1, h1_1 = parameters.G1_0, parameters.G1_1, parameters.H1_1
    g2_0, g2_1, h2_1 = parameters.G2_0, parameters.G2_1, parameters.H2_1
    g2_2, h2_2 = parameters.G2_2, parameters.H2_2
    r0 = parameters.R0
    
    # --- 2. Calculate Intermediate Parameters ---
    B0, theta_n_rad, lambda_n_rad = parameters.calculate_cd_parameters(g1_0, g1_1, h1_1)
    rot_matrix = parameters.calculate_rotation_matrix(theta_n_rad, lambda_n_rad)
    ed_params_geo = parameters.calculate_ed_parameters(g1_0, g1_1, h1_1, g2_0, g2_1, h2_1, g2_2, h2_2, B0)

    print("--- Calculated Parameters for IGRF-1990 ---")
    print(f"Reference Field (B0): {B0:.2f} nT")
    print(f"CD North Pole Co-latitude: {np.degrees(theta_n_rad):.2f}°")
    print(f"CD North Pole Longitude: {np.degrees(lambda_n_rad):.2f}°")
    print("\nRotation Matrix (Geographic to CD):")
    print(rot_matrix)
    print(f"\nED Geographic Parameters [eta, zeta, xi]: {ed_params_geo}")
    print("-" * 45 + "\n")

    # --- 3. Define a Sample Point and Convert to Cartesian ---
    # A point on the Earth's surface at 12°N latitude, 88°E longitude
    lat_deg, lon_deg = 12.0, 88.0
    lat_rad, lon_rad = np.radians(lat_deg), np.radians(lon_deg)
    
    # Note: Co-latitude (theta) = 90 - latitude
    theta = np.pi / 2 - lat_rad
    x = r0 * np.sin(theta) * np.cos(lon_rad)
    y = r0 * np.sin(theta) * np.sin(lon_rad)
    z = r0 * np.cos(theta)
    
    geo_point = np.array([x, y, z])
    print(f"--- Coordinate Transformations for Sample Point ---")
    print(f"Initial Geographic Point (lat={lat_deg}°, lon={lon_deg}°):")
    print(f"  (x, y, z) = {geo_point.round(2)}\n")

    # --- 4. Perform Forward Transformations ---
    # Geographic -> CD
    cd_point = coordinates.geographic_to_cd(geo_point, rot_matrix)
    print("Transformed to Centered Dipole (CD) Coordinates:")
    print(f"  (x', y', z') = {cd_point.round(2)}\n")

    # Geographic -> ED
    ed_point = coordinates.geographic_to_ed(geo_point, rot_matrix, r0, ed_params_geo)
    print("Transformed to Eccentric Dipole (ED) Coordinates:")
    print(f"  (X, Y, Z) = {ed_point.round(2)}\n")
    
    # --- 5. Perform Inverse Transformations for Verification ---
    # ED -> Geographic
    geo_point_restored = coordinates.ed_to_geographic(ed_point, rot_matrix, r0, ed_params_geo)
    print("Transformed back from ED to Geographic Coordinates:")
    print(f"  (x, y, z) = {geo_point_restored.round(2)}\n")
    
    # Check if the restored point matches the original
    is_close = np.allclose(geo_point, geo_point_restored)
    print(f"Verification: Restored geographic point matches original? -> {is_close}")
    print("-" * 65)

if __name__ == '__main__':
    main()