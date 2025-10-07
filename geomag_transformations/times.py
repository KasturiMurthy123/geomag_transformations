# geomag_transformations/times.py

#This module handles all the time-related calculations.


import numpy as np
import ephem
import datetime
from . import parameters, coordinates

def get_sun_position_and_time(observer):
    """Calculates equation of time and sun's celestial coordinates using PyEphem."""
    sun = ephem.Sun(observer)
    observer.lon = '0'
    gst = observer.sidereal_time()
    gha = gst - sun.g_ra
    
    ut_datetime = observer.date.datetime()
    ut_hours = ut_datetime.hour + ut_datetime.minute/60 + ut_datetime.second/3600
    
    delta_t_hours = (np.degrees(gha)/15 + 12) - ut_hours
    if delta_t_hours > 12: delta_t_hours -= 24
    if delta_t_hours < -12: delta_t_hours += 24

    sun_declination_rad = sun.dec
    t_g_hours = ut_hours + delta_t_hours
    sun_geo_lon_rad = np.radians(180 - 15 * t_g_hours)
    return delta_t_hours, sun_declination_rad, sun_geo_lon_rad

def calculate_geomagnetic_times(lat_deg, lon_deg):
    """Main function to calculate geographic, CD, and ED local times."""
    observer = ephem.Observer()
    observer.lat = str(lat_deg)
    observer.lon = str(lon_deg)
    observer.date = datetime.datetime.now(datetime.timezone.utc)
    utc_time = observer.date.datetime()
    ut_hours = utc_time.hour + utc_time.minute / 60.0 + utc_time.second / 3600.0
    
    g1_0, g1_1, h1_1 = -29775.0, -1851.0, 5411.0
    g2_0, g2_1, h2_1 = -2136.0, 3058.0, -2278.0
    g2_2, h2_2 = 1693.0, -380.0
    
    B0, theta_n_rad, lambda_n_rad = parameters.calculate_cd_parameters(g1_0, g1_1, h1_1)
    rot_matrix = parameters.calculate_rotation_matrix(theta_n_rad, lambda_n_rad)
    ed_params_geo = parameters.calculate_ed_parameters(g1_0, g1_1, h1_1, g2_0, g2_1, h2_1, g2_2, h2_2, B0)
    
    delta_t_hours, sun_dec_rad, sun_lon_rad = get_sun_position_and_time(observer)
    t_hours = ut_hours + delta_t_hours + (lon_deg / 15.0)
    
    lat_rad, lon_rad = np.radians(lat_deg), np.radians(lon_deg)
    theta = np.pi / 2 - lat_rad
    x = np.sin(theta) * np.cos(lon_rad)
    y = np.sin(theta) * np.sin(lon_rad)
    z = np.cos(theta)
    cd_coords_p = coordinates.geographic_to_cd(np.array([x, y, z]), rot_matrix)
    lambda_prime_rad = np.arctan2(cd_coords_p[1], cd_coords_p[0])

    x_sun = np.cos(sun_dec_rad) * np.cos(sun_lon_rad)
    y_sun = np.cos(sun_dec_rad) * np.sin(sun_lon_rad)
    z_sun = np.sin(sun_dec_rad)
    cd_coords_sun = coordinates.geographic_to_cd(np.array([x_sun, y_sun, z_sun]), rot_matrix)
    lambda_prime_o_rad = np.arctan2(cd_coords_sun[1], cd_coords_sun[0])
    
    term_cd = (np.degrees(lambda_prime_rad - lon_rad) - np.degrees(lambda_prime_o_rad - sun_lon_rad))
    t_prime_hours = t_hours + term_cd / 15.0

    ed_params_cd = rot_matrix @ ed_params_geo
    ed_coords_p = cd_coords_p - ed_params_cd
    phi_rad = np.arctan2(ed_coords_p[1], ed_coords_p[0])
    ed_coords_sun = cd_coords_sun - ed_params_cd
    phi_o_rad = np.arctan2(ed_coords_sun[1], ed_coords_sun[0])
    
    term_ed = (np.degrees(phi_rad - lon_rad) - np.degrees(phi_o_rad - sun_lon_rad))
    T_hours = t_hours + term_ed / 15.0

    def format_time(h):
        h %= 24
        hours = int(h)
        minutes = int((h * 60) % 60)
        seconds = int((h * 3600) % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return {
        "UTC Time": utc_time.strftime('%H:%M:%S'),
        "Geographic Apparent Time": format_time(t_hours),
        "Centered Dipole Time": format_time(t_prime_hours),
        "Eccentric Dipole Time": format_time(T_hours)
    }