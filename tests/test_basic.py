"""
Basic tests for SHMR datasets package.

These tests validate the core functionality of the SHMR datasets package.
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
from datetime import datetime

# Import the package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from shmr_datasets import (
    SHMRData, SHMRMetadata,
    save_shmr, load_shmr, validate_shmr,
    calculate_shmr, interpolate_shmr
)


class TestSHMRMetadata:
    """Test SHMRMetadata class."""
    
    def test_metadata_creation(self):
        """Test creating metadata with required fields."""
        metadata = SHMRMetadata(
            name="Test SHMR",
            version="1.0",
            description="Test dataset",
            source_type="observation",
            reference="Test et al. 2024",
            creation_method="test",
            creation_date="2024-01-01",
            created_by="Test User"
        )
        
        assert metadata.name == "Test SHMR"
        assert metadata.version == "1.0"
        assert metadata.source_type == "observation"
        assert metadata.creation_method == "test"


class TestSHMRData:
    """Test SHMRData class."""
    
    def test_basic_data_creation(self):
        """Test creating SHMR data with basic arrays."""
        halo_masses = np.array([1e12, 1e13, 1e14])
        stellar_masses = np.array([1e10, 1e11, 5e11])
        
        shmr_data = SHMRData(
            halo_mass=halo_masses,
            stellar_mass=stellar_masses
        )
        
        assert len(shmr_data.halo_mass) == 3
        assert len(shmr_data.stellar_mass) == 3
        assert shmr_data.n_points == 3
        assert not shmr_data.has_stellar_mass_errors()
        assert not shmr_data.has_halo_mass_errors()
    
    def test_data_with_errors(self):
        """Test creating SHMR data with error arrays."""
        halo_masses = np.array([1e12, 1e13, 1e14])
        stellar_masses = np.array([1e10, 1e11, 5e11])
        stellar_errors = np.array([1e9, 1e10, 5e10])
        
        shmr_data = SHMRData(
            halo_mass=halo_masses,
            stellar_mass=stellar_masses,
            stellar_mass_err_lower=stellar_errors,
            stellar_mass_err_upper=stellar_errors
        )
        
        assert shmr_data.has_stellar_mass_errors()
        assert not shmr_data.has_halo_mass_errors()
    
    def test_array_length_mismatch(self):
        """Test that mismatched array lengths raise an error."""
        halo_masses = np.array([1e12, 1e13, 1e14])
        stellar_masses = np.array([1e10, 1e11])  # Different length
        
        with pytest.raises(ValueError, match="same length"):
            SHMRData(halo_mass=halo_masses, stellar_mass=stellar_masses)


class TestIOFunctions:
    """Test I/O functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample SHMR data for testing."""
        metadata = SHMRMetadata(
            name="Test SHMR",
            version="1.0",
            description="Test dataset for I/O",
            source_type="test",
            reference="Test Reference",
            creation_method="test",
            creation_date=datetime.now().strftime("%Y-%m-%d"),
            created_by="Test Suite"
        )
        
        return SHMRData(
            halo_mass=np.array([1e12, 1e13, 1e14]),
            stellar_mass=np.array([1e10, 1e11, 5e11]),
            stellar_mass_err_lower=np.array([1e9, 1e10, 5e10]),
            stellar_mass_err_upper=np.array([1e9, 1e10, 5e10]),
            metadata=metadata
        )
    
    def test_yaml_roundtrip(self, sample_data):
        """Test saving and loading YAML format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.yaml"
            
            # Save data
            save_shmr(sample_data, filepath, format="yaml")
            assert filepath.exists()
            
            # Load data back
            loaded_data = load_shmr(filepath, format="yaml")
            
            # Verify data integrity
            np.testing.assert_array_equal(sample_data.halo_mass, loaded_data.halo_mass)
            np.testing.assert_array_equal(sample_data.stellar_mass, loaded_data.stellar_mass)
            assert sample_data.metadata.name == loaded_data.metadata.name
            assert sample_data.metadata.reference == loaded_data.metadata.reference
    
    def test_hdf5_roundtrip(self, sample_data):
        """Test saving and loading HDF5 format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.h5"
            
            # Save data
            save_shmr(sample_data, filepath, format="hdf5")
            assert filepath.exists()
            
            # Load data back
            loaded_data = load_shmr(filepath, format="hdf5")
            
            # Verify data integrity
            np.testing.assert_array_equal(sample_data.halo_mass, loaded_data.halo_mass)
            np.testing.assert_array_equal(sample_data.stellar_mass, loaded_data.stellar_mass)
            assert sample_data.metadata.name == loaded_data.metadata.name
    
    def test_auto_format_detection(self, sample_data):
        """Test automatic format detection from file extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "test.yaml"
            h5_path = Path(tmpdir) / "test.h5"
            
            # Save with auto format detection
            save_shmr(sample_data, yaml_path)  # Should detect YAML
            save_shmr(sample_data, h5_path)    # Should detect HDF5
            
            # Load with auto format detection
            yaml_data = load_shmr(yaml_path)   # Should detect YAML
            h5_data = load_shmr(h5_path)       # Should detect HDF5
            
            # Both should have same data
            np.testing.assert_array_equal(yaml_data.halo_mass, h5_data.halo_mass)
            np.testing.assert_array_equal(yaml_data.stellar_mass, h5_data.stellar_mass)


