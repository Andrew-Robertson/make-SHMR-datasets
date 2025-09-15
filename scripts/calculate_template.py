#!/usr/bin/env python3
"""
Template script for calculating SHMR from theoretical models.

This script provides a template for creating SHMR datasets from 
parametric models described in the literature.
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from shmr_datasets import SHMRData, SHMRMetadata, save_shmr, calculate_shmr


def create_behroozi2013_shmr():
    """
    Create SHMR dataset using Behroozi et al. 2013 parametrization.
    
    This implements the abundance matching relation from:
    Behroozi, Wechsler & Conroy 2013, ApJ, 770, 57
    """
    
    # Define halo mass range
    log_mh_min, log_mh_max = 10.0, 15.0
    n_points = 100
    
    halo_masses = np.logspace(log_mh_min, log_mh_max, n_points)
    
    # Behroozi et al. 2013 parameters at z=0 for central galaxies
    parameters = {
        "log_m1": 12.35,    # Characteristic halo mass
        "ms0": 10.72,       # Normalization
        "beta": 0.44,       # Low-mass slope
        "delta": 0.57,      # High-mass slope  
        "gamma": 1.56       # Turnover sharpness
    }
    
    # Create metadata
    metadata = SHMRMetadata(
        name="Behroozi et al. 2013 SHMR",
        version="1.0",
        description="Stellar mass - halo mass relation from abundance matching (Behroozi+ 2013)",
        source_type="observation",
        reference="Behroozi, P. S., Wechsler, R. H., & Conroy, C. 2013, ApJ, 770, 57",
        doi="10.1088/0004-637X/770/1/57",
        creation_method="calculation",
        creation_date=datetime.now().strftime("%Y-%m-%d"),
        created_by="SHMR Datasets Repository",
        redshift=0.0,
        stellar_mass_definition="total stellar mass",
        halo_mass_definition="M200c",
        cosmology={
            "h": 0.7,
            "omega_m": 0.27,
            "omega_lambda": 0.73,
            "sigma_8": 0.82
        },
        mass_range={
            "halo_mass_min": 10**log_mh_min,
            "halo_mass_max": 10**log_mh_max
        },
        uncertainties_included=False,
        limitations="Applies to central galaxies only at z=0",
        tags=["abundance_matching", "central_galaxies", "z0", "behroozi2013"],
        notes=f"Calculated using parameters: {parameters}"
    )
    
    # Calculate SHMR
    shmr_data = calculate_shmr(
        halo_masses=halo_masses,
        shmr_function="behroozi2013",
        parameters=parameters,
        **metadata.__dict__
    )
    
    return shmr_data


def create_moster2013_shmr():
    """
    Create SHMR dataset using Moster et al. 2013 parametrization.
    
    This implements the abundance matching relation from:
    Moster, Naab & White 2013, MNRAS, 428, 3121
    """
    
    # Define halo mass range
    log_mh_min, log_mh_max = 10.0, 15.0
    n_points = 100
    
    halo_masses = np.logspace(log_mh_min, log_mh_max, n_points)
    
    # Moster et al. 2013 parameters at z=0
    parameters = {
        "m1": 1.87e12,      # Characteristic halo mass
        "n10": 0.0351,      # Normalization  
        "beta": 1.376,      # Low-mass slope
        "gamma": 0.608      # High-mass slope
    }
    
    # Create metadata
    metadata = SHMRMetadata(
        name="Moster et al. 2013 SHMR",
        version="1.0", 
        description="Stellar mass - halo mass relation from abundance matching (Moster+ 2013)",
        source_type="observation",
        reference="Moster, B. P., Naab, T., & White, S. D. M. 2013, MNRAS, 428, 3121",
        doi="10.1093/mnras/sts261",
        creation_method="calculation",
        creation_date=datetime.now().strftime("%Y-%m-%d"),
        created_by="SHMR Datasets Repository",
        redshift=0.0,
        stellar_mass_definition="total stellar mass",
        halo_mass_definition="M200c",
        cosmology={
            "h": 0.7,
            "omega_m": 0.27,
            "omega_lambda": 0.73
        },
        mass_range={
            "halo_mass_min": 10**log_mh_min,
            "halo_mass_max": 10**log_mh_max
        },
        uncertainties_included=False,
        limitations="Applies to central galaxies only at z=0",
        tags=["abundance_matching", "central_galaxies", "z0", "moster2013"],
        notes=f"Calculated using parameters: {parameters}"
    )
    
    # Calculate SHMR
    shmr_data = calculate_shmr(
        halo_masses=halo_masses,
        shmr_function="moster2013",
        parameters=parameters,
        **metadata.__dict__
    )
    
    return shmr_data


def save_dataset(shmr_data, output_dir, filename_base):
    """Save SHMR dataset in multiple formats."""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as HDF5
    h5_file = output_dir / f"{filename_base}.h5"
    save_shmr(shmr_data, h5_file, format="hdf5")
    print(f"Saved HDF5 file: {h5_file}")
    
    # Save as YAML  
    yaml_file = output_dir / f"{filename_base}.yaml"
    save_shmr(shmr_data, yaml_file, format="yaml")
    print(f"Saved YAML file: {yaml_file}")
    
    return output_dir


def main():
    """Main function to calculate and save SHMR datasets."""
    
    print("SHMR Calculation Script")
    print("=" * 40)
    
    # Create Behroozi et al. 2013 SHMR
    print("\nCalculating Behroozi et al. 2013 SHMR...")
    behroozi_data = create_behroozi2013_shmr()
    behroozi_dir = save_dataset(
        behroozi_data,
        "../data/theory/behroozi2013",
        "behroozi2013_z0_central"
    )
    
    # Create Moster et al. 2013 SHMR
    print("\nCalculating Moster et al. 2013 SHMR...")
    moster_data = create_moster2013_shmr()
    moster_dir = save_dataset(
        moster_data,
        "../data/theory/moster2013", 
        "moster2013_z0_central"
    )
    
    # Create comparison plot (optional)
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        plt.loglog(behroozi_data.halo_mass, behroozi_data.stellar_mass, 
                   'b-', label='Behroozi+ 2013', linewidth=2)
        plt.loglog(moster_data.halo_mass, moster_data.stellar_mass,
                   'r--', label='Moster+ 2013', linewidth=2)
        
        plt.xlabel('Halo Mass [M☉]')
        plt.ylabel('Stellar Mass [M☉]') 
        plt.title('SHMR Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plot_file = Path("../data/shmr_comparison.png")
        plt.savefig(plot_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"\nCreated comparison plot: {plot_file}")
        
    except ImportError:
        print("\nMatplotlib not available - skipping comparison plot")
    
    print(f"\nCalculation completed successfully!")
    print(f"Datasets saved in:")
    print(f"  - {behroozi_dir}")
    print(f"  - {moster_dir}")


if __name__ == "__main__":
    main()