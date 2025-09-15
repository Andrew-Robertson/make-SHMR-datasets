# SHMR Datasets Repository

A repository for storing and managing stellar mass - halo mass relations (SHMRs) with complete data provenance and compatibility with astrophysical simulation codes like Galacticus.

## Overview

This repository provides a standardized framework for:

- **Data Storage**: Standardized formats for SHMR datasets with comprehensive metadata
- **Data Provenance**: Complete documentation of data sources, processing methods, and limitations  
- **Reproducibility**: Scripts and notebooks documenting how datasets were created or downloaded
- **Validation**: Tools to ensure data quality and format compliance
- **Integration**: Easy integration with simulation codes and analysis pipelines

## Repository Structure

```
├── data/                     # SHMR datasets organized by source type
│   ├── observations/         # Observational datasets (abundance matching, etc.)
│   ├── simulations/          # Results from cosmological simulations
│   └── theory/              # Theoretical/parametric models
├── scripts/                  # Data collection and processing scripts
│   ├── download_template.py  # Template for downloading data
│   ├── calculate_template.py # Template for calculating SHMRs
│   └── validate.py          # Data validation script
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

# Or install dependencies only
pip install -r requirements.txt
```

### Basic Usage

```python
from shmr_datasets import load_shmr, calculate_shmr, save_shmr

# Load an existing dataset
shmr_data = load_shmr("data/theory/behroozi2013/behroozi2013_z0_central.h5")

# Access data
halo_masses = shmr_data.halo_mass
stellar_masses = shmr_data.stellar_mass
print(f"Reference: {shmr_data.metadata.reference}")

# Calculate a theoretical SHMR
import numpy as np
halo_masses = np.logspace(10, 15, 100)
calculated_shmr = calculate_shmr(
    halo_masses=halo_masses,
    shmr_function="behroozi2013",
    parameters={"log_m1": 12.35, "ms0": 10.72, "beta": 0.44, "delta": 0.57, "gamma": 1.56},
    name="My Behroozi SHMR",
    reference="Behroozi+ 2013",
    creation_date="2024-01-15",
    created_by="Your Name"
)

# Save the dataset
save_shmr(calculated_shmr, "my_shmr.h5")
```

## Data Format

The repository uses a standardized format that includes:

### Data Arrays
- `halo_mass`: Halo masses (with units specified in metadata)
- `stellar_mass`: Corresponding stellar masses
- Optional uncertainty arrays for both quantities
- Additional data fields as needed

### Metadata Fields
- **Identification**: name, version, description
- **Provenance**: source type, reference, DOI, creation method
- **Physical Parameters**: redshift, mass definitions, cosmology
- **Quality Information**: uncertainties, limitations, systematic errors

### Supported Formats
- **HDF5** (`.h5`): Binary format with compression, best for large datasets
- **YAML** (`.yaml`): Human-readable format, good for small datasets and documentation
- **JSON** (`.json`): Web-compatible format

See [docs/data_format.md](docs/data_format.md) for complete specification.

## Creating New Datasets

### From Downloaded Data

Use the download template to create reproducible data collection workflows:

```bash
cp scripts/download_template.py scripts/download_my_data.py
# Edit the script to download and process your specific dataset
python scripts/download_my_data.py
```

### From Theoretical Models

Use the calculation template to create datasets from parametric models:

```bash
cp scripts/calculate_template.py scripts/calculate_my_model.py
# Edit the script to implement your specific SHMR model
python scripts/calculate_my_model.py
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

- **Behroozi et al. 2013**: Abundance matching relation
- **Moster et al. 2013**: Alternative abundance matching form  
- **Rodriguez-Puebla et al. 2017**: Updated abundance matching
- **Double Power Law**: Simple parametric form
- **Custom Functions**: Support for user-defined functions

## Integration with Galacticus

The data format is designed to be easily convertible to Galacticus input formats:

```python
# Load SHMR data
shmr_data = load_shmr("my_dataset.h5")

# Convert for Galacticus (example workflow)
# Implementation depends on specific Galacticus requirements
galacticus_data = convert_to_galacticus_format(shmr_data)
```

## Contributing

Contributions are welcome! Please:

1. **Follow the data format specification**
2. **Include complete metadata and provenance**
3. **Add validation and documentation**
4. **Submit datasets with reproducible creation scripts**

### Adding New Datasets

1. Create appropriate directory structure under `data/`
2. Include creation script in `scripts/`
3. Add documentation (README, notebook if appropriate)
4. Validate the dataset
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
