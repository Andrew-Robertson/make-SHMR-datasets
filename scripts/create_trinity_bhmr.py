#!/usr/bin/env python3
"""
Script to create TRINITY black hole mass - halo mass relation dataset in Galacticus format.

This script creates a BHMR dataset using data from the TRINITY project:
Zhang et al. 2022, MNRAS, 518, 2123 (arXiv:2208.00719)
https://github.com/HaowenZhang/TRINITY

This demonstrates creating datasets for black hole - halo mass relations.
"""

import numpy as np
import sys
from pathlib import Path
from collections import defaultdict
import urllib.request

from shmr_datasets import (
    save_galacticus_bhmr,
    GalacticusCosmology,
    BlackHoleRedshiftInterval,
    GalacticusBHMRData
)


def create_trinity_cosmology():
    """Create cosmology consistent with TRINITY (Planck 2018)."""
    return GalacticusCosmology(
        OmegaMatter=0.3111,      # Planck 2018
        OmegaDarkEnergy=0.6889,  # 1 - Ω_M
        OmegaBaryon=0.04897,     # Planck 2018 baryon density
        HubbleConstant=67.66     # km/s/Mpc, Planck 2018
    )


def download_trinity_data(output_path):
    """
    Download TRINITY data from GitHub repository.
    
    Parameters
    ----------
    output_path : Path
        Path where to save the downloaded data
        
    Returns
    -------
    Path
        Path to the downloaded file
    """
    url = "https://raw.githubusercontent.com/HaowenZhang/TRINITY/main/plot_data/Paper1/fig14_median_BHHM_z%3D0-10/fig14_median_BHHM_fit_z%3D0-10.dat"
    
    print(f"Downloading TRINITY data from: {url}")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"Successfully downloaded to: {output_path}")
        return output_path
    except Exception as e:
        raise RuntimeError(f"Failed to download TRINITY data: {e}")


def calculate_redshift_bins(redshifts):
    """
    Calculate redshift bin edges from discrete redshift values.
    
    For each redshift z, the bin covers the range where z is the closest output.
    E.g., for z=0.1, 1.0, 2.0, bins would be [0, 0.55], [0.55, 1.5], [1.5, ...]
    
    Parameters
    ----------
    redshifts : np.ndarray
        Array of unique redshift values
        
    Returns
    -------
    dict
        Dictionary mapping redshift to (z_min, z_max) tuple
    """
    z_sorted = np.sort(redshifts)
    z_bins = {}
    
    for i, z in enumerate(z_sorted):
        if i == 0:
            # First bin starts at 0
            z_min = 0.0
            z_max = (z + z_sorted[i+1]) / 2.0 if i+1 < len(z_sorted) else z + 0.5
        elif i == len(z_sorted) - 1:
            # Last bin extends beyond
            z_min = (z_sorted[i-1] + z) / 2.0
            z_max = z + 0.5
        else:
            # Middle bins
            z_min = (z_sorted[i-1] + z) / 2.0
            z_max = (z + z_sorted[i+1]) / 2.0
        
        z_bins[z] = (z_min, z_max)
    
    return z_bins


