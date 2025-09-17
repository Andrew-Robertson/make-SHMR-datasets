#!/usr/bin/env python3
"""
Validation script for SHMR datasets.

This script validates SHMR data files against the standard format
and reports any issues or warnings.
"""

import sys
import argparse
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from shmr_datasets import load_shmr, validate_shmr


def validate_file(filepath):
    """
    Validate a single SHMR file.
    
    Parameters:
    -----------
    filepath : Path
        Path to the SHMR file to validate
        
    Returns:
    --------
    dict
        Validation results
    """
    try:
        # Load the data
        print(f"Loading {filepath}...")
        shmr_data = load_shmr(filepath)
        
        # Validate the data
        print("Validating data...")
        results = validate_shmr(shmr_data)
        
        # Print results
        print(f"\nValidation Results for {filepath.name}")
        print("=" * 50)
        
        if results["valid"]:
            print("✅ VALID: Dataset passes all validation checks")
        else:
            print("❌ INVALID: Dataset has validation errors")
        
        if results["errors"]:
            print(f"\n🚫 Errors ({len(results['errors'])}):")
            for i, error in enumerate(results["errors"], 1):
                print(f"  {i}. {error}")
        
        if results["warnings"]:
            print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for i, warning in enumerate(results["warnings"], 1):
                print(f"  {i}. {warning}")
        
        # Print dataset summary
        print(f"\n📊 Dataset Summary:")
        print(f"  Name: {shmr_data.metadata.name}")
        print(f"  Version: {shmr_data.metadata.version}")
        print(f"  Reference: {shmr_data.metadata.reference}")
        print(f"  Data points: {shmr_data.n_points}")
        print(f"  Halo mass range: {shmr_data.halo_mass.min():.2e} - {shmr_data.halo_mass.max():.2e}")
        print(f"  Stellar mass range: {shmr_data.stellar_mass.min():.2e} - {shmr_data.stellar_mass.max():.2e}")
        print(f"  Has stellar mass errors: {shmr_data.has_stellar_mass_errors()}")
        print(f"  Has halo mass errors: {shmr_data.has_halo_mass_errors()}")
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR: Failed to validate {filepath}: {e}")
        return {"valid": False, "errors": [str(e)], "warnings": []}


def validate_directory(directory):
    """
    Validate all SHMR files in a directory.
    
    Parameters:
    -----------
    directory : Path
        Directory containing SHMR files
    """
    shmr_extensions = {'.h5', '.yaml', '.yml', '.json'}
    shmr_files = []
    
    for ext in shmr_extensions:
        shmr_files.extend(directory.glob(f"**/*{ext}"))
    
    if not shmr_files:
        print(f"No SHMR files found in {directory}")
        return
    
    print(f"Found {len(shmr_files)} files to validate")
    
    valid_count = 0
    invalid_count = 0
    
    for filepath in shmr_files:
        print("\n" + "="*60)
        results = validate_file(filepath)
        
        if results["valid"]:
            valid_count += 1
        else:
            invalid_count += 1
    
    print("\n" + "="*60)
    print(f"VALIDATION SUMMARY")
    print(f"Total files: {len(shmr_files)}")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")
    
    if invalid_count == 0:
        print("🎉 All files passed validation!")
    else:
        print(f"⚠️  {invalid_count} files failed validation")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate SHMR dataset files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate.py file.h5                    # Validate single file
  python validate.py data/                      # Validate all files in directory
  python validate.py data/ --recursive          # Validate recursively
        """
    )
    
    parser.add_argument(
        "path",
        help="Path to SHMR file or directory to validate"
    )
    
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Search for files recursively (default for directories)"
    )
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path {path} does not exist")
        sys.exit(1)
    
    print("SHMR Dataset Validation")
    print("=" * 40)
    
    if path.is_file():
        # Validate single file
        results = validate_file(path)
        sys.exit(0 if results["valid"] else 1)
    
    elif path.is_dir():
        # Validate directory
        validate_directory(path)
        sys.exit(0)
    
    else:
        print(f"Error: {path} is neither a file nor a directory")
        sys.exit(1)


if __name__ == "__main__":
    main()