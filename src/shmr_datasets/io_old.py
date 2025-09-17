"""
Input/output utilities for SHMR datasets.

This module provides functions to load, save, and validate SHMR datasets
in various formats with complete metadata preservation.
"""

import json
import yaml
import h5py
import numpy as np
from pathlib import Path
from typing import Union, Dict, Any
import jsonschema
from dataclasses import asdict

from .data_format import SHMRData, SHMRMetadata, METADATA_SCHEMA


def save_shmr(data: SHMRData, filepath: Union[str, Path], format: str = "auto") -> None:
    """
    Save SHMR data to file with metadata.
    
    Parameters:
    -----------
    data : SHMRData
        The SHMR data to save
    filepath : str or Path
        Output file path
    format : str
        File format ("hdf5", "yaml", "json", or "auto" to infer from extension)
    """
    filepath = Path(filepath)
    
    if format == "auto":
        if filepath.suffix == ".h5":
            format = "hdf5"
        elif filepath.suffix == ".yaml":
            format = "yaml"
        elif filepath.suffix == ".json":
            format = "json"
        else:
            raise ValueError(f"Cannot infer format from extension {filepath.suffix}")
    
    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if format == "hdf5":
        _save_hdf5(data, filepath)
    elif format == "yaml":
        _save_yaml(data, filepath)
    elif format == "json":
        _save_json(data, filepath)
    else:
        raise ValueError(f"Unsupported format: {format}")


