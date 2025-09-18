# Example Scripts

This directory contains example scripts demonstrating how to create and analyze SHMR datasets in Galacticus format.

## Plotting and Analysis Scripts

### `plot_shmr_comparison.py`
Comprehensive SHMR comparison tool that plots all available datasets at z≈0.1, z≈1, and z≈2.

**Features:**
- Automatically finds best-matching redshift intervals for each dataset
- Creates side-by-side comparison plots with error bars
- Provides dataset summary with redshift coverage
- Handles missing data gracefully
- Outputs high-resolution PNG for analysis

**Usage:**
```bash
python scripts/plot_shmr_comparison.py
```

**Output:** 
- Console summary of all datasets
- `shmr_comparison.png` - comparison plot saved to current directory

This tool is perfect for:
- Visual quality control of SHMR datasets
- Identifying anomalies or inconsistencies
- Comparing theoretical models vs simulations
- Verifying parameter uncertainty propagation results

## Parametric Model Example

**Script**: `create_behroozi2010_parametric.py`

Creates an SHMR dataset from the Behroozi et al. 2010 parametric model (arXiv:1001.0015). This demonstrates:

- Implementing theoretical SHMR parametrizations
- Creating multiple redshift intervals
- Using appropriate cosmological parameters
- Proper Galacticus format structure

**Usage**:
```bash
python scripts/create_behroozi2010_parametric.py
```

**Output**: `data/theory/behroozi2010/behroozi2010_parametric.hdf5`

## Downloaded Data Example

**Script**: `create_universemachine_downloaded.py`

Creates an SHMR dataset based on the UniverseMachine project (Behroozi et al. 2019, arXiv:1806.07893). This demonstrates:

- Processing downloaded/external data
- Data provenance documentation  
- Converting to Galacticus format
- Handling observational uncertainties

**Usage**:
```bash
python scripts/create_universemachine_downloaded.py
```

**Output**: `data/simulations/universemachine/universemachine_downloaded.hdf5`

## Validation

Both scripts automatically validate their output using the included validation tool:

```bash
python scripts/validate.py data/theory/behroozi2010/behroozi2010_parametric.hdf5
python scripts/validate.py data/simulations/universemachine/universemachine_downloaded.hdf5
```

## Using in Galacticus

All created datasets can be used directly in Galacticus parameter files:

```xml
<stellarHaloMassRelation value="file">
  <fileName value="path/to/dataset.hdf5"/>
</stellarHaloMassRelation>
```

Galacticus will automatically read the cosmology, halo mass definition, and redshift intervals, applying appropriate conversions as needed.