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


def load_trinity_data(filepath):
    """
    Load TRINITY black hole - halo mass relation data from file.
    
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
    data = np.loadtxt(filepath, comments='#')
    
    # Columns: z_min, z_max, log10(Mpeak[Msun]), log10(Mbh[Msun]), log10(Mbh/Mpeak), sigma_log10_Mbh
    z_min = data[:, 0]
    z_max = data[:, 1]
    log_halo_mass = data[:, 2]
    log_bh_mass = data[:, 3]
    sigma_log_bh = data[:, 5]
    
    # Convert log masses to linear masses
    halo_mass = 10**log_halo_mass
    bh_mass = 10**log_bh_mass
    
    # Group data by redshift interval
    redshift_data = defaultdict(lambda: {'halo_masses': [], 'bh_masses': [], 'sigma': []})
    
    for i in range(len(data)):
        key = (z_min[i], z_max[i])
        redshift_data[key]['halo_masses'].append(halo_mass[i])
        redshift_data[key]['bh_masses'].append(bh_mass[i])
        redshift_data[key]['sigma'].append(sigma_log_bh[i])
    
    # Convert lists to arrays
    for key in redshift_data:
        redshift_data[key]['halo_masses'] = np.array(redshift_data[key]['halo_masses'])
        redshift_data[key]['bh_masses'] = np.array(redshift_data[key]['bh_masses'])
        redshift_data[key]['sigma'] = np.array(redshift_data[key]['sigma'])
    
    return redshift_data


def create_trinity_bhmr():
    """
    Create BHMR dataset using TRINITY data.
    
    This implements the black hole - halo mass relation from:
    Zhang et al. 2022, MNRAS, 518, 2123 (arXiv:2208.00719)
    
    The model includes multiple redshift intervals from z=0 to z=10.
    """
    
    # Load TRINITY data
    data_dir = Path(__file__).parent.parent / "data" / "observations" / "trinity"
    data_file = data_dir / "fig14_median_BHHM_fit_z0-10.txt"
    
    print(f"Loading TRINITY data from: {data_file}")
    redshift_data = load_trinity_data(data_file)
    
    # Create redshift intervals
    redshift_intervals = []
    
    # Sort by redshift minimum
    sorted_keys = sorted(redshift_data.keys(), key=lambda x: x[0])
    
    for i, (z_min, z_max) in enumerate(sorted_keys):
        data = redshift_data[(z_min, z_max)]
        
        print(f"Creating redshift interval {i+1}: z={z_min:.1f}-{z_max:.1f}, "
              f"{len(data['halo_masses'])} points")
        
        # For TRINITY, we assume:
        # - Error in black hole mass is ~0.3 dex (typical uncertainty)
        # - Scatter is provided in the data
        # - Error in scatter is ~0.1 dex (typical)
        
        bh_mass_error = 0.3 * np.log(10) * data['bh_masses']  # Convert dex to linear
        scatter_error = np.full_like(data['sigma'], 0.1)  # 0.1 dex uncertainty in scatter
        
        interval = BlackHoleRedshiftInterval(
            massHalo=data['halo_masses'],
            massBlackHole=data['bh_masses'],
            massBlackHoleError=bh_mass_error,
            massBlackHoleScatter=data['sigma'],
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
        reference="Zhang et al. (2022)"
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
    print(f"- Note: This uses the median black hole mass - peak halo mass relation")


if __name__ == "__main__":
    main()
