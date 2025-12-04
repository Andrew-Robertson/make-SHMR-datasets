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
    notes : str, optional
        Additional notes about the dataset (e.g., caveats, assumptions)
    """
    redshift_intervals: List[BlackHoleRedshiftInterval]
    cosmology: GalacticusCosmology
    haloMassDefinition: str
    label: str
    reference: str
    notes: Optional[str] = None
    
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
    "massBlackHoleScatterError": "Uncertainty in intrinsic scatter",
    "radiusEffective": "Effective radius",
    "radiusEffectiveError": "Uncertainty in effective radius",
    "radiusEffectiveScatter": "Relative scatter in effective radius (in dex)",
    "radiusEffectiveScatterError": "Uncertainty in Relative scatter in effective radius (in dex)",
    "mainSequenceSFR": "Mean star formation rate on the main sequence"
}

# Units in SI for conversion (Galacticus expects SI conversion factors)
UNITS_IN_SI = {
    "Msun": 1.98847e30,  # Solar masses to kg
    "dex": 1.0,          # dex is dimensionless
    "Mpc": 3.08567758149137e22,  # Megaparsecs to meters
    "Msun/yr": 1.98847e30 / (365.25 * 24 * 3600)  # Solar masses per year to kg/s
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


@dataclass
class MassSizeSample:
    """
    Data for a single mass-size sample compatible with Galacticus format.
    
    This represents the data structure for one sampleN group in the HDF5
    file that Galacticus expects for stellar mass-size relations.
    
    Attributes
    ----------
    massStellar : np.ndarray
        Stellar masses in units of M☉
    radiusEffective : np.ndarray
        Effective radii in units of Mpc
    radiusEffectiveError : np.ndarray
        Uncertainties in effective radius in units of Mpc
    radiusEffectiveScatter : np.ndarray
        Scatter in effective radius in units of dex
    radiusEffectiveScatterError : np.ndarray
        Uncertainty in scatter in effective radius in units of dex
    redshiftMinimum : float
        Minimum redshift for this sample
    redshiftMaximum : float
        Maximum redshift for this sample
    selection : str
        Selection criterion: 'none', 'star forming', or 'quiescent'
    mainSequenceSFR : np.ndarray, optional
        Mean star formation rate on the main sequence (log10 M☉/yr).
        Required for 'star forming' and 'quiescent' selections.
    offsetMainSequenceSFR : float, optional
        Offset below main sequence for quiescent classification.
        Required for 'star forming' and 'quiescent' selections.
    """
    massStellar: np.ndarray
    radiusEffective: np.ndarray
    radiusEffectiveError: np.ndarray
    radiusEffectiveScatter: np.ndarray
    radiusEffectiveScatterError: np.ndarray
    redshiftMinimum: float
    redshiftMaximum: float
    selection: str
    mainSequenceSFR: Optional[np.ndarray] = None
    offsetMainSequenceSFR: Optional[float] = None
    
    def __post_init__(self):
        """Validate and convert arrays after initialization."""
        # Convert to numpy arrays
        self.massStellar = np.asarray(self.massStellar)
        self.radiusEffective = np.asarray(self.radiusEffective)
        self.radiusEffectiveError = np.asarray(self.radiusEffectiveError)
        self.radiusEffectiveScatter = np.asarray(self.radiusEffectiveScatter)
        self.radiusEffectiveScatterError = np.asarray(self.radiusEffectiveScatterError)
        
        # Validate array lengths
        arrays = [self.massStellar, self.radiusEffective, self.radiusEffectiveError,
                 self.radiusEffectiveScatter, self.radiusEffectiveScatterError]
        if not all(len(arr) == len(arrays[0]) for arr in arrays):
            raise ValueError("All data arrays must have the same length")
        
        # Validate selection type
        valid_selections = ['none', 'star forming', 'quiescent']
        if self.selection not in valid_selections:
            raise ValueError(f"Selection must be one of {valid_selections}, got '{self.selection}'")
        
        # Validate that mainSequenceSFR and offsetMainSequenceSFR are provided when needed
        if self.selection in ['star forming', 'quiescent']:
            if self.mainSequenceSFR is None:
                raise ValueError(f"mainSequenceSFR required for selection='{self.selection}'")
            if self.offsetMainSequenceSFR is None:
                raise ValueError(f"offsetMainSequenceSFR required for selection='{self.selection}'")
            self.mainSequenceSFR = np.asarray(self.mainSequenceSFR)
            if len(self.mainSequenceSFR) != len(self.massStellar):
                raise ValueError("mainSequenceSFR must have same length as massStellar")
    
    @property
    def n_points(self) -> int:
        """Number of data points in this sample."""
        return len(self.massStellar)


@dataclass
class GalacticusMassSizeData:
    """
    Container for mass-size relation data compatible with Galacticus format.
    
    This class holds mass-size data in the exact structure that Galacticus
    expects: multiple samples with different selections, cosmology parameters,
    and required metadata attributes.
    
    Attributes
    ----------
    samples : List[MassSizeSample]
        List of mass-size samples, each with its own selection criterion
    cosmology : GalacticusCosmology
        Cosmological parameters
    label : str
        Space-free label for the dataset (e.g., "vanDerWel2014")
    reference : str
        Reference citation for figures (e.g., "van der Wel et al. (2014)")
    notes : str, optional
        Additional notes about the dataset (e.g., data source, methods, caveats)
    creator : str, optional
        Name or identifier of the person/tool that created this file
    creationDate : str, optional
        Date when this file was created (recommended format: YYYY-MM-DD)
    """
    samples: List[MassSizeSample]
    cosmology: GalacticusCosmology
    label: str
    reference: str
    notes: Optional[str] = None
    creator: Optional[str] = None
    creationDate: Optional[str] = None
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.samples:
            raise ValueError("At least one sample is required")
        
        if not self.label.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Label should be space-free (alphanumeric, underscore, hyphen only)")
    
    @property
    def n_samples(self) -> int:
        """Number of samples in the dataset."""
        return len(self.samples)
    
    @property
    def total_data_points(self) -> int:
        """Total number of data points across all samples."""
        return sum(sample.n_points for sample in self.samples)
    
    @property
    def redshift_range(self) -> tuple:
        """Get the full redshift range covered by this dataset."""
        if not self.samples:
            return (0.0, 0.0)
        
        z_min = min(sample.redshiftMinimum for sample in self.samples)
        z_max = max(sample.redshiftMaximum for sample in self.samples)
        return (z_min, z_max)