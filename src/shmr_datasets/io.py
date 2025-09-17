"""
Input/output utilities for Galacticus-compatible SHMR datasets.

This module provides functions to load, save, and validate SHMR datasets
in the exact HDF5 format expected by Galacticus.
"""

import h5py
import numpy as np
from pathlib import Path
from typing import Union, Dict, Any, List

from .data_format import (
    GalacticusSHMRData, 
    RedshiftInterval, 
    GalacticusCosmology,
    DATASET_DESCRIPTIONS,
    UNITS_IN_SI,
    validate_halo_mass_definition
)


def save_galacticus_shmr(data: GalacticusSHMRData, filepath: Union[str, Path]) -> None:
    """
    Save SHMR data to HDF5 file in Galacticus format.
    
    Parameters
    ----------
    data : GalacticusSHMRData
        The SHMR data to save
    filepath : str or Path
        Output HDF5 file path (must end with .h5 or .hdf5)
    """
    filepath = Path(filepath)
    
    # Validate file extension
    if filepath.suffix != '.hdf5':
        raise ValueError("Galacticus format requires .hdf5 extension")
    
    # Validate halo mass definition
    if not validate_halo_mass_definition(data.haloMassDefinition):
        raise ValueError(f"Invalid halo mass definition: {data.haloMassDefinition}")
    
    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with h5py.File(filepath, 'w') as f:
        # Set top-level attributes required by Galacticus
        f.attrs['haloMassDefinition'] = data.haloMassDefinition
        f.attrs['label'] = data.label
        f.attrs['reference'] = data.reference
        
        # Create cosmology group
        cosmo_group = f.create_group('cosmology')
        cosmo_group.attrs['OmegaMatter'] = data.cosmology.OmegaMatter
        cosmo_group.attrs['OmegaDarkEnergy'] = data.cosmology.OmegaDarkEnergy
        cosmo_group.attrs['OmegaBaryon'] = data.cosmology.OmegaBaryon
        cosmo_group.attrs['HubbleConstant'] = data.cosmology.HubbleConstant
        
        # Create redshift interval groups
        for i, interval in enumerate(data.redshift_intervals):
            group_name = f'redshiftInterval{i}'
            interval_group = f.create_group(group_name)
            
            # Set group attributes
            interval_group.attrs['redshiftMinimum'] = interval.redshiftMinimum
            interval_group.attrs['redshiftMaximum'] = interval.redshiftMaximum
            
            # Create datasets with proper attributes
            datasets = {
                'massHalo': interval.massHalo,
                'massStellar': interval.massStellar,
                'massStellarError': interval.massStellarError,
                'massStellarScatter': interval.massStellarScatter,
                'massStellarScatterError': interval.massStellarScatterError
            }
            
            for name, data_array in datasets.items():
                dset = interval_group.create_dataset(name, data=data_array)
                
                # Add description attribute
                if name in DATASET_DESCRIPTIONS:
                    dset.attrs['description'] = DATASET_DESCRIPTIONS[name]
                
                # Add unitsInSI attribute
                if name in ['massHalo', 'massStellar', 'massStellarError']:
                    dset.attrs['unitsInSI'] = UNITS_IN_SI['Msun']
                elif 'Scatter' in name:
                    dset.attrs['unitsInSI'] = UNITS_IN_SI['dex']


