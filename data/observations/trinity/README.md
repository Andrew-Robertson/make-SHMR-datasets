# TRINITY Black Hole Mass - Halo Mass Relation

This directory contains the black hole mass - halo mass relation data from the TRINITY project.

## Dataset Information

**Source:** TRINITY (TRiple-peak Integrated emulator of Neutral gas, Ionization, and Temperature based on halo-galaxY connection)

**Repository:** https://github.com/HaowenZhang/TRINITY

**Data URL:** https://github.com/HaowenZhang/TRINITY/blob/main/plot_data/Paper1/fig14_median_BHHM_z%3D0-10/fig14_median_BHHM_fit_z%3D0-10.dat

**Reference:** Zhang et al. 2022, MNRAS, 518, 2123 (arXiv:2208.00719)

**Description:** Semi-empirical model that simultaneously constrains the stellar mass - halo mass relation and the black hole mass - halo mass relation using observations from the UV luminosity function, stellar mass function, and quasar luminosity function across redshifts 0-10.

## Files

- `fig14_median_BHHM_fit_z0-10.dat`: Raw data downloaded from TRINITY repository containing median black hole mass - peak halo mass relation from Figure 14
- `trinity_bhmr.hdf5`: Black hole mass - halo mass relation in Galacticus-compatible HDF5 format

## Dataset Details

- **Redshift range:** z = 0.0 to 10.5
- **Number of redshift intervals:** 11
- **Total data points:** 88
- **Halo mass definition:** Virial (peak halo mass)
- **Cosmology:** Planck 2018 (Ω_M = 0.3111, Ω_Λ = 0.6889, Ω_b = 0.04897, H₀ = 67.66 km/s/Mpc)

## Redshift Intervals

Redshift bins are calculated such that each bin covers the range where that redshift is the closest output:

1. z = 0.00 - 0.55 (13 points)
2. z = 0.55 - 1.50 (12 points)
3. z = 1.50 - 2.50 (11 points)
4. z = 2.50 - 3.50 (10 points)
5. z = 3.50 - 4.50 (9 points)
6. z = 4.50 - 5.50 (8 points)
7. z = 5.50 - 6.50 (7 points)
8. z = 6.50 - 7.50 (6 points)
9. z = 7.50 - 8.50 (5 points)
10. z = 8.50 - 9.50 (4 points)
11. z = 9.50 - 10.50 (3 points)

## Usage with Galacticus

To use this dataset in Galacticus, add the following to your parameter file:

```xml
<blackHoleVsHaloMassRelation value="file">
  <fileNameTarget value="path/to/trinity_bhmr.hdf5"/>
</blackHoleVsHaloMassRelation>
```

## Data Provenance

The dataset was created using the script `scripts/create_trinity_bhmr.py` which:
1. Downloads the raw TRINITY data from the GitHub repository (if not already present)
2. Parses the TRINITY output format with columns: z, log10(Mpeak), log10(Mbh_median), log10(16th percentile), log10(84th percentile)
3. Calculates redshift bin edges so each bin covers the range where that redshift is closest
4. Converts logarithmic masses to linear masses
5. Calculates black hole mass errors from the 16th-84th percentile range
6. Adds assumed scatter values (TRINITY does not provide intrinsic scatter)
7. Saves in Galacticus-compatible HDF5 format

## Notes on Data Processing

- **Black hole masses**: Median values from TRINITY model
- **BH mass errors**: Half the 16th-84th percentile range from TRINITY posteriors
- **Scatter**: Assumed value of 0.3 dex (TRINITY does not provide intrinsic scatter information)
- **Scatter error**: Assumed value of 0.2 dex (typical uncertainty in scatter measurements)
- **Redshift bins**: Calculated to cover ranges where each redshift is the closest output (e.g., z=0.1 bin covers [0, 0.55])
- This represents the **median** relation from the TRINITY model posteriors

## Citation

If you use this dataset, please cite:

```
@article{Zhang2022,
  author = {Zhang, Haowen and Behroozi, Peter and Volonteri, Marta and Silk, Joseph and Fan, Xiaohui and Hopkins, Philip F. and Pfister, Hugo and Harikane, Yuichi},
  title = {TRINITY: A Trinity of galaxy-halo-black hole connection},
  journal = {MNRAS},
  volume = {518},
  pages = {2123},
  year = {2022},
  doi = {10.1093/mnras/stac2633},
  archivePrefix = {arXiv},
  eprint = {2208.00719}
}
```
