#!/usr/bin/env python3
"""
Script to create SHMR dataset from UniverseMachine data.

This script downloads and processes data from the UniverseMachine project:
Behroozi et al. 2019 (arXiv:1806.07893)
Repository: https://bitbucket.org/pbehroozi/universemachine/src/main/

This serves as an example of creating datasets from downloaded observational/simulation data.
"""

import numpy as np
import urllib.request
import gzip
from pathlib import Path
from io import StringIO
import os
import tarfile
import urllib.request
import sys

# Add the src directory to Python path
from shmr_datasets import (
    save_galacticus_shmr, 
    GalacticusCosmology,
    RedshiftInterval,
    GalacticusSHMRData
)


def create_universemachine_cosmology():
    """Create cosmology consistent with UniverseMachine (Planck 2018)."""
    return GalacticusCosmology(
        OmegaMatter=0.3089,      # Planck 2018
        OmegaDarkEnergy=0.6911,  # 1 - Ω_M
        OmegaBaryon=0.0486,      # Planck 2018 baryon density
        HubbleConstant=67.74     # km/s/Mpc, Planck 2018
    )


def download_universemachine_data():
    """
    Download UniverseMachine SHMR data.
    
    This downloads the stellar mass - halo mass relation data from the
    UniverseMachine repository. We'll use the central galaxy SHMR.
    
    Note: For a real implementation, you would download the actual
    UniverseMachine data files. For this example, we'll create synthetic
    data that matches the UniverseMachine format and methodology.
    """

    url = "https://halos.as.arizona.edu/UniverseMachine/DR1/umachine-dr1.tar.gz"
    tarball = "umachine-dr1.tar.gz"
    
    # Use repository root to determine extract directory
    repo_root = Path(__file__).parent.parent
    extract_dir = repo_root / "data" / "simulations" / "universemachine"
    target_subdir = extract_dir / "umachine-dr1" / "data" / "smhm"

    if not target_subdir.exists():
        print("Downloading UniverseMachine SHMR data...")
        # Ensure destination directory exists
        extract_dir.mkdir(parents=True, exist_ok=True)

        # Download tarball if not already present
        if not Path(tarball).exists():
            print(f"Downloading {url} ...")
            urllib.request.urlretrieve(url, tarball)

        # Extract only the median_fits subdirectory into extract_dir
        with tarfile.open(tarball, "r:gz") as tar:
            members = [m for m in tar.getmembers()
                    if m.name.startswith("umachine-dr1/data/smhm/")]
            tar.extractall(path=extract_dir, members=members)

        print(f"Extracted {len(members)} files under {extract_dir}/umachine-dr1/data/smhm/")

        # Remove tarball to save space
        Path(tarball).unlink()
        print(f"Deleted {tarball}")
    
    ##### /home/arobertson/Galacticus/make-SHMR-datasets/data/simulations/universemachine/umachine-dr1/data/smhm/params/gen_smhm_uncertainties.py is a script to create the SHMR and its uncertainty from a file describing the sample (which cotnains some parameters that were fit). Let;s use this. Though presumably not here. This should just be loading data, then the function below builds that SHMR files.
    return extract_dir