def load_galacticus_shmr(filepath: Union[str, Path]) -> GalacticusSHMRData:
    """
    Load SHMR data from Galacticus-format HDF5 file.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the HDF5 file
        
    Returns
    -------
    GalacticusSHMRData
        The loaded SHMR data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with h5py.File(filepath, 'r') as f:
        # Read top-level attributes
        haloMassDefinition = f.attrs['haloMassDefinition']
        if isinstance(haloMassDefinition, bytes):
            haloMassDefinition = haloMassDefinition.decode('utf-8')
            
        label = f.attrs['label']
        if isinstance(label, bytes):
            label = label.decode('utf-8')
            
        reference = f.attrs['reference']
        if isinstance(reference, bytes):
            reference = reference.decode('utf-8')
        
        # Read cosmology
        cosmo_group = f['cosmology']
        cosmology = GalacticusCosmology(
            OmegaMatter=cosmo_group.attrs['OmegaMatter'],
            OmegaDarkEnergy=cosmo_group.attrs['OmegaDarkEnergy'],
            OmegaBaryon=cosmo_group.attrs['OmegaBaryon'],
            HubbleConstant=cosmo_group.attrs['HubbleConstant']
        )
        
        # Read redshift intervals
        redshift_intervals = []
        
        # Find all redshiftInterval groups
        interval_names = [name for name in f.keys() 
                         if name.startswith('redshiftInterval')]
        interval_names.sort(key=lambda x: int(x.replace('redshiftInterval', '')))
        
        for interval_name in interval_names:
            group = f[interval_name]
            
            # Read group attributes
            redshiftMinimum = group.attrs['redshiftMinimum']
            redshiftMaximum = group.attrs['redshiftMaximum']
            
            # Read datasets
            interval = RedshiftInterval(
                massHalo=np.array(group['massHalo']),
                massStellar=np.array(group['massStellar']),
                massStellarError=np.array(group['massStellarError']),
                massStellarScatter=np.array(group['massStellarScatter']),
                massStellarScatterError=np.array(group['massStellarScatterError']),
                redshiftMinimum=redshiftMinimum,
                redshiftMaximum=redshiftMaximum
            )
            
            redshift_intervals.append(interval)
        
        return GalacticusSHMRData(
            redshift_intervals=redshift_intervals,
            cosmology=cosmology,
            haloMassDefinition=haloMassDefinition,
            label=label,
            reference=reference
        )


def validate_galacticus_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate that an HDF5 file conforms to Galacticus SHMR format.
    
    Parameters
    ---------- 
    filepath : str or Path
        Path to the HDF5 file to validate
        
    Returns
    -------
    Dict[str, Any]
        Validation results with 'valid' boolean and 'errors' list
    """
    filepath = Path(filepath)
    results = {'valid': True, 'errors': [], 'warnings': []}
    
    if not filepath.exists():
        results['valid'] = False
        results['errors'].append(f"File not found: {filepath}")
        return results
    
    try:
        with h5py.File(filepath, 'r') as f:
            # Check required top-level attributes
            required_attrs = ['haloMassDefinition', 'label', 'reference']
            for attr in required_attrs:
                if attr not in f.attrs:
                    results['valid'] = False
                    results['errors'].append(f"Missing required attribute: {attr}")
            
            # Check halo mass definition
            if 'haloMassDefinition' in f.attrs:
                halo_def = f.attrs['haloMassDefinition']
                if isinstance(halo_def, bytes):
                    halo_def = halo_def.decode('utf-8')
                if not validate_halo_mass_definition(halo_def):
                    results['warnings'].append(f"Non-standard halo mass definition: {halo_def}")
            
            # Check cosmology group
            if 'cosmology' not in f:
                results['valid'] = False
                results['errors'].append("Missing required cosmology group")
            else:
                cosmo_group = f['cosmology']
                required_cosmo_attrs = ['OmegaMatter', 'OmegaDarkEnergy', 
                                       'OmegaBaryon', 'HubbleConstant']
                for attr in required_cosmo_attrs:
                    if attr not in cosmo_group.attrs:
                        results['valid'] = False
                        results['errors'].append(f"Missing cosmology attribute: {attr}")
            
            # Check redshift intervals
            interval_names = [name for name in f.keys() 
                             if name.startswith('redshiftInterval')]
            
            if not interval_names:
                results['valid'] = False
                results['errors'].append("No redshift intervals found")
            
            for interval_name in interval_names:
                group = f[interval_name]
                
                # Check group attributes
                required_group_attrs = ['redshiftMinimum', 'redshiftMaximum']
                for attr in required_group_attrs:
                    if attr not in group.attrs:
                        results['valid'] = False
                        results['errors'].append(f"Missing attribute {attr} in {interval_name}")
                
                # Check datasets
                required_datasets = ['massHalo', 'massStellar', 'massStellarError',
                                   'massStellarScatter', 'massStellarScatterError']
                for dset_name in required_datasets:
                    if dset_name not in group:
                        results['valid'] = False
                        results['errors'].append(f"Missing dataset {dset_name} in {interval_name}")
                    else:
                        # Check that all datasets have same length
                        dset = group[dset_name]
                        if dset_name == 'massHalo':
                            expected_length = len(dset)
                        elif len(dset) != expected_length:
                            results['valid'] = False
                            results['errors'].append(f"Dataset {dset_name} has wrong length in {interval_name}")
                        
                        # Check for recommended attributes
                        if 'description' not in dset.attrs:
                            results['warnings'].append(f"Missing description for {dset_name} in {interval_name}")
                        if 'unitsInSI' not in dset.attrs:
                            results['warnings'].append(f"Missing unitsInSI for {dset_name} in {interval_name}")
    
    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"Error reading file: {str(e)}")
    
    return results


def print_galacticus_file_info(filepath: Union[str, Path]) -> None:
    """
    Print information about a Galacticus SHMR file.
    
    Parameters
    ----------
    filepath : str or Path
        Path to the HDF5 file
    """
    try:
        data = load_galacticus_shmr(filepath)
        
        print(f"File: {filepath}")
        print(f"Label: {data.label}")
        print(f"Reference: {data.reference}")
        print(f"Halo mass definition: {data.haloMassDefinition}")
        print(f"Number of redshift intervals: {data.n_redshift_intervals}")
        print(f"Total data points: {data.total_data_points}")
        print(f"Redshift range: {data.redshift_range[0]:.3f} - {data.redshift_range[1]:.3f}")
        
        print("\nCosmology:")
        print(f"  Ω_M = {data.cosmology.OmegaMatter:.4f}")
        print(f"  Ω_Λ = {data.cosmology.OmegaDarkEnergy:.4f}")
        print(f"  Ω_b = {data.cosmology.OmegaBaryon:.5f}")
        print(f"  H₀ = {data.cosmology.HubbleConstant:.2f} km/s/Mpc")
        
        print("\nRedshift intervals:")
        for i, interval in enumerate(data.redshift_intervals):
            print(f"  {i}: z={interval.redshiftMinimum:.3f}-{interval.redshiftMaximum:.3f}, "
                  f"{interval.n_points} points")
        
    except Exception as e:
        print(f"Error reading file: {e}")