def load_shmr(filepath: Union[str, Path], format: str = "auto") -> SHMRData:
    """
    Load SHMR data from file.
    
    Parameters:
    -----------
    filepath : str or Path
        Input file path
    format : str
        File format ("hdf5", "yaml", "json", or "auto" to infer from extension)
        
    Returns:
    --------
    SHMRData
        The loaded SHMR data with metadata
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if format == "auto":
        if filepath.suffix == ".h5":
            format = "hdf5"
        elif filepath.suffix == ".yaml":
            format = "yaml"
        elif filepath.suffix == ".json":
            format = "json"
        else:
            raise ValueError(f"Cannot infer format from extension {filepath.suffix}")
    
    if format == "hdf5":
        return _load_hdf5(filepath)
    elif format == "yaml":
        return _load_yaml(filepath)
    elif format == "json":
        return _load_json(filepath)
    else:
        raise ValueError(f"Unsupported format: {format}")


def validate_shmr(data: SHMRData) -> Dict[str, Any]:
    """
    Validate SHMR data against the standard schema.
    
    Parameters:
    -----------
    data : SHMRData
        The data to validate
        
    Returns:
    --------
    dict
        Validation results with 'valid' boolean and 'errors' list
    """
    results = {"valid": True, "errors": [], "warnings": []}
    
    try:
        # Validate metadata against schema
        metadata_dict = asdict(data.metadata)
        jsonschema.validate(metadata_dict, METADATA_SCHEMA)
    except jsonschema.ValidationError as e:
        results["valid"] = False
        results["errors"].append(f"Metadata validation error: {e.message}")
    
    # Check data array consistency
    if len(data.halo_mass) != len(data.stellar_mass):
        results["valid"] = False
        results["errors"].append("Halo mass and stellar mass arrays have different lengths")
    
    # Check for non-negative masses
    if np.any(data.halo_mass <= 0):
        results["valid"] = False
        results["errors"].append("Halo masses must be positive")
    
    if np.any(data.stellar_mass <= 0):
        results["valid"] = False
        results["errors"].append("Stellar masses must be positive")
    
    # Check for sorted data (recommended but not required)
    if not np.all(data.halo_mass[:-1] <= data.halo_mass[1:]):
        results["warnings"].append("Halo mass array is not sorted")
    
    # Check error array consistency
    if data.has_stellar_mass_errors():
        if data.stellar_mass_err_lower is not None:
            if len(data.stellar_mass_err_lower) != len(data.stellar_mass):
                results["valid"] = False
                results["errors"].append("Stellar mass lower error array length mismatch")
        
        if data.stellar_mass_err_upper is not None:
            if len(data.stellar_mass_err_upper) != len(data.stellar_mass):
                results["valid"] = False
                results["errors"].append("Stellar mass upper error array length mismatch")
    
    if data.has_halo_mass_errors():
        if data.halo_mass_err_lower is not None:
            if len(data.halo_mass_err_lower) != len(data.halo_mass):
                results["valid"] = False
                results["errors"].append("Halo mass lower error array length mismatch")
        
        if data.halo_mass_err_upper is not None:
            if len(data.halo_mass_err_upper) != len(data.halo_mass):
                results["valid"] = False
                results["errors"].append("Halo mass upper error array length mismatch")
    
    return results


def _save_hdf5(data: SHMRData, filepath: Path) -> None:
    """Save data in HDF5 format."""
    with h5py.File(filepath, 'w') as f:
        # Save main data arrays
        f.create_dataset('halo_mass', data=data.halo_mass, compression='gzip')
        f.create_dataset('stellar_mass', data=data.stellar_mass, compression='gzip')
        
        # Save error arrays if present
        if data.stellar_mass_err_lower is not None:
            f.create_dataset('stellar_mass_err_lower', 
                           data=data.stellar_mass_err_lower, compression='gzip')
        if data.stellar_mass_err_upper is not None:
            f.create_dataset('stellar_mass_err_upper', 
                           data=data.stellar_mass_err_upper, compression='gzip')
        if data.halo_mass_err_lower is not None:
            f.create_dataset('halo_mass_err_lower', 
                           data=data.halo_mass_err_lower, compression='gzip')
        if data.halo_mass_err_upper is not None:
            f.create_dataset('halo_mass_err_upper', 
                           data=data.halo_mass_err_upper, compression='gzip')
        
        # Save extra data arrays
        for key, value in data.extra_data.items():
            f.create_dataset(f'extra_data/{key}', data=value, compression='gzip')
        
        # Save metadata as attributes
        metadata_dict = asdict(data.metadata)
        _save_dict_to_hdf5_attrs(f, metadata_dict, prefix='metadata_')


def _load_hdf5(filepath: Path) -> SHMRData:
    """Load data from HDF5 format."""
    with h5py.File(filepath, 'r') as f:
        # Load main arrays
        halo_mass = f['halo_mass'][:]
        stellar_mass = f['stellar_mass'][:]
        
        # Load error arrays if present
        stellar_mass_err_lower = f['stellar_mass_err_lower'][:] if 'stellar_mass_err_lower' in f else None
        stellar_mass_err_upper = f['stellar_mass_err_upper'][:] if 'stellar_mass_err_upper' in f else None
        halo_mass_err_lower = f['halo_mass_err_lower'][:] if 'halo_mass_err_lower' in f else None
        halo_mass_err_upper = f['halo_mass_err_upper'][:] if 'halo_mass_err_upper' in f else None
        
        # Load extra data
        extra_data = {}
        if 'extra_data' in f:
            for key in f['extra_data'].keys():
                extra_data[key] = f[f'extra_data/{key}'][:]
        
        # Load metadata from attributes
        metadata_dict = _load_dict_from_hdf5_attrs(f, prefix='metadata_')
        metadata = SHMRMetadata(**metadata_dict)
        
        return SHMRData(
            halo_mass=halo_mass,
            stellar_mass=stellar_mass,
            stellar_mass_err_lower=stellar_mass_err_lower,
            stellar_mass_err_upper=stellar_mass_err_upper,
            halo_mass_err_lower=halo_mass_err_lower,
            halo_mass_err_upper=halo_mass_err_upper,
            metadata=metadata,
            extra_data=extra_data
        )


def _save_yaml(data: SHMRData, filepath: Path) -> None:
    """Save data in YAML format."""
    output_dict = {
        'metadata': asdict(data.metadata),
        'data': {
            'halo_mass': data.halo_mass.tolist(),
            'stellar_mass': data.stellar_mass.tolist(),
        }
    }
    
    # Add error arrays if present
    if data.stellar_mass_err_lower is not None:
        output_dict['data']['stellar_mass_err_lower'] = data.stellar_mass_err_lower.tolist()
    if data.stellar_mass_err_upper is not None:
        output_dict['data']['stellar_mass_err_upper'] = data.stellar_mass_err_upper.tolist()
    if data.halo_mass_err_lower is not None:
        output_dict['data']['halo_mass_err_lower'] = data.halo_mass_err_lower.tolist()
    if data.halo_mass_err_upper is not None:
        output_dict['data']['halo_mass_err_upper'] = data.halo_mass_err_upper.tolist()
    
    # Add extra data
    for key, value in data.extra_data.items():
        output_dict['data'][key] = value.tolist()
    
    with open(filepath, 'w') as f:
        yaml.dump(output_dict, f, default_flow_style=False, sort_keys=False)


def _load_yaml(filepath: Path) -> SHMRData:
    """Load data from YAML format."""
    with open(filepath, 'r') as f:
        data_dict = yaml.safe_load(f)
    
    metadata = SHMRMetadata(**data_dict['metadata'])
    data_section = data_dict['data']
    
    # Extract error arrays if present
    stellar_mass_err_lower = np.array(data_section.get('stellar_mass_err_lower')) if 'stellar_mass_err_lower' in data_section else None
    stellar_mass_err_upper = np.array(data_section.get('stellar_mass_err_upper')) if 'stellar_mass_err_upper' in data_section else None
    halo_mass_err_lower = np.array(data_section.get('halo_mass_err_lower')) if 'halo_mass_err_lower' in data_section else None
    halo_mass_err_upper = np.array(data_section.get('halo_mass_err_upper')) if 'halo_mass_err_upper' in data_section else None
    
    # Extract extra data (anything not in the standard fields)
    standard_fields = {'halo_mass', 'stellar_mass', 'stellar_mass_err_lower', 
                      'stellar_mass_err_upper', 'halo_mass_err_lower', 'halo_mass_err_upper'}
    extra_data = {k: np.array(v) for k, v in data_section.items() if k not in standard_fields}
    
    return SHMRData(
        halo_mass=np.array(data_section['halo_mass']),
        stellar_mass=np.array(data_section['stellar_mass']),
        stellar_mass_err_lower=stellar_mass_err_lower,
        stellar_mass_err_upper=stellar_mass_err_upper,
        halo_mass_err_lower=halo_mass_err_lower,
        halo_mass_err_upper=halo_mass_err_upper,
        metadata=metadata,
        extra_data=extra_data
    )


def _save_json(data: SHMRData, filepath: Path) -> None:
    """Save data in JSON format."""
    output_dict = {
        'metadata': asdict(data.metadata),
        'data': {
            'halo_mass': data.halo_mass.tolist(),
            'stellar_mass': data.stellar_mass.tolist(),
        }
    }
    
    # Add error arrays if present
    if data.stellar_mass_err_lower is not None:
        output_dict['data']['stellar_mass_err_lower'] = data.stellar_mass_err_lower.tolist()
    if data.stellar_mass_err_upper is not None:
        output_dict['data']['stellar_mass_err_upper'] = data.stellar_mass_err_upper.tolist()
    if data.halo_mass_err_lower is not None:
        output_dict['data']['halo_mass_err_lower'] = data.halo_mass_err_lower.tolist()
    if data.halo_mass_err_upper is not None:
        output_dict['data']['halo_mass_err_upper'] = data.halo_mass_err_upper.tolist()
    
    # Add extra data
    for key, value in data.extra_data.items():
        output_dict['data'][key] = value.tolist()
    
    with open(filepath, 'w') as f:
        json.dump(output_dict, f, indent=2)


def _load_json(filepath: Path) -> SHMRData:
    """Load data from JSON format."""
    with open(filepath, 'r') as f:
        data_dict = json.load(f)
    
    metadata = SHMRMetadata(**data_dict['metadata'])
    data_section = data_dict['data']
    
    # Extract error arrays if present
    stellar_mass_err_lower = np.array(data_section.get('stellar_mass_err_lower')) if 'stellar_mass_err_lower' in data_section else None
    stellar_mass_err_upper = np.array(data_section.get('stellar_mass_err_upper')) if 'stellar_mass_err_upper' in data_section else None
    halo_mass_err_lower = np.array(data_section.get('halo_mass_err_lower')) if 'halo_mass_err_lower' in data_section else None
    halo_mass_err_upper = np.array(data_section.get('halo_mass_err_upper')) if 'halo_mass_err_upper' in data_section else None
    
    # Extract extra data (anything not in the standard fields)
    standard_fields = {'halo_mass', 'stellar_mass', 'stellar_mass_err_lower', 
                      'stellar_mass_err_upper', 'halo_mass_err_lower', 'halo_mass_err_upper'}
    extra_data = {k: np.array(v) for k, v in data_section.items() if k not in standard_fields}
    
    return SHMRData(
        halo_mass=np.array(data_section['halo_mass']),
        stellar_mass=np.array(data_section['stellar_mass']),
        stellar_mass_err_lower=stellar_mass_err_lower,
        stellar_mass_err_upper=stellar_mass_err_upper,
        halo_mass_err_lower=halo_mass_err_lower,
        halo_mass_err_upper=halo_mass_err_upper,
        metadata=metadata,
        extra_data=extra_data
    )


def _save_dict_to_hdf5_attrs(group, data_dict, prefix=""):
    """Recursively save dictionary to HDF5 attributes."""
    for key, value in data_dict.items():
        attr_name = f"{prefix}{key}"
        if isinstance(value, dict):
            # For nested dictionaries, use double underscore to separate levels
            for subkey, subvalue in value.items():
                _save_dict_to_hdf5_attrs(group, {subkey: subvalue}, f"{attr_name}__")
        elif isinstance(value, (list, tuple)):
            # Convert lists/tuples to JSON strings for HDF5 storage
            group.attrs[attr_name] = json.dumps(value)
        elif value is None:
            # Store None as special marker
            group.attrs[attr_name] = "___NONE___"
        elif isinstance(value, (str, int, float, bool, np.integer, np.floating)):
            group.attrs[attr_name] = value
        else:
            # For any other type, convert to JSON string
            try:
                group.attrs[attr_name] = json.dumps(value)
            except (TypeError, ValueError):
                # If JSON serialization fails, convert to string
                group.attrs[attr_name] = str(value)


def _load_dict_from_hdf5_attrs(group, prefix=""):
    """Recursively load dictionary from HDF5 attributes."""
    result = {}
    prefix_len = len(prefix)
    
    # Find all attributes with our prefix
    all_attrs = [(k, v) for k, v in group.attrs.items() if k.startswith(prefix)]
    
    for attr_name, attr_value in all_attrs:
        key_part = attr_name[prefix_len:]
        
        if '__' in key_part:
            # This is a nested attribute
            keys = key_part.split('__')
            current_dict = result
            
            # Navigate to the correct nested location
            for i, key in enumerate(keys[:-1]):
                if key not in current_dict:
                    current_dict[key] = {}
                current_dict = current_dict[key]
            
            # Set the final value
            final_key = keys[-1]
            final_value = attr_value
            
            # Handle special values
            if final_value == "___NONE___":
                final_value = None
            elif isinstance(final_value, str) and final_value.startswith(('[', '{')):
                try:
                    final_value = json.loads(final_value)
                except (json.JSONDecodeError, ValueError):
                    pass
            elif isinstance(final_value, (np.integer, np.floating)):
                final_value = final_value.item()
            elif isinstance(final_value, np.bool_):
                final_value = bool(final_value)
            
            current_dict[final_key] = final_value
            
        else:
            # This is a direct attribute
            final_value = attr_value
            
            # Handle special values
            if final_value == "___NONE___":
                final_value = None
            elif isinstance(final_value, str):
                # Try to parse as JSON
                try:
                    final_value = json.loads(final_value)
                except (json.JSONDecodeError, ValueError):
                    pass
            elif isinstance(final_value, (np.integer, np.floating)):
                final_value = final_value.item()
            elif isinstance(final_value, np.bool_):
                final_value = bool(final_value)
            
            result[key_part] = final_value
    
    return result