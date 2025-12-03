# van der Wel et al. 2014 Stellar Mass-Size Relations

This directory contains the stellar mass-size relation dataset from van der Wel et al. 2014, formatted for use with Galacticus.

## Reference

van der Wel, A., et al. 2014, "3D-HST+CANDELS: The Evolution of the Galaxy Size-Mass Distribution since z=3", ApJ, 788, 28

Paper: https://iopscience.iop.org/article/10.1088/0004-637X/788/1/28  
ArXiv: https://arxiv.org/abs/1404.2844

## Dataset Description

The dataset contains logarithmic size distributions as a function of galaxy mass and redshift, separately for:
- **Star forming galaxies** (late-type morphologies)
- **Quiescent galaxies** (early-type morphologies)

### Redshift Coverage
11 redshift bins from z=0.25 to z=3.0

### Mass Range
Stellar masses from ~10^9.75 to ~10^11.25 M☉

### Galaxy Selection

The dataset uses the **Speagle et al. 2014** star forming main sequence to classify galaxies:
- **Star forming**: Galaxies on or above the main sequence
- **Quiescent**: Galaxies more than 0.4 dex below the main sequence

### Cosmology

WMAP7 cosmology (consistent with the original paper):
- Ω_M = 0.272
- Ω_Λ = 0.728
- Ω_b = 0.0456
- H₀ = 70.4 km/s/Mpc

## File Format

The dataset is stored in `vanderwel2014_mass_size.hdf5` using the Galacticus mass-size relation format:

### Structure
```
vanderwel2014_mass_size.hdf5
├── (attributes)
│   ├── label: "vanDerWel2014"
│   └── reference: "van der Wel et al. (2014)"
├── cosmology/
│   └── (attributes: OmegaMatter, OmegaDarkEnergy, OmegaBaryon, HubbleConstant)
├── sample1/  (z=0.25-0.50, star forming)
│   ├── massStellar
│   ├── radiusEffective
│   ├── radiusEffectiveError
│   ├── radiusEffectiveScatter
│   ├── radiusEffectiveScatterError
│   ├── mainSequenceSFR
│   └── (attributes: redshiftMinimum, redshiftMaximum, selection, offsetMainSequenceSFR)
├── sample2/  (z=0.25-0.50, quiescent)
│   └── ...
└── ... (22 samples total: 11 redshift bins × 2 selections)
```

### Units
- `massStellar`: Solar masses (M☉)
- `radiusEffective`: Megaparsecs (Mpc)
- `radiusEffectiveError`: Megaparsecs (Mpc)
- `radiusEffectiveScatter`: dex (logarithmic scatter)
- `radiusEffectiveScatterError`: dex
- `mainSequenceSFR`: Solar masses per year (M☉/yr)

## Usage with Galacticus

To use this dataset with Galacticus, add to your parameter file:

```xml
<stellarMassSizeRelation value="file">
  <fileNameTarget value="path/to/vanderwel2014_mass_size.hdf5"/>
</stellarMassSizeRelation>
```

Galacticus will automatically:
1. Read the cosmology and apply appropriate conversions
2. Select the appropriate sample based on redshift and galaxy properties
3. Classify galaxies as star forming or quiescent using the main sequence
4. Apply the mass-size relation with intrinsic scatter

## Data Provenance

The data was extracted from Table 2 of van der Wel et al. 2014, which provides effective radii measurements at different stellar masses and redshifts.

### Processing Steps
1. Extract logarithmic effective radius values (log Re/kpc) from Table 2
2. Convert to physical effective radius in Mpc
3. Propagate uncertainties using standard error propagation
4. Compute star forming main sequence using Speagle et al. 2014 at each redshift
5. Assign selection criteria and main sequence offsets

### Limitations
- Some mass bins at high redshift have limited data (marked as NaN in original table)
- Scatter values (0.15 dex) are typical literature values, not from the original paper
- Main sequence classification uses the Speagle et al. 2014 parametrization

## Reproduction

To regenerate this dataset:

```bash
python scripts/create_vanderwel2014_mass_size.py
```

The script will:
1. Parse the data from Table 2
2. Create separate samples for star forming and quiescent galaxies
3. Compute main sequence SFRs using Speagle et al. 2014
4. Save in Galacticus format
5. Validate the output file

## Validation

The dataset has been validated against the Galacticus format requirements:
- ✓ All required attributes present
- ✓ Cosmology group with correct parameters
- ✓ Sample groups with proper selection criteria
- ✓ Main sequence SFR and offset for star forming/quiescent samples
- ✓ All datasets have correct units and descriptions

To validate:
```python
from shmr_datasets import validate_galacticus_mass_size_file

result = validate_galacticus_mass_size_file('vanderwel2014_mass_size.hdf5')
print(f"Valid: {result['valid']}")
```