class TestValidation:
    """Test validation functions."""
    
    def test_valid_data(self):
        """Test validation of valid SHMR data."""
        metadata = SHMRMetadata(
            name="Valid SHMR",
            version="1.0",
            description="Valid test dataset",
            source_type="observation",
            reference="Valid Reference",
            creation_method="test",
            creation_date="2024-01-01",
            created_by="Test"
        )
        
        shmr_data = SHMRData(
            halo_mass=np.array([1e12, 1e13, 1e14]),
            stellar_mass=np.array([1e10, 1e11, 5e11]),
            metadata=metadata
        )
        
        results = validate_shmr(shmr_data)
        assert results["valid"] is True
        assert len(results["errors"]) == 0
    
    def test_negative_masses(self):
        """Test validation catches negative masses."""
        metadata = SHMRMetadata(
            name="Invalid SHMR",
            version="1.0",
            description="Invalid test dataset",
            source_type="observation",
            reference="Invalid Reference",
            creation_method="test",
            creation_date="2024-01-01",
            created_by="Test"
        )
        
        shmr_data = SHMRData(
            halo_mass=np.array([1e12, -1e13, 1e14]),  # Negative mass
            stellar_mass=np.array([1e10, 1e11, 5e11]),
            metadata=metadata
        )
        
        results = validate_shmr(shmr_data)
        assert results["valid"] is False
        assert any("positive" in error.lower() for error in results["errors"])


class TestCalculations:
    """Test SHMR calculation functions."""
    
    def test_behroozi2013_calculation(self):
        """Test Behroozi+ 2013 SHMR calculation."""
        halo_masses = np.array([1e12, 1e13, 1e14])
        
        shmr_data = calculate_shmr(
            halo_masses=halo_masses,
            shmr_function="behroozi2013",
            parameters={
                "log_m1": 12.0,
                "ms0": 10.5,
                "beta": 0.5,
                "delta": 0.5,
                "gamma": 1.5
            },
            name="Test Behroozi",
            version="1.0",
            description="Test calculation",
            reference="Test",
            creation_method="calculation",
            creation_date="2024-01-01",
            created_by="Test"
        )
        
        assert len(shmr_data.stellar_mass) == len(halo_masses)
        assert np.all(shmr_data.stellar_mass > 0)
        assert shmr_data.metadata.source_type == "theory"
    
    def test_interpolation(self):
        """Test SHMR interpolation."""
        # Create original data
        original_hm = np.logspace(12, 14, 5)
        original_sm = 1e10 * (original_hm / 1e12)**0.8
        
        metadata = SHMRMetadata(
            name="Test SHMR",
            version="1.0",
            description="Test",
            source_type="theory",
            reference="Test",
            creation_method="test",
            creation_date="2024-01-01",
            created_by="Test"
        )
        
        original_data = SHMRData(
            halo_mass=original_hm,
            stellar_mass=original_sm,
            metadata=metadata
        )
        
        # Interpolate to new points
        new_hm = np.logspace(12.5, 13.5, 3)
        interpolated = interpolate_shmr(
            original_data, 
            new_hm, 
            method="linear"
        )
        
        assert len(interpolated.halo_mass) == len(new_hm)
        assert np.all(interpolated.stellar_mass > 0)
        assert "interpolated" in interpolated.metadata.name.lower()


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])