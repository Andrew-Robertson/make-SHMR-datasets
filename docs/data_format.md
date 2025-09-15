# SHMR Data Format Specification

## Overview

This document describes the standardized data format used in the SHMR (Stellar Mass - Halo Mass Relations) datasets repository. The format is designed to ensure complete data provenance, compatibility with analysis tools, and ease of use for astrophysical applications.

## File Formats

The repository supports three file formats:

### 1. HDF5 (.h5)
- **Best for**: Large datasets, binary storage with compression
- **Compression**: Automatic gzip compression for data arrays
- **Metadata**: Stored as HDF5 attributes
- **Use case**: Primary format for distribution and archival

### 2. YAML (.yaml)
- **Best for**: Human-readable datasets, configuration files
- **Compression**: None (text-based)
- **Metadata**: Fully human-readable structure
- **Use case**: Small datasets, documentation, examples

### 3. JSON (.json)
- **Best for**: Web compatibility, API integration
- **Compression**: None (text-based)
- **Metadata**: Standard JSON structure
- **Use case**: Web applications, API responses

## Data Structure

Each SHMR dataset consists of:

### Required Data Arrays
- `halo_mass`: Array of halo masses (units specified in metadata)
- `stellar_mass`: Array of corresponding stellar masses (units specified in metadata)

### Optional Data Arrays
- `stellar_mass_err_lower`: Lower uncertainties on stellar masses
- `stellar_mass_err_upper`: Upper uncertainties on stellar masses
- `halo_mass_err_lower`: Lower uncertainties on halo masses
- `halo_mass_err_upper`: Upper uncertainties on halo masses
- `extra_data`: Dictionary of additional data arrays (e.g., redshift, scatter)

### Metadata Fields

#### Required Fields
- `name`: Short descriptive name for the dataset
- `version`: Version string (e.g., "1.0", "2.1")
- `description`: Detailed description of the data
- `source_type`: Type of data source ("observation", "simulation", "theory", "compilation")
- `reference`: Primary reference (paper, survey, etc.)
- `creation_method`: How the data was created ("download", "calculation", "extraction", "compilation")
- `creation_date`: ISO format date string (YYYY-MM-DD)
- `created_by`: Person or organization who created the dataset

#### Optional Fields
- `doi`: DOI of primary reference
- `url`: URL where data was obtained
- `cosmology`: Dictionary of cosmological parameters
- `redshift`: Redshift(s) of the data (float or list)
- `stellar_mass_definition`: Definition of stellar mass used
- `halo_mass_definition`: Definition of halo mass used (e.g., "M200c", "Mvir")
- `mass_range`: Dictionary with mass range information
- `uncertainties_included`: Boolean indicating if uncertainties are available
- `systematic_errors`: Description of systematic uncertainties
- `limitations`: Known limitations or caveats
- `units`: Dictionary specifying units for each quantity
- `tags`: List of descriptive tags
- `notes`: Additional notes or comments
- `related_datasets`: List of related dataset names

## Example Data Structure

```yaml
metadata:
  name: "Behroozi et al. 2013 SHMR"
  version: "1.0"
  description: "Stellar mass - halo mass relation from Behroozi et al. 2013"
  source_type: "observation"
  reference: "Behroozi, Wechsler & Conroy 2013, ApJ, 770, 57"
  doi: "10.1088/0004-637X/770/1/57"
  creation_method: "extraction"
  creation_date: "2024-01-15"
  created_by: "A. Robertson"
  redshift: 0.0
  stellar_mass_definition: "total"
  halo_mass_definition: "M200c"
  cosmology:
    h: 0.7
    omega_m: 0.27
    omega_lambda: 0.73
  units:
    stellar_mass: "Msun"
    halo_mass: "Msun"
  uncertainties_included: true
  tags: ["abundance_matching", "central_galaxies"]
  
data:
  halo_mass: [1.0e10, 1.0e11, 1.0e12, 1.0e13, 1.0e14]
  stellar_mass: [1.0e7, 1.0e9, 1.0e10, 5.0e10, 1.0e11]
  stellar_mass_err_lower: [0.1e7, 0.1e9, 0.1e10, 0.5e10, 0.1e11]
  stellar_mass_err_upper: [0.1e7, 0.1e9, 0.1e10, 0.5e10, 0.1e11]
```

## Validation Rules

1. **Array Consistency**: All data arrays must have the same length
2. **Positive Masses**: All mass values must be positive
3. **Unit Consistency**: Units must be specified and consistent throughout
4. **Metadata Completeness**: All required metadata fields must be present
5. **Error Array Matching**: Error arrays, if present, must match data array lengths

## Naming Conventions

### File Names
- Use descriptive names: `behroozi2013_z0_central.h5`
- Include key parameters: redshift, galaxy type, etc.
- Use lowercase with underscores

### Dataset Names  
- Use author + year format: "Behroozi et al. 2013"
- Include key distinguishing features: "z=2.0", "centrals only"

### Directory Structure
```
data/
├── observations/
│   ├── behroozi2013/
│   └── moster2013/
├── simulations/
│   ├── eagle/
│   └── illustris/
└── theory/
    ├── analytical_models/
    └── semi_analytical/
```

## Version Control

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Increment MAJOR for incompatible changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

## Integration with Galacticus

The format is designed to be easily convertible to Galacticus input formats:

1. **Mass definitions**: Standard definitions compatible with Galacticus
2. **Units**: Solar masses as primary unit
3. **Cosmology**: Standard cosmological parameters
4. **Interpolation**: Built-in interpolation functions for smooth relations

## Quality Assurance

All datasets should include:
1. **Validation**: Pass format validation checks
2. **Documentation**: Complete metadata and provenance
3. **Testing**: Verify physical reasonableness
4. **Review**: Peer review of data extraction/calculation