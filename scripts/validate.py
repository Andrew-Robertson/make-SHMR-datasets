#!/usr/bin/env python3
"""
Validation script for Galacticus-compatible SHMR and BHMR datasets.

This script validates stellar mass - halo mass relation (SHMR) and
black hole mass - halo mass relation (BHMR) data files against the
Galacticus format specification and reports any issues or warnings.
"""

import sys
import argparse
from pathlib import Path

from shmr_datasets import (
    validate_galacticus_file, 
    print_galacticus_file_info,
    validate_galacticus_bhmr_file,
    print_galacticus_bhmr_file_info
)
import h5py


def detect_file_type(filepath):
    """
    Detect whether a file is SHMR or BHMR based on its datasets.
    
    Parameters
    ----------
    filepath : Path
        Path to the file
        
    Returns
    -------
    str
        'shmr' for stellar mass files, 'bhmr' for black hole mass files, or 'unknown'
    """
    try:
        with h5py.File(filepath, 'r') as f:
            # Find a redshift interval group
            interval_groups = [name for name in f.keys() if name.startswith('redshiftInterval')]
            if not interval_groups:
                return 'unknown'
            
            # Check the first interval for dataset names
            group = f[interval_groups[0]]
            if 'massStellar' in group:
                return 'shmr'
            elif 'massBlackHole' in group:
                return 'bhmr'
            else:
                return 'unknown'
    except Exception:
        return 'unknown'


def validate_file(filepath):
    """
    Validate a single Galacticus SHMR or BHMR file.
    
    Parameters
    ----------
    filepath : Path
        Path to the file to validate
        
    Returns
    -------
    dict
        Validation results
    """
    try:
        # Detect file type
        file_type = detect_file_type(filepath)
        
        print(f"Validating {filepath}...")
        if file_type == 'shmr':
            print("  Detected: Stellar Mass - Halo Mass Relation")
        elif file_type == 'bhmr':
            print("  Detected: Black Hole Mass - Halo Mass Relation")
        else:
            print("  Warning: Could not detect file type")
        
        # Validate the file format
        if file_type == 'bhmr':
            results = validate_galacticus_bhmr_file(filepath)
        else:
            results = validate_galacticus_file(filepath)
        
        # Print results
        print(f"\nValidation Results for {filepath.name}")
        print("=" * 50)
        
        if results["valid"]:
            print("✅ VALID: Dataset passes all validation checks")
        else:
            print("❌ INVALID: Dataset has validation errors")
        
        # Print errors
        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  ❌ {error}")
        
        # Print warnings
        if results["warnings"]:
            print("\nWarnings:")
            for warning in results["warnings"]:
                print(f"  ⚠️  {warning}")
        
        # Print file info if valid
        if results["valid"]:
            print("\nFile Information:")
            print("-" * 30)
            if file_type == 'bhmr':
                print_galacticus_bhmr_file_info(filepath)
            else:
                print_galacticus_file_info(filepath)
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR: Failed to validate {filepath}: {e}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_directory(directory):
    """
    Validate all SHMR files in a directory.
    
    Parameters
    ----------
    directory : Path
        Directory containing SHMR files
        
    Returns
    -------
    dict
        Summary of validation results
    """
    # Find all HDF5 files
    hdf5_files = list(directory.rglob("*.hdf5"))
    
    if not hdf5_files:
        print(f"No HDF5 files found in {directory}")
        return {"total": 0, "valid": 0, "invalid": 0}
    
    print(f"Found {len(hdf5_files)} HDF5 files to validate")
    print("=" * 60)
    
    valid_count = 0
    invalid_count = 0
    
    for filepath in sorted(hdf5_files):
        results = validate_file(filepath)
        
        if results["valid"]:
            valid_count += 1
        else:
            invalid_count += 1
        
        print("\n" + "-" * 60)
    
    # Print summary
    print(f"\nValidation Summary")
    print("=" * 40)
    print(f"Total files: {len(hdf5_files)}")
    print(f"Valid files: {valid_count}")
    print(f"Invalid files: {invalid_count}")
    
    if invalid_count == 0:
        print("🎉 All files are valid!")
    else:
        print(f"⚠️  {invalid_count} files have validation issues")
    
    return {
        "total": len(hdf5_files),
        "valid": valid_count, 
        "invalid": invalid_count
    }


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate SHMR and BHMR datasets in Galacticus format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single SHMR file
  python validate.py data/theory/behroozi2010/behroozi2010_parametric.hdf5
  
  # Validate a single BHMR file
  python validate.py data/observations/trinity/trinity_bhmr.hdf5
  
  # Validate all files in a directory
  python validate.py data/
  
  # Validate specific file types
  python validate.py data/ --pattern "*.hdf5"
        """
    )
    
    parser.add_argument(
        "path",
        type=Path,
        help="Path to SHMR/BHMR file or directory to validate"
    )
    
    parser.add_argument(
        "--pattern",
        default="*.hdf5",
        help="File pattern to match when validating directories (default: *.hdf5)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Check if path exists
    if not args.path.exists():
        print(f"❌ Error: Path '{args.path}' does not exist")
        sys.exit(1)
    
    try:
        if args.path.is_file():
            # Validate single file
            results = validate_file(args.path)
            sys.exit(0 if results["valid"] else 1)
        
        elif args.path.is_dir():
            # Validate directory
            summary = validate_directory(args.path)
            sys.exit(0 if summary["invalid"] == 0 else 1)
        
        else:
            print(f"❌ Error: '{args.path}' is neither a file nor directory")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()