def create_universemachine_shmr(sample="True_Cen", measurement="median_raw"):
    """
    Create a Stellar Halo Mass Relation (SHMR) dataset from UniverseMachine data.
    This function processes the downloaded UniverseMachine data to create a 
    Galacticus-compatible HDF5 file containing the SHMR dataset. It retrieves 
    data from specified files, calculates redshift intervals, and constructs 
    RedshiftInterval objects for each interval.
    Parameters:
        sample (str): The type of sample to use. Default is "True_Cen".
                      Other samples may be implemented in the future.
        measurement (str): The type of measurement to process. Currently, 
                           only "median_raw" is supported. "median_fits" 
                           is not yet implemented due to lack of recorded scatter.
    Returns:
        GalacticusSHMRData: An object containing the SHMR dataset, which includes 
                             redshift intervals and associated stellar and halo mass 
                             data, along with cosmological parameters.
    Notes:
        - The function expects the UniverseMachine data to be downloaded and 
          available in a specific directory structure.
        - The function handles symmetric errors for stellar mass calculations 
          and averages the errors from the scatter data.
        - The redshift intervals are calculated based on the scale factors 
          derived from the filenames of the data files.
    """
    
    # Download/create the data
    extract_dir = download_universemachine_data()
    print(f"Using UniverseMachine data from: {extract_dir}")
    # Load the scale factors and convert to redshifts
    scale_factors = []
    
    umachine_data_dir = extract_dir / "umachine-dr1" / "data" / "smhm" / measurement
    for filename in os.listdir(umachine_data_dir):
        if filename.startswith("smhm_a") and filename.endswith(".dat"):
            scale_factor = float(filename.split('_')[1].split('.d')[0][1:])
            scale_factors.append(scale_factor)
    scale_factors = np.array(sorted(scale_factors))[::-1] # Sort and reverse to have low-z to high-z        
    redshifts = 1 / scale_factors - 1
    print("Redshifts found:")
    for z in redshifts:
        print(f"z = {z:.4f}")
    # Create redshift intervals
    redshift_intervals = []
    
    for i,z in enumerate(redshifts):
        # Define z_min and z_max for the interval
        z_min = (redshifts[i - 1] + z) / 2 if i > 0 else max(0.0, z - 0.5*(redshifts[i + 1] - z))  # Calculate z_min based on spacing
        z_max = (redshifts[i + 1] + z) / 2 if i < len(redshifts)-1 else z + 0.5*(z - redshifts[i - 1])  # Calculate z_max based on spacing

        interval_data = {
            'z_min': z_min,
            'z_max': z_max,
            'halo_masses': [],
            'stellar_masses': [],
            'stellar_errors': [],
            'stellar_scatter': [],
            'scatter_errors': []
        }
        
        print(f"Processing redshift interval {i+1}: z={interval_data['z_min']:.2f}-{interval_data['z_max']:.2f}")
        
        # Load corresponding smhm and smhm_scatter files
        smhm_file = umachine_data_dir / f"smhm_a{1/(1+z):.6f}.dat"
        smhm_scatter_file = umachine_data_dir / f"smhm_scatter_a{1/(1+z):.6f}.dat"

        if sample=="True_Cen":
            sample_column = 25 # these are listed in the header if we want to extend to other samples
        usecols = (0, sample_column, sample_column+1, sample_column+2) 
        
        # Read data from smhm file
        if smhm_file.exists():
            data = np.loadtxt(smhm_file, usecols=usecols, unpack=True)
            log10halo_mass, log10stellar_mass_ratio, err_plus_dex, err_minus_dex = data
            err_dex = (err_plus_dex + err_minus_dex) / 2 # symmetric error in dex
            interval_data['halo_masses'].extend(10**log10halo_mass)  # Convert log10 to actual mass
            interval_data['stellar_masses'].extend(10**(log10halo_mass + log10stellar_mass_ratio))  # Mstar = Mhalo * (Mstar/Mhalo)
            interval_data['stellar_errors'].extend(np.array(interval_data['stellar_masses']) * np.log(10) * err_dex)  # Approximate error on Mstar, from error on log10(Mstar)
        else:
            print(f"Warning: {smhm_file} does not exist.")
            
        # Read data from smhm_scatter file
        if smhm_scatter_file.exists():
            scatter_data = np.loadtxt(smhm_scatter_file, usecols=usecols, unpack=True)
            _, scatter, scatter_err_plus, scatter_err_minus = scatter_data # already in dex as expected by Galacticus
            interval_data['stellar_scatter'].extend(scatter)
            interval_data['scatter_errors'].extend((scatter_err_plus + scatter_err_minus) / 2)  # Average errors
        else:
            print(f"Warning: {smhm_scatter_file} does not exist.")
        
        # generate the RedshiftInterval object 
        interval = RedshiftInterval(
            massHalo=interval_data['halo_masses'],
            massStellar=interval_data['stellar_masses'],
            massStellarError=interval_data['stellar_errors'],
            massStellarScatter=interval_data['stellar_scatter'],
            massStellarScatterError=interval_data['scatter_errors'],
            redshiftMinimum=interval_data['z_min'],
            redshiftMaximum=interval_data['z_max']
        )
        
        redshift_intervals.append(interval)
    
    # Create the complete dataset
    shmr_dataset = GalacticusSHMRData(
        redshift_intervals=redshift_intervals,
        cosmology=create_universemachine_cosmology(),
        haloMassDefinition="virial",  # UniverseMachine uses virial masses
        label="UniverseMachine",
        reference="Behroozi et al. (2019)"
    )
    
    return shmr_dataset


def main():
    """Main function to create and save the dataset."""
    print("Creating UniverseMachine SHMR dataset...")
    print("=" * 50)
    print("Source: https://bitbucket.org/pbehroozi/universemachine/")
    print("Paper: Behroozi et al. 2019, MNRAS, 488, 3143 (arXiv:1806.07893)")
    print()
    
    # Create the dataset
    shmr_data = create_universemachine_shmr()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / "simulations" / "universemachine"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the dataset
    output_file = output_dir / "universemachine_downloaded.hdf5"
    save_galacticus_shmr(shmr_data, output_file)
    
    print(f"\nDataset saved to: {output_file}")
    print(f"Number of redshift intervals: {shmr_data.n_redshift_intervals}")
    print(f"Total data points: {shmr_data.total_data_points}")
    print(f"Redshift range: {shmr_data.redshift_range[0]:.1f} - {shmr_data.redshift_range[1]:.1f}")
    
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
    
    print(f"\nData provenance:")
    print(f"- Source: UniverseMachine project")
    print(f"- Repository: https://bitbucket.org/pbehroozi/universemachine/")
    print(f"- Paper: Behroozi et al. 2019, MNRAS, 488, 3143")
    print(f"- Method: Empirical modeling of galaxy-halo connection")
    print(f"- Cosmology: Planck 2018")


if __name__ == "__main__":
    main()