"""
SHMR Datasets Package

A package for storing and managing stellar mass - halo mass relations (SHMRs) 
with complete data provenance and compatibility with Galacticus.
"""

__version__ = "0.1.0"
__author__ = "Andrew Robertson"

from .data_format import SHMRData, SHMRMetadata
from .io import load_shmr, save_shmr, validate_shmr
from .utils import calculate_shmr, interpolate_shmr

__all__ = [
    "SHMRData",
    "SHMRMetadata", 
    "load_shmr",
    "save_shmr",
    "validate_shmr",
    "calculate_shmr",
    "interpolate_shmr"
]