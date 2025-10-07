# geomag_transformations/__init__.py
#This file makes the package easier to use by exposing the main functions at the top level.
# Expose key functions for easy access

from . import coordinates
from . import times

# You can also expose specific functions directly if you prefer
# from .times import calculate_geomagnetic_times
# from .coordinates import transform_geographic_point