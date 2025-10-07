# geomag_transformations/coordinates.py
#This module contains all the coordinate transformation functions.

import numpy as np
from . import parameters

def geographic_to_cd(geo_coords, rotation_matrix):
    """Transforms geographic cartesian coords to CD coords."""
    return rotation_matrix @ geo_coords

def cd_to_geographic(cd_coords, rotation_matrix):
    """Transforms CD cartesian coords to geographic coords."""
    return rotation_matrix.T @ cd_coords

def geographic_to_ed(geo_coords, rotation_matrix, r0, ed_params_geo):
    """Transforms geographic cartesian coords to ED coords."""
    offset_geo_coords = geo_coords - r0 * ed_params_geo
    return rotation_matrix @ offset_geo_coords

def ed_to_geographic(ed_coords, rotation_matrix, r0, ed_params_geo):
    """Transforms ED cartesian coords to geographic coords."""
    offset_geo_coords = rotation_matrix.T @ ed_coords
    return offset_geo_coords + r0 * ed_params_geo

def transform_geographic_point(lat_deg, lon_deg):
    """
    A helper function to run a full transformation for a given lat/lon point.
    """
    g1_0, g1_1, h1_1 = -29775.0, -1851.0, 5411.0
    g2_0, g2_1, h2_1 = -2136.0, 3058.0, -2278.0
    g2_2, h2_2 = 1693.0, -380.0
    r0 = 6371.2

    B0, theta_n_rad, lambda_n_rad = parameters.calculate_cd_parameters(g1_0, g1_1, h1_1)
    rot_matrix = parameters.calculate_rotation_matrix(theta_n_rad, lambda_n_rad)
    ed_params_geo = parameters.calculate_ed_parameters(g1_0, g1_1, h1_1, g2_0, g2_1, h2_1, g2_2, h2_2, B0)

    lat_rad, lon_rad = np.radians(lat_deg), np.radians(lon_deg)
    theta = np.pi / 2 - lat_rad
    x = r0 * np.sin(theta) * np.cos(lon_rad)
    y = r0 * np.sin(theta) * np.sin(lon_rad)
    z = r0 * np.cos(theta)
    geo_point = np.array([x, y, z])

    cd_point = geographic_to_cd(geo_point, rot_matrix)
    ed_point = geographic_to_ed(geo_point, rot_matrix, r0, ed_params_geo)
    
    return {
        "geo_coords": geo_point,
        "cd_coords": cd_point,
        "ed_coords": ed_point
    }