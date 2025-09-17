"""
SHMR Datasets Package

A package for storing and managing stellar mass - halo mass relations (SHMRs) 
with complete data provenance and compatibility with Galacticus.
"""

__version__ = "0.1.0"
__author__ = "Andrew Robertson"

from .data_format import (
    GalacticusSHMRData, 
    RedshiftInterval, 
    GalacticusCosmology,
    create_example_cosmology,
    validate_halo_mass_definition
)
from .io import (
    load_galacticus_shmr, 
    save_galacticus_shmr, 
    validate_galacticus_file,
    print_galacticus_file_info
)
from .utils import calculate_shmr, interpolate_shmr

__all__ = [
    "GalacticusSHMRData",
    "RedshiftInterval", 
    "GalacticusCosmology",
    "create_example_cosmology",
    "validate_halo_mass_definition",
    "load_galacticus_shmr",
    "save_galacticus_shmr",
    "validate_galacticus_file", 
    "print_galacticus_file_info",
    "calculate_shmr",
    "interpolate_shmr"
]