# SHMR Datasets Repository

A repository for storing and managing stellar mass - halo mass relations (SHMRs) in the exact format required by [Galacticus](https://github.com/galacticusorg/galacticus), with complete data provenance and quality assurance.

## Overview

This repository provides a standardized framework for:

- **Galacticus Compatibility**: Data stored in the exact HDF5 format expected by Galacticus's `stellarHaloMassRelation` analysis class
- **Data Provenance**: Complete documentation of data sources, processing methods, and limitations  
- **Reproducibility**: Scripts and notebooks documenting how datasets were created or downloaded
- **Validation**: Tools to ensure data quality and format compliance
- **Integration**: Direct usage with Galacticus simulations and other astrophysical codes

## Galacticus Format Specification

The repository uses the standard Galacticus SHMR format with:

### File Structure
- **Top-level attributes**: `haloMassDefinition`, `label`, `reference`
- **Cosmology group**: Contains `OmegaMatter`, `OmegaDarkEnergy`, `OmegaBaryon`, `HubbleConstant`
- **Redshift interval groups**: `redshiftInterval0`, `redshiftInterval1`, etc.

### Each Redshift Interval Contains
- **Datasets**: `massHalo`, `massStellar`, `massStellarError`, `massStellarScatter`, `massStellarScatterError`
- **Attributes**: `redshiftMinimum`, `redshiftMaximum`
- **Dataset attributes**: `description` and `unitsInSI` (conversion factors to SI units)

### Supported Halo Mass Definitions
- `"virial"` or `"spherical collapse"`
- `"Bryan & Norman (1998)"`
- `"200 * critical density"`, `"500 * critical density"`, etc.
- `"200 * mean density"`, `"500 * mean density"`, etc.

## Repository Structure

```
├── data/                     # SHMR datasets organized by source type
│   ├── observations/         # Observational datasets (abundance matching, etc.)
│   ├── simulations/          # Results from cosmological simulations
│   └── theory/              # Theoretical/parametric models
├── scripts/                  # Data collection and processing scripts
│   ├── download_template.py  # Template for downloading data
│   ├── calculate_template.py # Template for calculating SHMRs
│   └── validate.py          # Galacticus format validation script
├── notebooks/               # Jupyter notebooks for documentation and examples
├── docs/                    # Documentation and specifications
├── src/shmr_datasets/       # Python package for SHMR data handling
└── tests/                   # Test suite
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Andrew-Robertson/make-SHMR-datasets.git
cd make-SHMR-datasets

# Install the package (development mode)
pip install -e .
```

### Basic Usage

```python
from shmr_datasets import (
    load_galacticus_shmr, 
    calculate_shmr, 
    save_galacticus_shmr,
    create_example_cosmology
)
import numpy as np

# Load an existing Galacticus-format dataset
shmr_data = load_galacticus_shmr("data/theory/behroozi2013/behroozi2013_z0_galacticus.hdf5")

# Access data
interval = shmr_data.redshift_intervals[0]  # First redshift interval
halo_masses = interval.massHalo
stellar_masses = interval.massStellar
print(f"Reference: {shmr_data.reference}")
print(f"Label: {shmr_data.label}")
print(f"Halo mass definition: {shmr_data.haloMassDefinition}")

# Calculate a theoretical SHMR
halo_masses = np.logspace(10, 15, 100)
calculated_shmr = calculate_shmr(
    halo_masses=halo_masses,
    shmr_function="behroozi2013",
    parameters={"log_m1": 12.35, "ms0": 10.72, "beta": 0.44, "delta": 0.57, "gamma": 1.56},
    redshift=0.0,
    cosmology=create_example_cosmology(),
    halo_mass_definition="virial",
    label="Behroozi2013",
    reference="Behroozi et al. (2013)"
)

# Save in Galacticus format
save_galacticus_shmr(calculated_shmr, "my_shmr.hdf5")
```

### Using with Galacticus

Once you have a properly formatted HDF5 file, you can use it directly in Galacticus:

```xml
<stellarHaloMassRelation value="file">
  <fileName value="path/to/your/shmr_file.hdf5"/>
</stellarHaloMassRelation>
```

Galacticus will automatically read the cosmology, halo mass definition, and redshift intervals, applying appropriate conversions as needed.
```

### Validation

Always validate your datasets:

```bash
python scripts/validate.py data/my_new_dataset/
```

## Examples

See the [notebooks/](notebooks/) directory for detailed examples:

- [data_provenance_example.ipynb](notebooks/data_provenance_example.ipynb): Complete workflow for creating and documenting datasets

## Supported SHMR Models

The package includes implementations of several common SHMR parametrizations:

- **Behroozi et al. 2010**: Original abundance matching relation (arXiv:1001.0015)
- **Behroozi et al. 2013**: Updated abundance matching relation
- **Moster et al. 2013**: Alternative abundance matching form  
- **Rodriguez-Puebla et al. 2017**: Updated abundance matching
- **Double Power Law**: Simple parametric form
- **Custom Functions**: Support for user-defined functions

## Example Datasets

The repository includes validated example datasets:

- **Behroozi et al. 2010**: `data/theory/behroozi2010/behroozi2010_parametric.hdf5` (parametric model)
- **Behroozi et al. 2013**: `data/theory/behroozi2013/behroozi2013_z0_galacticus.hdf5`
- **Moster et al. 2013**: `data/theory/moster2013/moster2013_z0_galacticus.hdf5`
- **UniverseMachine**: `data/simulations/universemachine/universemachine_downloaded.hdf5` (downloaded data)

All datasets pass Galacticus format validation and can be used directly in simulations.

## Contributing

Contributions are welcome! Please:

1. **Follow the Galacticus format specification**
2. **Include complete metadata and provenance**
3. **Add validation and documentation**
4. **Submit datasets with reproducible creation scripts**

### Adding New Datasets

1. Create appropriate directory structure under `data/`
2. Include creation script in `scripts/`
3. Add documentation (README, notebook if appropriate)
4. Validate the dataset with `scripts/validate.py`
5. Submit via pull request

### Code Contributions

1. Add tests for new functionality
2. Update documentation
3. Follow existing code style
4. Ensure all tests pass

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=shmr_datasets

# Run specific test
pytest tests/test_basic.py -v
```

## Requirements

- Python ≥ 3.8
- numpy
- scipy  
- astropy
- h5py
- pyyaml
- jsonschema
- matplotlib (optional, for plotting)

Development requirements:
- pytest
- pytest-cov
- black (code formatting)
- flake8 (linting)
- jupyter (for notebooks)

## License

MIT License - see [LICENSE](LICENSE) file.

## Citation

If you use datasets from this repository in your research, please cite:

1. **This repository**: Robertson, A. et al. "SHMR Datasets Repository" (GitHub)
2. **Original data sources**: Always cite the primary references for individual datasets
3. **Methodology papers**: Cite the papers describing the methods used to derive the SHMRs

## Support

- **Documentation**: See [docs/](docs/) directory
- **Examples**: See [notebooks/](notebooks/) directory  
- **Issues**: Report bugs or request features via GitHub issues
- **Discussions**: Use GitHub discussions for questions and suggestions

## Acknowledgments

This repository format is designed to support reproducible astrophysical research and facilitate comparison of stellar mass - halo mass relations across different studies and methodologies.
