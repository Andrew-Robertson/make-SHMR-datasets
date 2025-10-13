# Black Hole Mass - Halo Mass Relation Implementation

This document describes the implementation of black hole mass - halo mass relation (BHMR) support in the SHMR datasets repository.

## Overview

The repository now supports both:
- **SHMR**: Stellar Mass - Halo Mass Relations
- **BHMR**: Black Hole Mass - Halo Mass Relations

Both follow the exact HDF5 format specifications required by Galacticus.

## Galacticus BHMR Format Specification

The BHMR format follows the specification for Galacticus's `outputAnalysisBlackHoleVsHaloMassRelation` class.

### File Structure

```
file.hdf5
├── @haloMassDefinition (attribute)
├── @label (attribute)
├── @reference (attribute)
├── cosmology/
│   ├── @OmegaMatter
│   ├── @OmegaDarkEnergy
│   ├── @OmegaBaryon
│   └── @HubbleConstant
├── redshiftInterval1/
│   ├── @redshiftMinimum
│   ├── @redshiftMaximum
│   ├── massHalo (dataset)
│   ├── massBlackHole (dataset)
│   ├── massBlackHoleError (dataset)
│   ├── massBlackHoleScatter (dataset)
│   └── massBlackHoleScatterError (dataset)
├── redshiftInterval2/
│   └── ...
└── ...
```

### Required Datasets

Each redshift interval must contain:

| Dataset | Description | Units | SI Conversion |
|---------|-------------|-------|---------------|
| `massHalo` | Halo mass | M☉ | 1.98847×10³⁰ kg |
| `massBlackHole` | Black hole mass | M☉ | 1.98847×10³⁰ kg |
| `massBlackHoleError` | Uncertainty in black hole mass | M☉ | 1.98847×10³⁰ kg |
| `massBlackHoleScatter` | Scatter in black hole mass | dex | 1.0 (dimensionless) |
| `massBlackHoleScatterError` | Uncertainty in scatter | dex | 1.0 (dimensionless) |

### Required Attributes

Each redshift interval group must have:
- `redshiftMinimum`: Minimum redshift for this interval
- `redshiftMaximum`: Maximum redshift for this interval

Each dataset should have:
- `description`: Human-readable description
- `unitsInSI`: Conversion factor to SI units

## Python API

### Data Classes

```python
from shmr_datasets import BlackHoleRedshiftInterval, GalacticusBHMRData, GalacticusCosmology

# Create a redshift interval
interval = BlackHoleRedshiftInterval(
    massHalo=halo_masses,                    # numpy array
    massBlackHole=bh_masses,                 # numpy array
    massBlackHoleError=bh_errors,            # numpy array
    massBlackHoleScatter=scatter,            # numpy array
    massBlackHoleScatterError=scatter_err,   # numpy array
    redshiftMinimum=0.0,
    redshiftMaximum=1.0
)

# Create complete dataset
data = GalacticusBHMRData(
    redshift_intervals=[interval1, interval2],
    cosmology=GalacticusCosmology(...),
    haloMassDefinition="virial",
    label="MyBHMR",
    reference="Smith et al. (2024)"
)
```

### I/O Functions

```python
from shmr_datasets import (
    save_galacticus_bhmr,
    load_galacticus_bhmr,
    validate_galacticus_bhmr_file,
    print_galacticus_bhmr_file_info
)

# Save BHMR data
save_galacticus_bhmr(data, "my_bhmr.hdf5")

# Load BHMR data
loaded_data = load_galacticus_bhmr("my_bhmr.hdf5")

# Validate file
results = validate_galacticus_bhmr_file("my_bhmr.hdf5")
if results['valid']:
    print("✅ File is valid")

# Display file information
print_galacticus_bhmr_file_info("my_bhmr.hdf5")
```

## Using with Galacticus

To use a BHMR dataset in Galacticus, add the following to your parameter file:

```xml
<blackHoleVsHaloMassRelation value="file">
  <fileNameTarget value="path/to/your_bhmr.hdf5"/>
</blackHoleVsHaloMassRelation>
```

Galacticus will automatically:
- Read the cosmology and apply appropriate conversions
- Interpolate between redshift intervals
- Convert between different halo mass definitions if needed

## Example: TRINITY Dataset

The repository includes an example BHMR dataset from the TRINITY project:

