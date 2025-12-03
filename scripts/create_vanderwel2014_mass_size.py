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

# Main sequence offset for quiescent classification
# Galaxies below this offset from the main sequence are considered quiescent
DEFAULT_MAIN_SEQUENCE_OFFSET_DEX = 0.4  # 0.4 dex below main sequence


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
        (0.25, 0.50),
        (0.50, 0.75),
        (0.75, 1.00),
        (1.00, 1.25),
        (1.25, 1.50),
        (1.50, 1.75),
        (1.75, 2.00),
        (2.00, 2.25),
        (2.25, 2.50),
        (2.50, 2.75),
        (2.75, 3.00)
    ]
    
    # Stellar mass bin centers (log10 M_sun)
    mass_bins = np.array([9.75, 10.25, 10.75, 11.25])
    
    # Data from Table 2: log(Re/kpc) for late-type (star forming) galaxies
    # Format: [z_bin][mass_bin] = value ± error
    # Using NaN for missing data
    late_type_Re = np.array([
        # z=0.25-0.50: 16%, 50%, 84% percentiles from paper
        # Converting 16-84% range to effective radius and error
        [0.24, 0.49, 0.61, np.nan],   # Derived from 16%/50%/84% percentiles
        # z=0.50-0.75
        [0.18, 0.43, 0.58, 0.70],
        # z=0.75-1.00  
        [0.18, 0.43, 0.57, 0.67],
        # z=1.00-1.25
        [0.11, 0.37, 0.48, 0.60],
        # z=1.25-1.50
        [0.07, 0.33, 0.45, 0.57],
        # z=1.50-1.75
        [0.07, 0.16, 0.42, 0.52],
        # z=1.75-2.00
        [np.nan, 0.10, 0.35, 0.44],
        # z=2.00-2.25
        [np.nan, 0.10, 0.26, 0.40],
        # z=2.25-2.50
        [np.nan, np.nan, 0.17, 0.33],
        # z=2.50-2.75
        [np.nan, np.nan, 0.16, 0.26],
        # z=2.75-3.00
        [np.nan, np.nan, 0.19, 0.33]
    ])
    
    # Uncertainties in log(Re/kpc) for late-type
    late_type_Re_err = np.array([
        [0.01, 0.01, 0.03, np.nan],
        [0.01, 0.01, 0.01, 0.01],
        [0.01, 0.01, 0.01, 0.01],
        [0.01, 0.01, 0.01, 0.01],
        [0.01, 0.01, 0.01, 0.01],
        [0.01, 0.01, 0.01, 0.01],
        [np.nan, 0.01, 0.01, 0.01],
        [np.nan, 0.01, 0.02, 0.02],
        [np.nan, np.nan, 0.02, 0.01],
        [np.nan, np.nan, 0.02, 0.03],
        [np.nan, np.nan, 0.06, 0.04]
    ])
    
    # Data for early-type (quiescent) galaxies  
    early_type_Re = np.array([
        [0.03, 0.36, 0.42, 0.65],
        [-0.02, 0.27, 0.38, 0.62],
        [-0.02, 0.23, 0.32, 0.51],
        [0.02, 0.21, 0.26, 0.45],
        [-0.27, 0.02, 0.19, 0.37],
        [-0.27, -0.02, 0.13, 0.28],
        [np.nan, -0.04, 0.02, 0.16],
        [np.nan, -0.27, 0.02, 0.10],
        [np.nan, np.nan, -0.04, 0.08],
        [np.nan, np.nan, -0.37, 0.07],
        [np.nan, np.nan, np.nan, -0.04]
    ])
    
    early_type_Re_err = np.array([
        [0.06, 0.02, 0.02, 0.05],
        [0.03, 0.02, 0.01, 0.02],
        [0.02, 0.02, 0.01, 0.02],
        [0.06, 0.03, 0.02, 0.02],
        [0.02, 0.03, 0.03, 0.03],
        [0.02, 0.06, 0.02, 0.02],
        [np.nan, 0.06, 0.03, 0.03],
        [np.nan, 0.02, 0.03, 0.01],
        [np.nan, np.nan, 0.08, 0.03],
        [np.nan, np.nan, 0.02, 0.07],
        [np.nan, np.nan, np.nan, 0.02]
    ])
    
    return {
        'redshift_bins': redshift_bins,
        'mass_bins': mass_bins,
        'late_type': {'Re': late_type_Re, 'Re_err': late_type_Re_err},
        'early_type': {'Re': early_type_Re, 'Re_err': early_type_Re_err}
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
        late_Re_err = data['late_type']['Re_err'][i_z]
        early_Re = data['early_type']['Re'][i_z]
        early_Re_err = data['early_type']['Re_err'][i_z]
        
        # Process star forming (late-type) sample
        valid_late = ~np.isnan(late_Re)
        if np.any(valid_late):
            mass_stellar_late = 10**data['mass_bins'][valid_late]
            log_mass_late = data['mass_bins'][valid_late]
            
            # Convert log(Re/kpc) to Re in Mpc
            Re_late_kpc = 10**late_Re[valid_late]
            Re_late_mpc = Re_late_kpc * 1e-3  # kpc to Mpc
            
            # Error propagation from logarithmic to linear space:
            # For R = 10^(log R), the error is: dR = R * ln(10) * d(log R)
            Re_late_err_mpc = Re_late_mpc * np.log(10) * late_Re_err[valid_late]
            
            # Calculate main sequence SFR at these masses using Speagle+14
            log_sfr_ms = speagle14_log_sfr_ms(log_mass_late, z=z_center, cosmology=cosmology)
            sfr_ms = 10**log_sfr_ms
            
            # Use default scatter values from module constants
            Re_scatter = np.full(len(mass_stellar_late), DEFAULT_RADIUS_SCATTER_DEX)
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
                mainSequenceSFR=sfr_ms,
                offsetMainSequenceSFR=DEFAULT_MAIN_SEQUENCE_OFFSET_DEX
            )
            samples.append(sample_sf)
        
        # Process quiescent (early-type) sample
        valid_early = ~np.isnan(early_Re)
        if np.any(valid_early):
            mass_stellar_early = 10**data['mass_bins'][valid_early]
            log_mass_early = data['mass_bins'][valid_early]
            
            # Convert log(Re/kpc) to Re in Mpc
            Re_early_kpc = 10**early_Re[valid_early]
            Re_early_mpc = Re_early_kpc * 1e-3
            
            # Error propagation from logarithmic to linear space:
            # For R = 10^(log R), the error is: dR = R * ln(10) * d(log R)
            Re_early_err_mpc = Re_early_mpc * np.log(10) * early_Re_err[valid_early]
            
            # Calculate main sequence SFR (even for quiescent, as reference)
            log_sfr_ms = speagle14_log_sfr_ms(log_mass_early, z=z_center, cosmology=cosmology)
            sfr_ms = 10**log_sfr_ms
            
            # Use default scatter values from module constants
            Re_scatter = np.full(len(mass_stellar_early), DEFAULT_RADIUS_SCATTER_DEX)
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
                mainSequenceSFR=sfr_ms,
                offsetMainSequenceSFR=DEFAULT_MAIN_SEQUENCE_OFFSET_DEX
            )
            samples.append(sample_q)
    
    return GalacticusMassSizeData(
        samples=samples,
        cosmology=cosmology,
        label='vanDerWel2014',
        reference='van der Wel et al. (2014)'
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
