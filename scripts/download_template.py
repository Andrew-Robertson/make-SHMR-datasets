#!/usr/bin/env python3
"""
Template script for downloading SHMR data from online sources.

This script provides a template for creating reproducible data download
workflows with complete provenance tracking.
"""

import os
import sys
import requests
import numpy as np
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from shmr_datasets import SHMRData, SHMRMetadata, save_shmr


def download_example_data():
    """
    Download example SHMR data from a hypothetical online source.
    
    This is a template - replace with actual data source URLs and
    parsing logic for real datasets.
    """
    
    # Example URL (replace with actual data source)
    data_url = "https://example.com/shmr_data.txt"
    
    print(f"Downloading data from {data_url}")
    
    # For this template, we'll create synthetic data
    # In a real script, you would download and parse actual data
    halo_masses = np.logspace(10, 15, 50)  # 10^10 to 10^15 Msun
    stellar_masses = 1e9 * (halo_masses / 1e12)**0.8  # Simple power law
    
    # Add some realistic uncertainties
    stellar_mass_errors = 0.2 * stellar_masses  # 20% uncertainties
    
    return halo_masses, stellar_masses, stellar_mass_errors


def create_metadata():
    """Create metadata for the downloaded dataset."""
    
    metadata = SHMRMetadata(
        name="Example Downloaded SHMR",
        version="1.0",
        description="Example SHMR dataset downloaded from online source",
        source_type="observation",
        reference="Smith et al. 2024, ApJ, 999, 123",
        doi="10.3847/1538-4357/example",
        url="https://example.com/shmr_data.txt",
        creation_method="download",
        creation_date=datetime.now().strftime("%Y-%m-%d"),
        created_by="Your Name",
        redshift=0.0,
        stellar_mass_definition="total stellar mass within R90",
        halo_mass_definition="M200c",
        cosmology={
            "h": 0.7,
            "omega_m": 0.3,
            "omega_lambda": 0.7,
            "sigma_8": 0.8
        },
        mass_range={
            "halo_mass_min": 1e10,
            "halo_mass_max": 1e15,
            "stellar_mass_min": 1e7,
            "stellar_mass_max": 1e12
        },
        uncertainties_included=True,
        systematic_errors="Includes observational uncertainties and scatter",
        limitations="Limited to central galaxies at z=0",
        tags=["central_galaxies", "z0", "observations"],
        notes="Downloaded from public data release. See reference for details."
    )
    
    return metadata


def main():
    """Main function to download and save SHMR data."""
    
    print("SHMR Data Download Script")
    print("=" * 40)
    
    # Create output directory
    output_dir = Path("../data/observations/example_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download data
        halo_masses, stellar_masses, stellar_mass_errors = download_example_data()
        print(f"Downloaded {len(halo_masses)} data points")
        
        # Create metadata
        metadata = create_metadata()
        
        # Create SHMR data object
        shmr_data = SHMRData(
            halo_mass=halo_masses,
            stellar_mass=stellar_masses,
            stellar_mass_err_lower=stellar_mass_errors,
            stellar_mass_err_upper=stellar_mass_errors,
            metadata=metadata
        )
        
        # Save in multiple formats
        base_filename = "example_shmr_z0"
        
        # Save as HDF5 (recommended for large datasets)
        h5_file = output_dir / f"{base_filename}.hdf5"
        save_shmr(shmr_data, h5_file, format="hdf5")
        print(f"Saved HDF5 file: {h5_file}")
        
        # Save as YAML (human-readable)
        yaml_file = output_dir / f"{base_filename}.yaml"
        save_shmr(shmr_data, yaml_file, format="yaml")
        print(f"Saved YAML file: {yaml_file}")
        
        # Create a README for the dataset
        readme_content = f"""# {metadata.name}

## Description
{metadata.description}

## Source Information
- **Reference**: {metadata.reference}
- **DOI**: {metadata.doi}
- **URL**: {metadata.url}
- **Downloaded**: {metadata.creation_date}

## Data Properties
- **Number of points**: {len(halo_masses)}
- **Halo mass range**: {metadata.mass_range['halo_mass_min']:.1e} - {metadata.mass_range['halo_mass_max']:.1e} Msun
- **Stellar mass range**: {metadata.mass_range['stellar_mass_min']:.1e} - {metadata.mass_range['stellar_mass_max']:.1e} Msun
- **Redshift**: {metadata.redshift}
- **Uncertainties included**: {metadata.uncertainties_included}

## Mass Definitions
- **Stellar mass**: {metadata.stellar_mass_definition}
- **Halo mass**: {metadata.halo_mass_definition}

## Cosmology
{chr(10).join([f"- **{k}**: {v}" for k, v in metadata.cosmology.items()])}

## Files
- `{base_filename}.hdf5`: HDF5 format (recommended for analysis)
- `{base_filename}.yaml`: YAML format (human-readable)

## Usage
```python
from shmr_datasets import load_shmr

# Load the data
shmr_data = load_shmr("{base_filename}.hdf5")

# Access data arrays
halo_mass = shmr_data.halo_mass
stellar_mass = shmr_data.stellar_mass

# Access metadata
print(shmr_data.metadata.reference)
```

## Notes
{metadata.notes}

## Limitations
{metadata.limitations}
"""
        
        readme_file = output_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        print(f"Created README: {readme_file}")
        
        print("\nDownload completed successfully!")
        print(f"Dataset saved in: {output_dir}")
        
    except Exception as e:
        print(f"Error during download: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()