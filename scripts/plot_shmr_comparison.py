#!/usr/bin/env python3
"""
Compare SHMR datasets at different redshifts.

This script plots and compares all available SHMR datasets at z≈0.1, z≈1, and z≈2,
allowing visual inspection to identify any issues with the datasets.
"""

import numpy as np
import matplotlib.pyplot as plt
import h5py
from pathlib import Path

def load_shmr_at_redshift(filepath, target_redshift, tolerance=0.15):
    """
    Load SHMR data from a file at a specific redshift.
    
    Parameters
    ----------
    filepath : str
        Path to the HDF5 file
    target_redshift : float
        Target redshift to extract
    tolerance : float
        Tolerance for redshift matching (default: 0.15)
        
    Returns
    -------
    dict or None
        Dictionary with halo_masses, stellar_masses, errors, and metadata
        Returns None if no matching redshift interval found
    """
    try:
        with h5py.File(filepath, 'r') as f:
            # Get metadata
            label = f.attrs.get('label', 'Unknown')
            if hasattr(label, 'decode'):
                label = label.decode()
                
            reference = f.attrs.get('reference', 'Unknown')
            if hasattr(reference, 'decode'):
                reference = reference.decode()
            
            # Find best matching redshift interval
            best_match = None
            best_diff = float('inf')
            
            for key in f.keys():
                if key.startswith('redshiftInterval'):
                    group = f[key]
                    z_min = group.attrs['redshiftMinimum']
                    z_max = group.attrs['redshiftMaximum']
                    z_center = (z_min + z_max) / 2
                    
                    diff = abs(z_center - target_redshift)
                    if diff < tolerance and diff < best_diff:
                        best_diff = diff
                        best_match = key
            
            if best_match is None:
                return None
                
            # Load data from best matching interval
            group = f[best_match]
            z_min = group.attrs['redshiftMinimum']
            z_max = group.attrs['redshiftMaximum']
            z_center = (z_min + z_max) / 2
            
            return {
                'halo_masses': np.array(group['massHalo']),
                'stellar_masses': np.array(group['massStellar']),
                'stellar_errors': np.array(group['massStellarError']),
                'scatter': np.array(group['massStellarScatter']),
                'redshift': z_center,
                'redshift_range': (z_min, z_max),
                'label': label,
                'reference': reference,
                'filename': Path(filepath).name
            }
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

# Define files to compare
files = [
    'data/theory/behroozi2010/behroozi2010_parametric.hdf5',
    'data/theory/moster2013/moster2013_z0_galacticus.hdf5',
    'data/simulations/universemachine/universemachine_downloaded.hdf5'
]

def plot_shmr_comparison():
    """Create comparison plots of SHMR datasets at different redshifts."""
    
    # Target redshifts for comparison
    target_redshifts = [0.1, 1.0, 2.0]
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, len(target_redshifts), figsize=(18, 6))
    fig.suptitle('SHMR Dataset Comparison', fontsize=16, fontweight='bold')
    
    N = len(files)
    cmap = plt.get_cmap('tab10' if N <= 10 else 'hsv', N)
    colors = [cmap(i) for i in range(N)]
    
    for i, target_z in enumerate(target_redshifts):
        ax = axes[i]
        
        print(f"\\nPlotting SHMR at z ≈ {target_z}:")
        print("-" * 40)
        
        datasets_plotted = 0
        
        for j,filepath in enumerate(files):
            if not Path(filepath).exists():
                print(f"  Skipping {filepath} (file not found)")
                continue
                
            shmr_data = load_shmr_at_redshift(filepath, target_z)
            
            if shmr_data is None:
                print(f"  No data for {Path(filepath).name} at z ≈ {target_z}")
                continue
                
            # Plot the SHMR
            color = colors[j]
            
            ax.errorbar(
                shmr_data['halo_masses'], 
                shmr_data['stellar_masses'],
                yerr=shmr_data['stellar_errors'],
                label=f"{shmr_data['label']} (z={shmr_data['redshift']:.2f})",
                color=color,
                alpha=0.7,
                capsize=2,
                marker='o',
                markersize=3,
                linewidth=1
            )
            
            print(f"  ✓ {shmr_data['label']}: z={shmr_data['redshift']:.2f} "
                  f"(range: {shmr_data['redshift_range'][0]:.2f}-{shmr_data['redshift_range'][1]:.2f}), "
                  f"{len(shmr_data['halo_masses'])} points")
            
            datasets_plotted += 1
        
        # Formatting
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Halo Mass [M☉]', fontsize=12)
        if i == 0:
            ax.set_ylabel('Stellar Mass [M☉]', fontsize=12)
        ax.set_title(f'z ≈ {target_z}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10, loc='upper left')
        
        # Set reasonable axis limits
        ax.set_xlim(1e10, 1e15)
        ax.set_ylim(1e6, 1e12)
        
        if datasets_plotted == 0:
            ax.text(0.5, 0.5, f'No datasets available\\nat z ≈ {target_z}', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, color='gray')
    
    plt.tight_layout()
    
    # Save the plot
    output_file = 'shmr_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\\n📊 Comparison plot saved as: {output_file}")
    
    # Also show plot if running interactively
    try:
        plt.show()
    except:
        pass  # Ignore if no display available

def print_dataset_summary():
    """Print a summary of all available datasets."""
    
    print("\\n" + "="*60)
    print("SHMR DATASET SUMMARY")
    print("="*60)
    
    for filepath in files:
        if not Path(filepath).exists():
            print(f"\\n❌ {filepath}")
            print("   File not found")
            continue
            
        try:
            with h5py.File(filepath, 'r') as f:
                label = f.attrs.get('label', 'Unknown')
                if hasattr(label, 'decode'):
                    label = label.decode()
                    
                reference = f.attrs.get('reference', 'Unknown')  
                if hasattr(reference, 'decode'):
                    reference = reference.decode()
                
                intervals = [k for k in f.keys() if k.startswith('redshiftInterval')]
                
                if intervals:
                    z_centers = []
                    for interval in intervals:
                        group = f[interval]
                        z_min = group.attrs['redshiftMinimum']
                        z_max = group.attrs['redshiftMaximum']
                        z_centers.append((z_min + z_max) / 2)
                    
                    z_range = f"{min(z_centers):.2f} - {max(z_centers):.2f}"
                else:
                    z_range = "No redshift intervals"
                
                print(f"\\n✅ {Path(filepath).name}")
                print(f"   Label: {label}")
                print(f"   Reference: {reference}")
                print(f"   Redshift range: {z_range}")
                print(f"   Number of intervals: {len(intervals)}")
                
        except Exception as e:
            print(f"\\n❌ {filepath}")
            print(f"   Error: {e}")

def main():
    """Main function to create SHMR comparison plots."""
    
    print("SHMR Dataset Comparison Tool")
    print("="*50)
    
    # Print summary first
    print_dataset_summary()
    
    # Create comparison plots
    print("\\n" + "="*60)
    print("CREATING COMPARISON PLOTS")
    print("="*60)
    
    plot_shmr_comparison()
    
    print("\\n✅ Analysis complete!")
    print("\\nNext steps:")
    print("- Review the comparison plot to identify any anomalies")
    print("- Check that stellar mass ranges and trends look reasonable")
    print("- Verify that parameter uncertainty propagation is working correctly")
    print("- Ensure all datasets follow expected SHMR evolution with redshift")

if __name__ == "__main__":
    main()