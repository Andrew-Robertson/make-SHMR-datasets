#!/usr/bin/env python3
"""
Script to create van der Wel et al. 2014 stellar mass-size dataset in Galacticus format.

This script creates a mass-size relation dataset from:
van der Wel et al. 2014, ApJ, 788, 28 (https://iopscience.iop.org/article/10.1088/0004-637X/788/1/28)

The data is from Table 2 of the paper, which provides the logarithmic size distribution
as a function of galaxy mass and redshift for both early-type (quiescent) and 
late-type (star forming) galaxies.
"""

import numpy as np
import sys
from pathlib import Path
from datetime import datetime

from shmr_datasets import (
    GalacticusMassSizeData,
    MassSizeSample,
    GalacticusCosmology,
    save_galacticus_mass_size,
    validate_galacticus_mass_size_file,
    print_galacticus_mass_size_file_info
)
from shmr_datasets.utils import speagle14_log_sfr_ms

# Default scatter values from literature
# These are typical values for the intrinsic scatter in the mass-size relation
DEFAULT_RADIUS_SCATTER_DEX = 0.15  # Intrinsic scatter in dex
DEFAULT_RADIUS_SCATTER_ERROR_DEX = 0.03  # Uncertainty in scatter measurement
DEFAULT_RADIUS_ERROR_DEX = 0.01

# Main sequence offset for quiescent classification
# Galaxies below this offset from the main sequence are considered quiescent
DEFAULT_MAIN_SEQUENCE_OFFSET_DEX = 1.0  # 1.0 dex below main sequence


def create_vanderwel2014_cosmology():
    """Create cosmology consistent with van der Wel et al. 2014."""
    # They used WMAP7 cosmology (from paper)
    return GalacticusCosmology(
        OmegaMatter=0.272,
        OmegaDarkEnergy=0.728,
        OmegaBaryon=0.0456,
        HubbleConstant=70.4  # km/s/Mpc
    )


def parse_vanderwel2014_data():
    """
    Parse van der Wel et al. 2014 Table 2 data.
    
    Returns data from Table 2 of van der Wel et al. 2014.
    The table provides logarithmic effective radii (Re/kpc) at different
    mass bins and redshifts for both early-type (quiescent) and 
    late-type (star forming) galaxies.
    
    Returns
    -------
    dict
        Dictionary with keys:
        - 'redshift_bins': List of (z_min, z_max) tuples
        - 'mass_bins': Array of stellar mass bin centers (log10 M_sun)
        - 'late_type': Dict with 'Re' and 'Re_err' arrays for star forming
        - 'early_type': Dict with 'Re' and 'Re_err' arrays for quiescent
    """
    # Redshift bins from Table 2
    redshift_bins = [
        (0.0, 0.5),
        (0.5, 1.0),
        (1.0, 1.5),
        (1.5, 2.0),
        (2.0, 2.5),
        (2.5, 3.0),
    ]
    
    # Stellar mass bin centers (log10 M_sun)
    mass_bins = np.array([9.25, 9.75, 10.25, 10.75, 11.25])
    
    # Data from Table 2: log(Re/kpc) for late-type (star forming) galaxies
    # Data for late-type (star forming) galaxies, using NaN for missing data

    late_type_Re_16 = np.array([
        [0.24, 0.36, 0.42, 0.61, np.nan], 
        [0.18, 0.32, 0.39, 0.51, 0.77],
        [0.11, 0.23, 0.33, 0.47, 0.62],
        [0.07, 0.16, 0.28, 0.35, 0.53],
        [np.nan, 0.10, 0.17, 0.26, 0.40],
        [np.nan, np.nan, 0.16, 0.19, 0.33],
    ])

    late_type_Re_50 = np.array([
        [0.49, 0.61, 0.66, 0.83, np.nan], 
        [0.43, 0.56, 0.64, 0.75, 0.90],
        [0.37, 0.48, 0.57, 0.67, 0.82],
        [0.33, 0.42, 0.52, 0.61, 0.70],
        [np.nan, 0.35, 0.44, 0.53, 0.64],
        [np.nan, np.nan, 0.43, 0.47, 0.55],
    ])

    late_type_Re_84 = np.array([
        [0.70, 0.80, 0.85, 1.01, np.nan], 
        [0.65, 0.76, 0.83, 0.90, 1.12],
        [0.60, 0.69, 0.77, 0.83, 0.96],
        [0.57, 0.65, 0.72, 0.80, 0.87],
        [np.nan, 0.57, 0.64, 0.70, 0.84],
        [np.nan, np.nan, 0.65, 0.71, 0.76],
    ])

    
    # Data for early-type (quiescent) galaxies  

    early_type_Re_16 = np.array([
        [0.03, 0.04, 0.13, 0.42, 0.65], 
        [-0.02, -0.14, 0.02, 0.26, 0.62],
        [np.nan, -0.15, -0.15, 0.07, 0.41 ],
        [np.nan, -0.02, -0.27, -0.04, 0.28],
        [np.nan, np.nan, -0.37, -0.20, 0.16],
        [np.nan, np.nan, np.nan, -0.22, 0.07],
    ])

    early_type_Re_50 = np.array([
        [0.27, 0.28, 0.38, 0.67, 0.76], 
        [0.23, 0.21, 0.23, 0.45, 0.81],
        [np.nan, 0.18, 0.09, 0.30, 0.58],
        [np.nan, 0.22, 0.02, 0.19, 0.45],
        [np.nan, np.nan, -0.04, 0.08, 0.36],
        [np.nan, np.nan, np.nan, 0.10, 0.39],
    ])

    early_type_Re_84 = np.array([
        [0.46, 0.46, 0.58, 0.92, 1.08], 
        [0.43, 0.44, 0.42, 0.64, 0.97],
        [np.nan, 0.42, 0.36, 0.54, 0.81],
        [np.nan, 0.48, 0.35, 0.50, 0.74],
        [np.nan, np.nan,0.36, 0.54, 0.55],
        [np.nan, np.nan, np.nan, 0.50, 0.68],
    ])

    return {
        'redshift_bins': redshift_bins,
        'mass_bins': mass_bins,
        'late_type': {'Re': late_type_Re_50, 'Re_scatt': 0.5*(late_type_Re_84-late_type_Re_16)},
        'early_type': {'Re': early_type_Re_50, 'Re_scatt': 0.5*(early_type_Re_84-early_type_Re_16)},
    }


