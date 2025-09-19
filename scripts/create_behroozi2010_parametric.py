#!/usr/bin/env python3
"""
Script to create Behroozi et al. 2010 SHMR dataset in Galacticus format.

This script creates an SHMR dataset using the parametric model from:
Behroozi et al. 2010, ApJ, 717, 379 (arXiv:1001.0015)

This serves as an example of creating datasets from theoretical/parametric models.
"""

import numpy as np
from pathlib import Path

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
    
    # Define halo mass range and bins
    halo_masses = np.logspace(9.95, 15.05, 251) 
    Nzbin = 40
    zbin_edges = np.linspace(0,4,Nzbin+1)   
    z_bins = [(zbin_edges[i],zbin_edges[i+1]) for i in np.arange(Nzbin)]
     # Create redshift intervals
    redshift_intervals = []
    
    
    for i, (z_min, z_max) in enumerate(z_bins):
        print(f"Creating redshift interval {i+1}: z={z_min:.3f}-{z_max:.3f}")
        
        # Calculate stellar masses using Behroozi 2010 model
        stellar_masses = calculate_shmr(
            halo_masses=halo_masses,
            shmr_function="behroozi2010",
            parameters=None, # Use default Behroozi2010 parameters
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
    output_file = output_dir / "behroozi2010_parametric.hdf5"
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