"""
Data format definitions for SHMR datasets compatible with Galacticus.

This module defines the standard data structures and formats used for
storing stellar mass-halo mass relations that can be directly read by
Galacticus's stellarHaloMassRelation analysis class.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import numpy as np


@dataclass
class GalacticusCosmology:
    """
    Cosmology parameters for Galacticus compatibility.
    
    Attributes
    ----------
    OmegaMatter : float
        Matter density parameter (Ω_M)
    OmegaDarkEnergy : float  
        Dark energy density parameter (Ω_Λ)
    OmegaBaryon : float
        Baryon density parameter (Ω_b)
    HubbleConstant : float
        Hubble constant in km/s/Mpc (H₀)
    """
    OmegaMatter: float
    OmegaDarkEnergy: float
    OmegaBaryon: float
    HubbleConstant: float


@dataclass
class RedshiftInterval:
    """
    Data for a single redshift interval compatible with Galacticus format.
    
    This represents the data structure for one redshiftIntervalN group
    in the HDF5 file that Galacticus expects.
    
    Attributes
    ----------
    massHalo : np.ndarray
        Halo masses in units of M☉
    massStellar : np.ndarray  
        Stellar masses in units of M☉
    massStellarError : np.ndarray
        Uncertainties in stellar mass in units of M☉
    massStellarScatter : np.ndarray
        Scatter in stellar mass in units of dex
    massStellarScatterError : np.ndarray
        Uncertainty in scatter in stellar mass in units of dex
    redshiftMinimum : float
        Minimum redshift for this interval
    redshiftMaximum : float
        Maximum redshift for this interval
    """
    massHalo: np.ndarray
    massStellar: np.ndarray
    massStellarError: np.ndarray
    massStellarScatter: np.ndarray
    massStellarScatterError: np.ndarray
    redshiftMinimum: float
    redshiftMaximum: float
    
    def __post_init__(self):
        """Validate and convert arrays after initialization."""
        # Convert to numpy arrays
        self.massHalo = np.asarray(self.massHalo)
        self.massStellar = np.asarray(self.massStellar)
        self.massStellarError = np.asarray(self.massStellarError)
        self.massStellarScatter = np.asarray(self.massStellarScatter)
        self.massStellarScatterError = np.asarray(self.massStellarScatterError)
        
        # Validate array lengths
        arrays = [self.massHalo, self.massStellar, self.massStellarError, 
                 self.massStellarScatter, self.massStellarScatterError]
        if not all(len(arr) == len(arrays[0]) for arr in arrays):
            raise ValueError("All data arrays must have the same length")
    
    @property 
    def n_points(self) -> int:
        """Number of data points in this redshift interval."""
        return len(self.massHalo)


@dataclass
class BlackHoleRedshiftInterval:
    """
    Data for a single redshift interval for black hole mass relations.
    
    This represents the data structure for one redshiftIntervalN group
    in the HDF5 file that Galacticus expects for black hole mass relations.
    
    Attributes
    ----------
    massHalo : np.ndarray
        Halo masses in units of M☉
    massBlackHole : np.ndarray  
        Black hole masses in units of M☉
    massBlackHoleError : np.ndarray
        Uncertainties in black hole mass in units of M☉
    massBlackHoleScatter : np.ndarray
        Scatter in black hole mass in units of dex
    massBlackHoleScatterError : np.ndarray
        Uncertainty in scatter in black hole mass in units of dex
    redshiftMinimum : float
        Minimum redshift for this interval
    redshiftMaximum : float
        Maximum redshift for this interval
    """
    massHalo: np.ndarray
    massBlackHole: np.ndarray
    massBlackHoleError: np.ndarray
    massBlackHoleScatter: np.ndarray
    massBlackHoleScatterError: np.ndarray
    redshiftMinimum: float
    redshiftMaximum: float
    
    def __post_init__(self):
        """Validate and convert arrays after initialization."""
        # Convert to numpy arrays
        self.massHalo = np.asarray(self.massHalo)
        self.massBlackHole = np.asarray(self.massBlackHole)
        self.massBlackHoleError = np.asarray(self.massBlackHoleError)
        self.massBlackHoleScatter = np.asarray(self.massBlackHoleScatter)
        self.massBlackHoleScatterError = np.asarray(self.massBlackHoleScatterError)
        
        # Validate array lengths
        arrays = [self.massHalo, self.massBlackHole, self.massBlackHoleError, 
                 self.massBlackHoleScatter, self.massBlackHoleScatterError]
        if not all(len(arr) == len(arrays[0]) for arr in arrays):
            raise ValueError("All data arrays must have the same length")
    
    @property 
    def n_points(self) -> int:
        """Number of data points in this redshift interval."""
        return len(self.massHalo)


@dataclass 
class GalacticusSHMRData:
    """
    Container for SHMR data compatible with Galacticus format.
    
    This class holds SHMR data in the exact structure that Galacticus
    expects: multiple redshift intervals, cosmology parameters, and
    required metadata attributes.
    
    Attributes
    ----------
    redshift_intervals : List[RedshiftInterval]
        List of redshift intervals, each containing SHMR data
    cosmology : GalacticusCosmology  
        Cosmological parameters
    haloMassDefinition : str
        Halo mass definition (e.g., "virial", "200 * critical density")
    label : str
        Space-free label for the dataset (e.g., "Behroozi2010")
    reference : str
        Reference citation for figures (e.g., "Behroozi et al. (2013)")
    """
    redshift_intervals: List[RedshiftInterval]
    cosmology: GalacticusCosmology
    haloMassDefinition: str
    label: str
    reference: str
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.redshift_intervals:
            raise ValueError("At least one redshift interval is required")
        
        if not self.label.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Label should be space-free (alphanumeric, underscore, hyphen only)")
    
    @property
    def n_redshift_intervals(self) -> int:
        """Number of redshift intervals in the dataset."""
        return len(self.redshift_intervals)
    
    @property 
    def total_data_points(self) -> int:
        """Total number of data points across all redshift intervals."""
        return sum(interval.n_points for interval in self.redshift_intervals)
    
    @property
    def redshift_range(self) -> tuple:
        """Get the full redshift range covered by this dataset."""
        if not self.redshift_intervals:
            return (0.0, 0.0)
        
        z_min = min(interval.redshiftMinimum for interval in self.redshift_intervals)
        z_max = max(interval.redshiftMaximum for interval in self.redshift_intervals)
        return (z_min, z_max)


@dataclass 
class GalacticusBHMRData:
    """
    Container for BHMR (Black Hole Mass - Halo Mass Relation) data compatible with Galacticus format.
    
    This class holds BHMR data in the exact structure that Galacticus
    expects: multiple redshift intervals, cosmology parameters, and
    required metadata attributes.
    
    Attributes
    ----------
    redshift_intervals : List[BlackHoleRedshiftInterval]
        List of redshift intervals, each containing BHMR data
    cosmology : GalacticusCosmology  
        Cosmological parameters
    haloMassDefinition : str
        Halo mass definition (e.g., "virial", "200 * critical density")
    label : str
        Space-free label for the dataset (e.g., "TRINITY")
    reference : str
        Reference citation for figures (e.g., "Zhang et al. (2022)")
    """
    redshift_intervals: List[BlackHoleRedshiftInterval]
    cosmology: GalacticusCosmology
    haloMassDefinition: str
    label: str
    reference: str
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.redshift_intervals:
            raise ValueError("At least one redshift interval is required")
        
        if not self.label.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Label should be space-free (alphanumeric, underscore, hyphen only)")
    
    @property
    def n_redshift_intervals(self) -> int:
        """Number of redshift intervals in the dataset."""
        return len(self.redshift_intervals)
    
    @property 
    def total_data_points(self) -> int:
        """Total number of data points across all redshift intervals."""
        return sum(interval.n_points for interval in self.redshift_intervals)
    
    @property
    def redshift_range(self) -> tuple:
        """Get the full redshift range covered by this dataset."""
        if not self.redshift_intervals:
            return (0.0, 0.0)
        
        z_min = min(interval.redshiftMinimum for interval in self.redshift_intervals)
        z_max = max(interval.redshiftMaximum for interval in self.redshift_intervals)
        return (z_min, z_max)


# Standard halo mass definitions supported by Galacticus
GALACTICUS_HALO_MASS_DEFINITIONS = [
    "spherical collapse",
    "virial", 
    "Bryan & Norman (1998)",
    "200 * mean density",
    "200 * critical density",
    "500 * mean density", 
    "500 * critical density",
    "1000 * mean density",
    "1000 * critical density"
]

# Standard dataset descriptions for common datasets
DATASET_DESCRIPTIONS = {
    "massHalo": "Halo mass",
    "massStellar": "Stellar mass", 
    "massStellarError": "Uncertainty in stellar mass",
    "massStellarScatter": "Intrinsic scatter in stellar mass",
    "massStellarScatterError": "Uncertainty in intrinsic scatter",
    "massBlackHole": "Black hole mass",
    "massBlackHoleError": "Uncertainty in black hole mass",
    "massBlackHoleScatter": "Intrinsic scatter in black hole mass",
    "massBlackHoleScatterError": "Uncertainty in intrinsic scatter"
}

# Units in SI for conversion (Galacticus expects SI conversion factors)
UNITS_IN_SI = {
    "Msun": 1.98847e30,  # Solar masses to kg
    "dex": 1.0           # dex is dimensionless
}


def create_example_cosmology() -> GalacticusCosmology:
    """
    Create an example cosmology (Planck 2018 values).
    
    Returns
    -------
    GalacticusCosmology
        Standard cosmological parameters
    """
    return GalacticusCosmology(
        OmegaMatter=0.3111,
        OmegaDarkEnergy=0.6889,
        OmegaBaryon=0.04897,
        HubbleConstant=67.66
    )


def validate_halo_mass_definition(definition: str) -> bool:
    """
    Validate that a halo mass definition is supported by Galacticus.
    
    Parameters
    ----------
    definition : str
        Halo mass definition to validate
        
    Returns
    -------
    bool
        True if the definition is valid
    """
    return definition in GALACTICUS_HALO_MASS_DEFINITIONS