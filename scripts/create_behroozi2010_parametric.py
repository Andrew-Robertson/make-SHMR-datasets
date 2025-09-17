#!/usr/bin/env python3
"""
Script to create Behroozi et al. 2010 SHMR dataset in Galacticus format.

This script creates an SHMR dataset using the parametric model from:
Behroozi et al. 2010, ApJ, 717, 379 (arXiv:1001.0015)

This serves as an example of creating datasets from theoretical/parametric models.
"""

import sys
import numpy as np
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from shmr_datasets import (
    calculate_shmr, 
    save_galacticus_shmr, 
    GalacticusCosmology,
    RedshiftInterval,
    GalacticusSHMRData
)


def create_behroozi2010_cosmology():
    """Create cosmology consistent with Behroozi et al. 2010."""
    return GalacticusCosmology(
        OmegaMatter=0.279,      # From WMAP7 used in Behroozi+ 2010
        OmegaDarkEnergy=0.721,  # 1 - Ω_M
        OmegaBaryon=0.0469,     # WMAP7 baryon density
        HubbleConstant=70.0     # km/s/Mpc, WMAP7
    )


def create_behroozi2010_shmr():
    """
    Create SHMR dataset using Behroozi et al. 2010 parametrization.
    
    This implements the abundance matching relation from:
    Behroozi et al. 2010, ApJ, 717, 379 (arXiv:1001.0015)
    
    The model includes multiple redshift intervals to match the structure
    of the example file provided.
    """
    
    # Define halo mass range (similar to example file)
    log_mh_min, log_mh_max = 10.5, 15.0
    n_points = 51  # Match the example file
    
    halo_masses = np.logspace(log_mh_min, log_mh_max, n_points)
    
    # Create redshift intervals matching the example structure
    redshift_intervals = []
    
    # Define redshift bins and corresponding parameters
    z_bins = [
        (0.0, 0.333),      # z=0.0-0.33
        (0.333, 0.667),    # z=0.33-0.67  
        (0.667, 1.0)       # z=0.67-1.0
    ]
    
    # Behroozi+ 2010 parameters for different redshifts
    # Parameters evolved with redshift according to their fitting formulae
    param_sets = [
        # z~0.17 (midpoint of first bin)
        {"log_m1": 11.88, "ms0": 10.21, "beta": 0.48, "delta": 0.15, "gamma": 2.51},
        # z~0.5 (midpoint of second bin) 
        {"log_m1": 11.95, "ms0": 10.35, "beta": 0.50, "delta": 0.12, "gamma": 2.8},
        # z~0.83 (midpoint of third bin)
        {"log_m1": 12.05, "ms0": 10.55, "beta": 0.53, "delta": 0.10, "gamma": 3.2}
    ]
    
    for i, ((z_min, z_max), params) in enumerate(zip(z_bins, param_sets)):
        print(f"Creating redshift interval {i+1}: z={z_min:.3f}-{z_max:.3f}")
        
        # Calculate stellar masses using Behroozi 2010 model
        stellar_masses = calculate_shmr(
            halo_masses=halo_masses,
            shmr_function="behroozi2010",
            parameters=params,
            redshift=(z_min + z_max) / 2,
            redshift_width=z_max - z_min,
            cosmology=create_behroozi2010_cosmology(),
            halo_mass_definition="Bryan & Norman (1998)",
            label="Behroozi2010",
            reference="Behroozi et al. (2010)"
        ).redshift_intervals[0]  # Get the single interval
        
        # Create redshift interval with proper bounds
        interval = RedshiftInterval(
            massHalo=stellar_masses.massHalo,
            massStellar=stellar_masses.massStellar,
            massStellarError=stellar_masses.massStellarError,
            massStellarScatter=stellar_masses.massStellarScatter,
            massStellarScatterError=stellar_masses.massStellarScatterError,
            redshiftMinimum=z_min,
            redshiftMaximum=z_max
        )
        
        redshift_intervals.append(interval)
    
    # Create the complete dataset
    shmr_dataset = GalacticusSHMRData(
        redshift_intervals=redshift_intervals,
        cosmology=create_behroozi2010_cosmology(),
        haloMassDefinition="Bryan & Norman (1998)",
        label="Behroozi2010",
        reference="Behroozi et al. (2010)"
    )
    
    return shmr_dataset


def main():
    """Main function to create and save the dataset."""
    print("Creating Behroozi et al. 2010 SHMR dataset...")
    print("=" * 50)
    
    # Create the dataset
    shmr_data = create_behroozi2010_shmr()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / "theory" / "behroozi2010"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the dataset
    output_file = output_dir / "behroozi2010_parametric.h5"
    save_galacticus_shmr(shmr_data, output_file)
    
    print(f"\nDataset saved to: {output_file}")
    print(f"Number of redshift intervals: {shmr_data.n_redshift_intervals}")
    print(f"Total data points: {shmr_data.total_data_points}")
    print(f"Redshift range: {shmr_data.redshift_range[0]:.3f} - {shmr_data.redshift_range[1]:.3f}")
    
    # Validate the created file
    print("\nValidating created dataset...")
    import subprocess
    result = subprocess.run([
        sys.executable, 
        str(Path(__file__).parent / "validate.py"), 
        str(output_file)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Validation successful!")
    else:
        print("❌ Validation failed:")
        print(result.stdout)
        print(result.stderr)
    
    print(f"\nTo use this dataset in Galacticus, add to your parameter file:")
    print(f'<stellarHaloMassRelation value="file">')
    print(f'  <fileName value="{output_file}"/>')
    print(f'</stellarHaloMassRelation>')


if __name__ == "__main__":
    main()