def load_trinity_data(filepath):
    """
    Load TRINITY black hole - halo mass relation data from file.
    
    The TRINITY data format has columns:
    z, log10(Mpeak)[Msun], log10(Mbh_median)[Msun], 
    log10(16-th percentile), log10(84-th percentile)
    
    Parameters
    ----------
    filepath : str or Path
        Path to the TRINITY data file
        
    Returns
    -------
    dict
        Dictionary with redshift intervals as keys and data arrays as values
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"TRINITY data file not found: {filepath}")
    
    # Read data file
    # Columns: z, log10(Mpeak[Msun]), log10(Mbh_median)[Msun], log10(16th percentile), log10(84th percentile)
    data = np.loadtxt(filepath, comments='#')
    
    z = data[:, 0]
    log_halo_mass = data[:, 1]
    log_bh_mass = data[:, 2]
    log_bh_mass_16 = data[:, 3]
    log_bh_mass_84 = data[:, 4]
    
    # Get unique redshifts and calculate bin edges
    unique_z = np.unique(z)
    z_bins = calculate_redshift_bins(unique_z)
    
    print(f"\nRedshift bins calculated:")
    for z_val in sorted(z_bins.keys()):
        z_min, z_max = z_bins[z_val]
        print(f"  z={z_val:.1f}: [{z_min:.2f}, {z_max:.2f}]")
    
    # Convert log masses to linear masses
    halo_mass = 10**log_halo_mass
    bh_mass = 10**log_bh_mass
    
    # Calculate error from 16th-84th percentile range (half the range)
    log_bh_mass_error = 0.5 * (log_bh_mass_84 - log_bh_mass_16)
    bh_mass_error = bh_mass * np.log(10) * log_bh_mass_error
    
    # Group data by redshift interval
    redshift_data = defaultdict(lambda: {
        'halo_masses': [], 
        'bh_masses': [], 
        'bh_mass_errors': []
    })
    
    for i in range(len(data)):
        z_val = z[i]
        z_min, z_max = z_bins[z_val]
        key = (z_min, z_max)
        
        redshift_data[key]['halo_masses'].append(halo_mass[i])
        redshift_data[key]['bh_masses'].append(bh_mass[i])
        redshift_data[key]['bh_mass_errors'].append(bh_mass_error[i])
    
    # Convert lists to arrays
    for key in redshift_data:
        redshift_data[key]['halo_masses'] = np.array(redshift_data[key]['halo_masses'])
        redshift_data[key]['bh_masses'] = np.array(redshift_data[key]['bh_masses'])
        redshift_data[key]['bh_mass_errors'] = np.array(redshift_data[key]['bh_mass_errors'])
    
    return redshift_data


def create_trinity_bhmr():
    """
    Create BHMR dataset using TRINITY data.
    
    This implements the black hole - halo mass relation from:
    Zhang et al. 2022, MNRAS, 518, 2123 (arXiv:2208.00719)
    
    The model includes multiple redshift intervals from z=0 to z=10.
    """
    
    # Download or load TRINITY data
    data_dir = Path(__file__).parent.parent / "data" / "observations" / "trinity"
    data_file = data_dir / "fig14_median_BHHM_fit_z0-10.dat"
    
    # Download if not present
    if not data_file.exists():
        print("TRINITY data not found locally. Downloading...")
        data_file = download_trinity_data(data_file)
    else:
        print(f"Using existing TRINITY data: {data_file}")
    
    redshift_data = load_trinity_data(data_file)
    
    # Create redshift intervals
    redshift_intervals = []
    
    # Sort by redshift minimum
    sorted_keys = sorted(redshift_data.keys(), key=lambda x: x[0])
    
    for i, (z_min, z_max) in enumerate(sorted_keys):
        data = redshift_data[(z_min, z_max)]
        
        print(f"Creating redshift interval {i+1}: z={z_min:.2f}-{z_max:.2f}, "
              f"{len(data['halo_masses'])} points")
        
        # Note: TRINITY data does not include scatter information
        # We use assumed values as per discussion:
        # - Scatter: 0.3 dex (typical for black hole-halo mass relations)
        # - Scatter error: 0.2 dex (uncertainty in scatter measurement)
        # - BH mass error: from 16th-84th percentile range in data
        
        n_points = len(data['halo_masses'])
        scatter = np.full(n_points, 0.3)  # Assumed scatter: 0.3 dex
        scatter_error = np.full(n_points, 0.2)  # Assumed scatter error: 0.2 dex
        
        interval = BlackHoleRedshiftInterval(
            massHalo=data['halo_masses'],
            massBlackHole=data['bh_masses'],
            massBlackHoleError=data['bh_mass_errors'],
            massBlackHoleScatter=scatter,
            massBlackHoleScatterError=scatter_error,
            redshiftMinimum=z_min,
            redshiftMaximum=z_max
        )
        
        redshift_intervals.append(interval)
    
    # Create the complete dataset
    bhmr_dataset = GalacticusBHMRData(
        redshift_intervals=redshift_intervals,
        cosmology=create_trinity_cosmology(),
        haloMassDefinition="virial",  # TRINITY uses virial masses (peak halo mass)
        label="TRINITY",
        reference="Zhang et al. (2022)",
        notes="Zhang et al. (2022) do not advocate for the massBlackHoleScatter and massBlackHoleScatterError values that are listed in this file, which we arbitrarily set to 0.3 +/- 0.2 dex"
    )
    
    return bhmr_dataset


def main():
    """Main function to create and save the dataset."""
    print("Creating TRINITY Black Hole Mass - Halo Mass Relation dataset...")
    print("=" * 70)
    print("Source: https://github.com/HaowenZhang/TRINITY")
    print("Paper: Zhang et al. 2022, MNRAS, 518, 2123 (arXiv:2208.00719)")
    print()
    
    # Create the dataset
    bhmr_data = create_trinity_bhmr()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / "observations" / "trinity"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the dataset
    output_file = output_dir / "trinity_bhmr.hdf5"
    save_galacticus_bhmr(bhmr_data, output_file)
    
    print(f"\nDataset saved to: {output_file}")
    print(f"Number of redshift intervals: {bhmr_data.n_redshift_intervals}")
    print(f"Total data points: {bhmr_data.total_data_points}")
    print(f"Redshift range: {bhmr_data.redshift_range[0]:.1f} - {bhmr_data.redshift_range[1]:.1f}")
    
    # Validate the created file
    print("\nValidating created dataset...")
    from shmr_datasets import validate_galacticus_bhmr_file
    
    results = validate_galacticus_bhmr_file(output_file)
    
    if results['valid']:
        print("✅ Validation successful!")
    else:
        print("❌ Validation failed:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['warnings']:
        print("\n⚠️  Warnings:")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    print(f"\nTo use this dataset in Galacticus, add to your parameter file:")
    print(f'<blackHoleVsHaloMassRelation value="file">')
    print(f'  <fileNameTarget value="{output_file}"/>')
    print(f'</blackHoleVsHaloMassRelation>')
    
    print(f"\nData provenance:")
    print(f"- Source: TRINITY project")
    print(f"- Repository: https://github.com/HaowenZhang/TRINITY")
    print(f"- Paper: Zhang et al. 2022, MNRAS, 518, 2123")
    print(f"- Method: Semi-empirical modeling of galaxy-halo-black hole connection")
    print(f"- Cosmology: Planck 2018")
    print(f"\nData processing notes:")
    print(f"- Black hole masses: Median values from TRINITY model")
    print(f"- BH mass errors: Half the 16th-84th percentile range from TRINITY")
    print(f"- Scatter: Assumed value of 0.3 dex (TRINITY does not provide scatter)")
    print(f"- Scatter error: Assumed value of 0.2 dex")
    print(f"- Redshift bins: Calculated to cover ranges where each z is closest output")


if __name__ == "__main__":
    main()
