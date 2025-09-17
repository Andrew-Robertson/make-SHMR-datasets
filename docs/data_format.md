# SHMR Data Format Specification (Galacticus Compatible)

## Overview

This document describes the standardized HDF5 data format used in the SHMR (Stellar Mass - Halo Mass Relations) datasets repository. The format is designed to be directly compatible with Galacticus's `stellarHaloMassRelation` analysis class, ensuring complete data provenance and ease of integration with astrophysical simulations.

## File Format

The repository supports **HDF5 format only** (`.hdf5` extension):

- **Primary format**: HDF5 with automatic gzip compression for data arrays
- **Metadata**: Stored as HDF5 attributes and group structures
- **Compatibility**: Direct integration with Galacticus simulation code
- **Use case**: All dataset storage, distribution, and archival

## Galacticus Data Structure

Each SHMR dataset file must contain the following structure to be compatible with Galacticus:

### Required Top-Level Attributes
- `haloMassDefinition`: Halo mass definition (e.g., "virial", "Bryan & Norman (1998)", "200 * critical density")
- `label`: Space-free label for the dataset (e.g., "Behroozi2010")
- `reference`: Reference citation suitable for figures (e.g., "Behroozi et al. (2010)")

### Required Groups

#### Cosmology Group (`/cosmology`)
Contains cosmological parameters as attributes:
- `OmegaMatter`: Matter density parameter (Ω_M)
- `OmegaDarkEnergy`: Dark energy density parameter (Ω_Λ)  
- `OmegaBaryon`: Baryon density parameter (Ω_b)
- `HubbleConstant`: Hubble constant in km/s/Mpc (H₀)

#### Redshift Interval Groups (`/redshiftIntervalN`)
One or more groups named `redshiftInterval0`, `redshiftInterval1`, etc., each containing:

##### Required Datasets (all in solar masses M☉ unless otherwise noted):
- `massHalo`: Halo masses
- `massStellar`: Stellar masses
- `massStellarError`: Uncertainties in stellar masses
- `massStellarScatter`: Intrinsic scatter in stellar mass (in dex)
- `massStellarScatterError`: Uncertainties in intrinsic scatter (in dex)

##### Required Group Attributes:
- `redshiftMinimum`: Minimum redshift for this interval
- `redshiftMaximum`: Maximum redshift for this interval

##### Optional Dataset Attributes:
- `description`: Human-readable description of the dataset
- `unitsInSI`: Multiplicative factor to convert to SI units

### Supported Halo Mass Definitions

Galacticus supports the following halo mass definitions:
- `"spherical collapse"` or `"virial"`: Spherical collapse calculations
- `"Bryan & Norman (1998)"`: Bryan & Norman (1998) fitting formula
- `"200 * mean density"`: 200 times mean density of universe
- `"200 * critical density"`: 200 times critical density of universe
- `"500 * mean density"`: 500 times mean density of universe
- `"500 * critical density"`: 500 times critical density of universe
- And similar for other overdensity values

## Example Data Structure

```python
# Example using h5py
import h5py

with h5py.File('example_shmr.hdf5', 'w') as f:
    # Top-level attributes
    f.attrs['haloMassDefinition'] = 'virial'
    f.attrs['label'] = 'Behroozi2010'
    f.attrs['reference'] = 'Behroozi et al. (2010)'
    
    # Cosmology group
    cosmo = f.create_group('cosmology')
    cosmo.attrs['OmegaMatter'] = 0.279
    cosmo.attrs['OmegaDarkEnergy'] = 0.721
    cosmo.attrs['OmegaBaryon'] = 0.0469
    cosmo.attrs['HubbleConstant'] = 70.0
    
    # Redshift interval
    interval = f.create_group('redshiftInterval0')
    interval.attrs['redshiftMinimum'] = 0.0
    interval.attrs['redshiftMaximum'] = 0.5
    
    # Datasets with attributes
    mh = interval.create_dataset('massHalo', data=halo_masses)
    mh.attrs['description'] = 'Halo mass'
    mh.attrs['unitsInSI'] = 1.98847e30  # M☉ to kg
    
    ms = interval.create_dataset('massStellar', data=stellar_masses)
    ms.attrs['description'] = 'Stellar mass'
    ms.attrs['unitsInSI'] = 1.98847e30  # M☉ to kg
    
    # Additional required datasets...
```

## Validation Rules

1. **Required Structure**: Must contain all required groups and attributes
2. **Array Consistency**: All datasets within a redshift interval must have same length
3. **Positive Masses**: All mass values must be positive
4. **Valid Cosmology**: Cosmological parameters must be physically reasonable
5. **Halo Mass Definition**: Must be one of the supported definitions
6. **Redshift Ordering**: Redshift intervals should not overlap

## Naming Conventions

### File Names
- Use descriptive names: `behroozi2010_parametric.hdf5`
- Include key parameters: redshift range, galaxy type, etc.
- Use lowercase with underscores
- Always use `.hdf5` extension

### Dataset Labels  
- Use author + year format: "Behroozi2010", "Moster2013"
- Keep space-free for Galacticus compatibility
- Include distinguishing features if multiple variants exist

### Directory Structure
```
data/
├── observations/
│   └── leauthaud2012/
├── simulations/
│   └── universemachine/
└── theory/
    ├── behroozi2010/
    ├── behroozi2013/
    └── moster2013/
```

## Integration with Galacticus

Files following this format can be used directly in Galacticus parameter files:

```xml
<stellarHaloMassRelation value="file">
  <fileName value="path/to/dataset.hdf5"/>
</stellarHaloMassRelation>
```

Galacticus will automatically:
1. Read the cosmological parameters and apply conversions if needed
2. Use the specified halo mass definition for internal calculations
3. Interpolate between redshift intervals as needed
4. Apply appropriate unit conversions using `unitsInSI` attributes

## Quality Assurance

All datasets should:
1. **Pass Validation**: Use `scripts/validate.py` to ensure format compliance
2. **Include Provenance**: Complete documentation of data sources and methods
3. **Physical Validation**: Verify results are physically reasonable
4. **Galacticus Testing**: Test compatibility with actual Galacticus runs

## Creating New Datasets

Use the provided example scripts:
- `scripts/create_behroozi2010_parametric.py`: Creating from parametric models
- `scripts/create_universemachine_downloaded.py`: Creating from downloaded data

Both scripts demonstrate the complete workflow from data sources to validated Galacticus-compatible files.