def create_vanderwel2014_mass_size():
    """
    Create mass-size relation dataset from van der Wel et al. 2014.
    
    Returns
    -------
    GalacticusMassSizeData
        The mass-size relation data in Galacticus format
    """
    data = parse_vanderwel2014_data()
    cosmology = create_vanderwel2014_cosmology()
    
    samples = []
    
    # Process each redshift bin
    for i_z, (z_min, z_max) in enumerate(data['redshift_bins']):
        z_center = (z_min + z_max) / 2
        
        # Get valid data for this redshift bin (both star forming and quiescent)
        late_Re = data['late_type']['Re'][i_z]
        late_Re_scatter = data['late_type']['Re_scatt'][i_z]
        early_Re = data['early_type']['Re'][i_z]
        early_Re_scatter = data['early_type']['Re_scatt'][i_z]
        
        # Process star forming (late-type) sample
        valid_late = ~np.isnan(late_Re)
        if np.any(valid_late):
            mass_stellar_late = 10**data['mass_bins'][valid_late]
            log_mass_late = data['mass_bins'][valid_late]
            
            # Convert log(Re/kpc) to Re in Mpc
            Re_late_mpc = 10**late_Re[valid_late] * 1e-3  # log10(r/kpc) to r/Mpc
            
            # Error propagation from logarithmic to linear space (using default relative error):
            # For R = 10^(log R), the error is: dR = R * ln(10) * d(log R)
            Re_late_err_mpc = Re_late_mpc * np.log(10) * DEFAULT_RADIUS_ERROR_DEX 
            
            # Calculate main sequence SFR at these masses using Speagle+14
            log_sfr_ms = speagle14_log_sfr_ms(log_mass_late, z=z_center, cosmology=cosmology)
            
            # Use default scatter values from module constants
            Re_scatter = late_Re_scatter[valid_late]
            Re_scatter_err = np.full(len(mass_stellar_late), DEFAULT_RADIUS_SCATTER_ERROR_DEX)
       
            sample_sf = MassSizeSample(
                massStellar=mass_stellar_late,
                radiusEffective=Re_late_mpc,
                radiusEffectiveError=Re_late_err_mpc,
                radiusEffectiveScatter=Re_scatter,
                radiusEffectiveScatterError=Re_scatter_err,
                redshiftMinimum=z_min,
                redshiftMaximum=z_max,
                selection='star forming',
                mainSequenceSFR=log_sfr_ms,
                offsetMainSequenceSFR=DEFAULT_MAIN_SEQUENCE_OFFSET_DEX
            )
            samples.append(sample_sf)
        
        # Process quiescent (early-type) sample
        valid_early = ~np.isnan(early_Re)
        if np.any(valid_early):
            mass_stellar_early = 10**data['mass_bins'][valid_early]
            log_mass_early = data['mass_bins'][valid_early]
            
            # Convert log(Re/kpc) to Re in Mpc
            Re_early_mpc = 10**early_Re[valid_early] * 1e-3
            
            # Error propagation from logarithmic to linear space:
            # For R = 10^(log R), the error is: dR = R * ln(10) * d(log R)
            Re_early_err_mpc = Re_early_mpc * np.log(10) * DEFAULT_RADIUS_ERROR_DEX 
            
            # Calculate main sequence SFR (even for quiescent, as reference)
            log_sfr_ms = speagle14_log_sfr_ms(log_mass_early, z=z_center, cosmology=cosmology)
            
            # Use default scatter values from module constants
            Re_scatter = early_Re_scatter[valid_early]
            Re_scatter_err = np.full(len(mass_stellar_early), DEFAULT_RADIUS_SCATTER_ERROR_DEX)
            
            sample_q = MassSizeSample(
                massStellar=mass_stellar_early,
                radiusEffective=Re_early_mpc,
                radiusEffectiveError=Re_early_err_mpc,
                radiusEffectiveScatter=Re_scatter,
                radiusEffectiveScatterError=Re_scatter_err,
                redshiftMinimum=z_min,
                redshiftMaximum=z_max,
                selection='quiescent',
                mainSequenceSFR=log_sfr_ms,
                offsetMainSequenceSFR=DEFAULT_MAIN_SEQUENCE_OFFSET_DEX
            )
            samples.append(sample_q)

    # Get current date
    creation_date = datetime.now().strftime("%Y-%m-%d")
    
    return GalacticusMassSizeData(
        samples=samples,
        cosmology=cosmology,
        label='vanDerWel2014',
        reference='van der Wel et al. (2014)',
        notes=(
            "Mass-size relations from van der Wel et al. 2014 (ApJ, 788, 28). "
            "Data extracted from Table 2, which provides log(Re/kpc) at different stellar masses and redshifts. "
            "12 samples: 6 redshift bins (z=0-3) × 2 selections (star forming + quiescent). "
            "The errors on mean sizes and scatter are not taken from the paper, but instead just use default values."
            "Cosmology: WMAP7 (though I could not find a statement of what they used/assumed in the paper)."
            "Star forming main sequence uses Speagle et al. 2014 parametrization. "
            f"Quiescent classification: {DEFAULT_MAIN_SEQUENCE_OFFSET_DEX} dex below main sequence. "
        ),
        creator="create_vanderwel2014_mass_size.py script",
        creationDate=creation_date
    )


def main():
    """Main function to create and save the dataset."""
    print("Creating van der Wel et al. 2014 mass-size relation dataset...")
    
    # Create the dataset
    mass_size_data = create_vanderwel2014_mass_size()
    
    # Output path
    output_dir = Path(__file__).parent.parent / 'data' / 'observations' / 'vanderwel2014'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'vanderwel2014_mass_size.hdf5'
    
    # Save the dataset
    print(f"Saving to {output_file}...")
    save_galacticus_mass_size(mass_size_data, output_file)
    
    # Validate the file
    print("\nValidating file...")
    validation = validate_galacticus_mass_size_file(output_file)
    
    if validation['valid']:
        print("✓ File validation passed!")
    else:
        print("✗ File validation failed:")
        for error in validation['errors']:
            print(f"  - {error}")
        sys.exit(1)
    
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # Print file info
    print("\n" + "="*60)
    print_galacticus_mass_size_file_info(output_file)
    print("="*60)
    
    print(f"\n✓ Successfully created {output_file}")
    print(f"\nDataset ready for use with Galacticus!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
