#!/usr/bin/env python3
"""
Validation script for Galacticus-compatible SHMR datasets.

This script validates SHMR data files against the Galacticus format
specification and reports any issues or warnings.
"""

import sys
import argparse
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from shmr_datasets import validate_galacticus_file, print_galacticus_file_info


def validate_file(filepath):
    """
    Validate a single Galacticus SHMR file.
    
    Parameters
    ----------
    filepath : Path
        Path to the SHMR file to validate
        
    Returns
    -------
    dict
        Validation results
    """
    try:
        print(f"Validating {filepath}...")
        
        # Validate the file format
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
        description="Validate SHMR datasets in Galacticus format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single file
  python validate.py data/theory/behroozi2013/behroozi2013_z0_galacticus.hdf5
  
  # Validate all files in a directory
  python validate.py data/
  
  # Validate specific file types
  python validate.py data/ --pattern "*.hdf5"
        """
    )
    
    parser.add_argument(
        "path",
        type=Path,
        help="Path to SHMR file or directory to validate"
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