**Location:** `data/observations/trinity/trinity_bhmr.hdf5`

**Reference:** Zhang et al. 2022, MNRAS, 518, 2123 (arXiv:2208.00719)

**Description:** Semi-empirical black hole mass - halo mass relation from z=0 to z=10

**Creation Script:** `scripts/create_trinity_bhmr.py`

### TRINITY Dataset Details

- 10 redshift intervals covering z=0-10
- 78 total data points
- Uses virial (peak) halo mass definition
- Planck 2018 cosmology
- Includes scatter estimates from the TRINITY model

### Creating the TRINITY Dataset

```bash
python scripts/create_trinity_bhmr.py
```

This will:
1. Read the TRINITY data from `data/observations/trinity/fig14_median_BHHM_fit_z0-10.txt`
2. Parse the data by redshift intervals
3. Convert logarithmic masses to linear masses
4. Add appropriate uncertainties
5. Save in Galacticus-compatible format
6. Validate the created file

## Validation

The validation script automatically detects file type and validates accordingly:

```bash
# Validate a single BHMR file
python scripts/validate.py data/observations/trinity/trinity_bhmr.hdf5

# Validate all files in a directory
python scripts/validate.py data/observations/trinity/

# The script will automatically detect BHMR vs SHMR files
```

## Implementation Details

### Code Structure

The BHMR implementation follows the same pattern as SHMR but with different field names:

| SHMR Field | BHMR Field |
|------------|------------|
| `massStellar` | `massBlackHole` |
| `massStellarError` | `massBlackHoleError` |
| `massStellarScatter` | `massBlackHoleScatter` |
| `massStellarScatterError` | `massBlackHoleScatterError` |
| `RedshiftInterval` | `BlackHoleRedshiftInterval` |
| `GalacticusSHMRData` | `GalacticusBHMRData` |

### File Detection

The validation script automatically detects file type by checking for the presence of `massStellar` (SHMR) or `massBlackHole` (BHMR) datasets in the first redshift interval.

### Backward Compatibility

All existing SHMR functionality remains unchanged. The BHMR implementation is completely parallel and does not affect existing code.

## Creating New BHMR Datasets

To create a new BHMR dataset:

1. **Prepare your data** as numpy arrays:
   - Halo masses (in M☉)
   - Black hole masses (in M☉)
   - Uncertainties and scatter values

2. **Create redshift intervals**:
   ```python
   interval = BlackHoleRedshiftInterval(
       massHalo=halo_masses,
       massBlackHole=bh_masses,
       massBlackHoleError=bh_errors,
       massBlackHoleScatter=scatter,
       massBlackHoleScatterError=scatter_errors,
       redshiftMinimum=z_min,
       redshiftMaximum=z_max
   )
   ```

3. **Specify cosmology**:
   ```python
   cosmology = GalacticusCosmology(
       OmegaMatter=0.3,
       OmegaDarkEnergy=0.7,
       OmegaBaryon=0.045,
       HubbleConstant=70.0
   )
   ```

4. **Create and save dataset**:
   ```python
   data = GalacticusBHMRData(
       redshift_intervals=[interval],
       cosmology=cosmology,
       haloMassDefinition="virial",
       label="MyDataset",
       reference="Author et al. (Year)"
   )
   
   save_galacticus_bhmr(data, "my_dataset.hdf5")
   ```

5. **Validate**:
   ```bash
   python scripts/validate.py my_dataset.hdf5
   ```

## Differences from SHMR

The main differences between SHMR and BHMR formats are:

1. **Dataset names**: `massStellar*` → `massBlackHole*`
2. **Typical mass ranges**: 
   - SHMR: M☉ ~ 10⁸ - 10¹² 
   - BHMR: M☉ ~ 10⁵ - 10¹⁰
3. **Physical interpretation**: Different astrophysical processes
4. **Scatter magnitudes**: Typically larger for black holes

## References

- **Galacticus Documentation**: https://github.com/galacticusorg/galacticus
- **TRINITY Project**: https://github.com/HaowenZhang/TRINITY
- **Zhang et al. 2022**: MNRAS, 518, 2123 (arXiv:2208.00719)

## Support

For questions or issues:
- Check the examples in `scripts/create_trinity_bhmr.py`
- Review the TRINITY dataset README
- Open an issue on GitHub
