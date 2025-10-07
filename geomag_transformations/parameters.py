### `geomag_transformations/parameters.py`

# This module contains the core functions for calculating model parameters from the Gauss coefficients.


# geomag_transformations/parameters.py
import numpy as np

# --- IGRF-1990 Model Constants ---
G1_0 = -29775.0
G1_1 = -1851.0
H1_1 = 5411.0
G2_0 = -2136.0
G2_1 = 3058.0
H2_1 = -2278.0
G2_2 = 1693.0
H2_2 = -380.0
R0 = 6371.2  # Earth's mean radius in km

def calculate_cd_parameters(g1_0, g1_1, h1_1):
    """Calculates Centered Dipole (CD) parameters from Gauss coefficients."""
    B0 = np.sqrt(g1_0**2 + g1_1**2 + h1_1**2)
    theta_n_prime_rad = np.arccos(-g1_0 / B0)
    lambda_n_prime_rad = np.arctan2(-h1_1, -g1_1)
    return B0, theta_n_prime_rad, lambda_n_prime_rad

def calculate_rotation_matrix(theta_n_prime_rad, lambda_n_prime_rad):
    """Calculates the rotation matrix to transform from geographic to CD coordinates."""
    cos_theta, sin_theta = np.cos(theta_n_prime_rad), np.sin(theta_n_prime_rad)
    cos_lambda, sin_lambda = np.cos(lambda_n_prime_rad), np.sin(lambda_n_prime_rad)
    l1, m1, n1 = cos_theta * cos_lambda, cos_theta * sin_lambda, -sin_theta
    l2, m2, n2 = -sin_lambda, cos_lambda, 0
    l3, m3, n3 = sin_theta * cos_lambda, sin_theta * sin_lambda, cos_theta
    return np.array([[l1, m1, n1], [l2, m2, n2], [l3, m3, n3]])

def calculate_ed_parameters(g1_0, g1_1, h1_1, g2_0, g2_1, h2_1, g2_2, h2_2, B0):
    """Calculates Eccentric Dipole (ED) position parameters."""
    L1 = -g1_1 * g2_0 + np.sqrt(3) * (g1_0 * g2_1 + g1_1 * g2_2 + h1_1 * h2_2)
    L2 = -h1_1 * g2_0 + np.sqrt(3) * (g1_0 * h2_1 - h1_1 * g2_2 + g1_1 * h2_2)
    L0 = 2 * g1_0 * g2_0 + np.sqrt(3) * (g1_1 * g2_1 + h1_1 * h2_1)
    E = (L0 * g1_0 + L1 * g1_1 + L2 * h1_1) / (4 * B0**2)
    eta = (L1 - g1_1 * E) / (3 * B0**2)
    zeta = (L2 - h1_1 * E) / (3 * B0**2)
    xi = (L0 - g1_0 * E) / (3 * B0**2)
    return np.array([eta, zeta, xi])