#geomag_transformations/field.py
import numpy as np
from . import parameters, coordinates

def cartesian_to_spherical(x, y, z):
    """Converts Cartesian coordinates to spherical coordinates (radius, theta, phi)."""
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(z / r) # Co-latitude
    phi = np.arctan2(y, x)   # Longitude / Azimuth
    return r, theta, phi

def calculate_geomagnetic_field(lat_deg, lon_deg):
    """
    Calculates geomagnetic field components, dip, and declination.
    Ref: Section 6 of the paper.
    """
    # --- 1. Get IGRF-1990 Parameters ---
    g1_0, g1_1, h1_1 = parameters.G1_0, parameters.G1_1, parameters.H1_1
    g2_0, g2_1, h2_1 = parameters.G2_0, parameters.G2_1, parameters.H2_1
    g2_2, h2_2 = parameters.G2_2, parameters.H2_2
    r0 = parameters.R0

    B0, theta_n_rad, lambda_n_rad = parameters.calculate_cd_parameters(g1_0, g1_1, h1_1)
    rot_matrix = parameters.calculate_rotation_matrix(theta_n_rad, lambda_n_rad)
    ed_params_geo = parameters.calculate_ed_parameters(g1_0, g1_1, h1_1, g2_0, g2_1, h2_1, g2_2, h2_2, B0)

    # --- 2. Get Point's Coordinates in All Frames ---
    # Convert geographic point to geographic cartesian
    lat_rad, lon_rad = np.radians(lat_deg), np.radians(lon_deg)
    geo_theta_rad = np.pi / 2 - lat_rad # Geographic co-latitude
    x = r0 * np.sin(geo_theta_rad) * np.cos(lon_rad)
    y = r0 * np.sin(geo_theta_rad) * np.sin(lon_rad)
    z = r0 * np.cos(geo_theta_rad)
    geo_point = np.array([x, y, z])

    # Transform to ED Cartesian coords to find the point's ED spherical coords
    ed_point_cartesian = coordinates.geographic_to_ed(geo_point, rot_matrix, r0, ed_params_geo)
    R, ED_theta_rad, ED_phi_rad = cartesian_to_spherical(*ed_point_cartesian)

    # --- 3. Calculate Field in ED Spherical Coordinates (Eq. 43) ---
    B_R = -2 * B0 * (r0 / R)**3 * np.cos(ED_theta_rad)
    B_Theta = -B0 * (r0 / R)**3 * np.sin(ED_theta_rad)
    B_Phi = 0
    B_ED_spherical = np.array([B_R, B_Theta, B_Phi])

    # --- 4. Transform Field to Geographic Spherical Components ---
    # Step 4a: ED Spherical -> ED Cartesian (Eq. 44)
    sin_T, cos_T = np.sin(ED_theta_rad), np.cos(ED_theta_rad)
    sin_P, cos_P = np.sin(ED_phi_rad), np.cos(ED_phi_rad)
    trans_matrix_44 = np.array([
        [sin_T * cos_P, cos_T * cos_P, -sin_P],
        [sin_T * sin_P, cos_T * sin_P, cos_P],
        [cos_T, -sin_T, 0]
    ])
    B_ED_cartesian = trans_matrix_44 @ B_ED_spherical

    # Step 4b: ED Cartesian -> Geographic Cartesian (Eq. 46)
    # This uses the inverse (transpose) of the main rotation matrix
    B_geo_cartesian = rot_matrix.T @ B_ED_cartesian

    # Step 4c: Geographic Cartesian -> Geographic Spherical (Eq. 47)
    sin_t, cos_t = np.sin(geo_theta_rad), np.cos(geo_theta_rad)
    sin_l, cos_l = np.sin(lon_rad), np.cos(lon_rad)
    trans_matrix_47 = np.array([
        [sin_t * cos_l, sin_t * sin_l, cos_t],
        [cos_t * cos_l, cos_t * sin_l, -sin_t],
        [-sin_l, cos_l, 0]
    ])
    B_r, B_theta, B_lambda = trans_matrix_47 @ B_geo_cartesian
    
    # --- 5. Calculate Dip and Declination ---
    # Dip Angle (I) from Eq. (50)
    horizontal_field = np.sqrt(B_theta**2 + B_lambda**2)
    dip_rad = np.arctan2(-B_r, horizontal_field)

    # Declination (D) from Eq. (51)
    declination_rad = np.arctan2(B_lambda, B_theta) # Note: Paper has -Bl/Bt, but atan2(y,x) convention is atan(y/x)

    return {
        "Br (nT)": B_r,
        "B_theta (nT)": B_theta,
        "B_lambda (nT)": B_lambda,
        "Dip Angle (°)": np.degrees(dip_rad),
        "Declination Angle (°)": np.degrees(declination_rad)
    }