"""
Data format definitions for SHMR datasets.

This module defines the standard data structures and formats used throughout
the SHMR datasets repository.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import numpy as np


@dataclass
class SHMRMetadata:
    """
    Metadata for an SHMR dataset, including complete provenance information.
    
    This class stores all the necessary information to understand where the
    data came from, how it was processed, and how it can be used.
    """
    
    # Required fields (no defaults)
    name: str
    version: str
    description: str
    source_type: str      # "observation", "simulation", "theory", "compilation"
    reference: str        # Primary paper/source reference
    creation_method: str  # "download", "calculation", "extraction", "compilation"
    creation_date: str    # ISO format date
    created_by: str       # Person/organization who created this dataset
    
    # Optional fields (with defaults)
    doi: Optional[str] = None
    url: Optional[str] = None
    cosmology: Dict[str, float] = field(default_factory=dict)
    redshift: Union[float, List[float]] = 0.0
    stellar_mass_definition: str = "total"  # "total", "disk", "bulge", etc.
    halo_mass_definition: str = "M200c"     # "M200c", "M500c", "Mvir", etc.
    mass_range: Dict[str, float] = field(default_factory=dict)  # min/max masses
    uncertainties_included: bool = False
    systematic_errors: Optional[str] = None
    limitations: Optional[str] = None
    units: Dict[str, str] = field(default_factory=lambda: {
        "stellar_mass": "Msun", 
        "halo_mass": "Msun"
    })
    data_format_version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    related_datasets: List[str] = field(default_factory=list)


@dataclass 
class SHMRData:
    """
    Container for SHMR data with metadata.
    
    This class holds both the numerical data and associated metadata
    for a stellar mass - halo mass relation.
    """
    
    # Core data arrays
    halo_mass: np.ndarray
    stellar_mass: np.ndarray
    
    # Optional uncertainty arrays
    stellar_mass_err_lower: Optional[np.ndarray] = None
    stellar_mass_err_upper: Optional[np.ndarray] = None
    halo_mass_err_lower: Optional[np.ndarray] = None
    halo_mass_err_upper: Optional[np.ndarray] = None
    
    # Metadata
    metadata: SHMRMetadata = field(default_factory=SHMRMetadata)
    
    # Additional data fields
    extra_data: Dict[str, np.ndarray] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate data arrays after initialization."""
        self.halo_mass = np.asarray(self.halo_mass)
        self.stellar_mass = np.asarray(self.stellar_mass)
        
        if len(self.halo_mass) != len(self.stellar_mass):
            raise ValueError("Halo mass and stellar mass arrays must have same length")
        
        # Convert error arrays to numpy arrays if provided
        if self.stellar_mass_err_lower is not None:
            self.stellar_mass_err_lower = np.asarray(self.stellar_mass_err_lower)
        if self.stellar_mass_err_upper is not None:
            self.stellar_mass_err_upper = np.asarray(self.stellar_mass_err_upper)
        if self.halo_mass_err_lower is not None:
            self.halo_mass_err_lower = np.asarray(self.halo_mass_err_lower)
        if self.halo_mass_err_upper is not None:
            self.halo_mass_err_upper = np.asarray(self.halo_mass_err_upper)
    
    @property
    def n_points(self) -> int:
        """Number of data points in the relation."""
        return len(self.halo_mass)
    
    def has_stellar_mass_errors(self) -> bool:
        """Check if stellar mass uncertainties are available."""
        return (self.stellar_mass_err_lower is not None or 
                self.stellar_mass_err_upper is not None)
    
    def has_halo_mass_errors(self) -> bool:
        """Check if halo mass uncertainties are available."""
        return (self.halo_mass_err_lower is not None or 
                self.halo_mass_err_upper is not None)


# Standard file format specifications
SHMR_FILE_FORMATS = {
    "hdf5": {
        "extension": ".h5",
        "description": "HDF5 format for large datasets with compression",
        "compression": True
    },
    "yaml": {
        "extension": ".yaml", 
        "description": "YAML format for human-readable small datasets",
        "compression": False
    },
    "json": {
        "extension": ".json",
        "description": "JSON format for web compatibility",
        "compression": False
    }
}

# Schema for validation
METADATA_SCHEMA = {
    "type": "object",
    "required": ["name", "version", "description", "source_type", "reference", 
                 "creation_method", "creation_date", "created_by"],
    "properties": {
        "name": {"type": "string"},
        "version": {"type": ["string", "number"]},  # Allow both string and number
        "description": {"type": "string"},
        "source_type": {"type": "string", "enum": ["observation", "simulation", "theory", "compilation"]},
        "reference": {"type": "string"},
        "doi": {"type": ["string", "null"]},
        "url": {"type": ["string", "null"]},
        "creation_method": {"type": "string", "enum": ["download", "calculation", "extraction", "compilation"]},
        "creation_date": {"type": "string", "format": "date"},
        "created_by": {"type": "string"},
        "cosmology": {"type": "object"},
        "redshift": {"type": ["number", "array"]},
        "stellar_mass_definition": {"type": "string"},
        "halo_mass_definition": {"type": "string"},
        "mass_range": {"type": "object"},
        "uncertainties_included": {"type": "boolean"},
        "systematic_errors": {"type": ["string", "null"]},
        "limitations": {"type": ["string", "null"]},
        "units": {"type": "object"},
        "data_format_version": {"type": ["string", "number"]},  # Allow both string and number
        "tags": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": ["string", "null"]},
        "related_datasets": {"type": "array", "items": {"type": "string"}}
    }
}