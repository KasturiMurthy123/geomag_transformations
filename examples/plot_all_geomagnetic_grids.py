import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# Import the necessary modules from your installed package
from geomag_transformations import parameters, coordinates

def main():
    """
    Generates and displays a plot comparing Geographic, CD, and ED coordinate grids,
    including markers for all North and South poles.
    """
    # --- 1. Get IGRF-1990 Parameters from the Package ---
    r0 = parameters.R0
    B0, theta_n_rad, lambda_n_rad = parameters.calculate_cd_parameters(
        parameters.G1_0, parameters.G1_1, parameters.H1_1
    )
    rot_matrix = parameters.calculate_rotation_matrix(theta_n_rad, lambda_n_rad)
    ed_params_geo = parameters.calculate_ed_parameters(
        parameters.G1_0, parameters.G1_1, parameters.H1_1,
        parameters.G2_0, parameters.G2_1, parameters.H2_1,
        parameters.G2_2, parameters.H2_2, B0
    )

    # --- 2. Create the Plot ---
    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mollweide())
    ax.set_global()

    ax.coastlines(color='black', zorder=3)
    ax.gridlines(linestyle=':', color='gray', alpha=0.7)
    ax.set_title('Geographic vs. CD and ED Coordinate Grids with Poles', fontsize=18)

    # --- 3. Plot Latitude and Longitude Lines ---
    # Plot CD Latitude Lines
    for cd_lat in np.arange(-60, 90, 10):
        lats, lons = [], []
        for cd_lon in np.arange(-180, 181, 5):
            cd_lat_rad = np.radians(cd_lat); cd_lon_rad = np.radians(cd_lon)
            cd_cartesian_unit = np.array([np.cos(cd_lat_rad) * np.cos(cd_lon_rad), np.cos(cd_lat_rad) * np.sin(cd_lon_rad), np.sin(cd_lat_rad)])
            geo_cartesian = coordinates.cd_to_geographic(cd_cartesian_unit, rot_matrix)
            geo_lon = np.degrees(np.arctan2(geo_cartesian[1], geo_cartesian[0])); geo_lat = np.degrees(np.arcsin(geo_cartesian[2]))
            lats.append(geo_lat); lons.append(geo_lon)
        ax.plot(lons, lats, color='blue', linestyle='--', linewidth=1.0, transform=ccrs.Geodetic(), label='CD Latitude' if cd_lat == 0 else "")

    # Plot CD Longitude Lines
    for cd_lon in np.arange(-180, 180, 30):
        lats, lons = [], []
        for cd_lat in np.arange(-90, 91, 5):
            cd_lat_rad = np.radians(cd_lat); cd_lon_rad = np.radians(cd_lon)
            cd_cartesian_unit = np.array([np.cos(cd_lat_rad) * np.cos(cd_lon_rad), np.cos(cd_lat_rad) * np.sin(cd_lon_rad), np.sin(cd_lat_rad)])
            geo_cartesian = coordinates.cd_to_geographic(cd_cartesian_unit, rot_matrix)
            geo_lon = np.degrees(np.arctan2(geo_cartesian[1], geo_cartesian[0])); geo_lat = np.degrees(np.arcsin(geo_cartesian[2]))
            lats.append(geo_lat); lons.append(geo_lon)
        ax.plot(lons, lats, color='blue', linewidth=1.5, transform=ccrs.Geodetic(), label='CD Longitude' if cd_lon == 0 else "")

    # Plot ED Latitude Lines
    for ed_lat in np.arange(-60, 90, 10):
        lats, lons = [], []
        for ed_lon in np.arange(-180, 181, 5):
            ed_lat_rad = np.radians(ed_lat); ed_lon_rad = np.radians(ed_lon)
            ed_cartesian = np.array([r0 * np.cos(ed_lat_rad) * np.cos(ed_lon_rad), r0 * np.cos(ed_lat_rad) * np.sin(ed_lon_rad), r0 * np.sin(ed_lat_rad)])
            geo_cartesian = coordinates.ed_to_geographic(ed_cartesian, rot_matrix, r0, ed_params_geo)
            norm_geo_cartesian = geo_cartesian / np.linalg.norm(geo_cartesian)
            geo_lon = np.degrees(np.arctan2(norm_geo_cartesian[1], norm_geo_cartesian[0])); geo_lat = np.degrees(np.arcsin(norm_geo_cartesian[2]))
            lats.append(geo_lat); lons.append(geo_lon)
        ax.plot(lons, lats, color='green', linestyle='--', linewidth=1.0, transform=ccrs.Geodetic(), label='ED Latitude' if ed_lat == 0 else "")

    # Plot ED Longitude Lines
    for ed_lon in np.arange(-180, 180, 30):
        lats, lons = [], []
        for ed_lat in np.arange(-90, 91, 5):
            ed_lat_rad = np.radians(ed_lat); ed_lon_rad = np.radians(ed_lon)
            ed_cartesian = np.array([r0 * np.cos(ed_lat_rad) * np.cos(ed_lon_rad), r0 * np.cos(ed_lat_rad) * np.sin(ed_lon_rad), r0 * np.sin(ed_lat_rad)])
            geo_cartesian = coordinates.ed_to_geographic(ed_cartesian, rot_matrix, r0, ed_params_geo)
            norm_geo_cartesian = geo_cartesian / np.linalg.norm(geo_cartesian)
            geo_lon = np.degrees(np.arctan2(norm_geo_cartesian[1], norm_geo_cartesian[0])); geo_lat = np.degrees(np.arcsin(norm_geo_cartesian[2]))
            lats.append(geo_lat); lons.append(geo_lon)
        ax.plot(lons, lats, color='green', linewidth=1.5, transform=ccrs.Geodetic(), label='ED Longitude' if ed_lon == 0 else "")


    # --- 4. Plot All Pole Positions ---
    # Geographic Poles
    ax.plot(0, 90, 'rD', markersize=10, transform=ccrs.Geodetic(), label='Geographic Pole', zorder=5)
    ax.plot(0, -90, 'rD', markersize=10, transform=ccrs.Geodetic(), zorder=5)

    # Centered Dipole (CD) Poles
    # North Pole is at CD Cartesian [0, 0, 1]
    cd_np_cart = coordinates.cd_to_geographic(np.array([0,0,1]), rot_matrix)
    cd_np_lon = np.degrees(np.arctan2(cd_np_cart[1], cd_np_cart[0]))
    cd_np_lat = np.degrees(np.arcsin(cd_np_cart[2]))
    ax.plot(cd_np_lon, cd_np_lat, 'b^', markersize=12, transform=ccrs.Geodetic(), label='CD Pole', zorder=5)
    # South Pole is at CD Cartesian [0, 0, -1]
    cd_sp_cart = coordinates.cd_to_geographic(np.array([0,0,-1]), rot_matrix)
    cd_sp_lon = np.degrees(np.arctan2(cd_sp_cart[1], cd_sp_cart[0]))
    cd_sp_lat = np.degrees(np.arcsin(cd_sp_cart[2]))
    ax.plot(cd_sp_lon, cd_sp_lat, 'b^', markersize=12, transform=ccrs.Geodetic(), zorder=5)


    # Eccentric Dipole (ED) Poles
    # North Pole is at ED Cartesian [0, 0, r0]
    ed_np_cart = coordinates.ed_to_geographic(np.array([0,0,r0]), rot_matrix, r0, ed_params_geo)
    norm_ed_np_cart = ed_np_cart / np.linalg.norm(ed_np_cart)
    ed_np_lon = np.degrees(np.arctan2(norm_ed_np_cart[1], norm_ed_np_cart[0]))
    ed_np_lat = np.degrees(np.arcsin(norm_ed_np_cart[2]))
    ax.plot(ed_np_lon, ed_np_lat, 'gs', markersize=10, transform=ccrs.Geodetic(), label='ED Pole', zorder=5)
    # South Pole is at ED Cartesian [0, 0, -r0]
    ed_sp_cart = coordinates.ed_to_geographic(np.array([0,0,-r0]), rot_matrix, r0, ed_params_geo)
    norm_ed_sp_cart = ed_sp_cart / np.linalg.norm(ed_sp_cart)
    ed_sp_lon = np.degrees(np.arctan2(norm_ed_sp_cart[1], norm_ed_sp_cart[0]))
    ed_sp_lat = np.degrees(np.arcsin(norm_ed_sp_cart[2]))
    ax.plot(ed_sp_lon, ed_sp_lat, 'gs', markersize=10, transform=ccrs.Geodetic(), zorder=5)


    ax.legend(loc='upper right')
    plt.savefig("geomagnetic_all_grids_with_poles.png", dpi=300)
    print("Plot saved as geomagnetic_all_grids_with_poles.png")

if __name__ == '__main__':
    main()