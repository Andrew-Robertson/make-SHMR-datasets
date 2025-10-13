# TRINITY Black Hole Mass - Halo Mass Relation

This directory contains the black hole mass - halo mass relation data from the TRINITY project.

## Dataset Information

**Source:** TRINITY (TRiple-peak Integrated emulator of Neutral gas, Ionization, and Temperature based on halo-galaxY connection)

**Repository:** https://github.com/HaowenZhang/TRINITY

**Reference:** Zhang et al. 2022, MNRAS, 518, 2123 (arXiv:2208.00719)

**Description:** Semi-empirical model that simultaneously constrains the stellar mass - halo mass relation and the black hole mass - halo mass relation using observations from the UV luminosity function, stellar mass function, and quasar luminosity function across redshifts 0-10.

## Files

- `fig14_median_BHHM_fit_z0-10.txt`: Raw data table containing the median black hole mass - peak halo mass relation from TRINITY Figure 14
- `trinity_bhmr.hdf5`: Black hole mass - halo mass relation in Galacticus-compatible HDF5 format

## Dataset Details

- **Redshift range:** z = 0.0 to 10.0
- **Number of redshift intervals:** 10
- **Total data points:** 78
- **Halo mass definition:** Virial (peak halo mass)
- **Cosmology:** Planck 2018 (Ω_M = 0.3111, Ω_Λ = 0.6889, Ω_b = 0.04897, H₀ = 67.66 km/s/Mpc)

## Redshift Intervals

1. z = 0.0 - 0.5 (9 points)
2. z = 0.5 - 1.0 (9 points)
3. z = 1.0 - 2.0 (9 points)
4. z = 2.0 - 3.0 (9 points)
5. z = 3.0 - 4.0 (9 points)
6. z = 4.0 - 5.0 (8 points)
7. z = 5.0 - 6.0 (7 points)
8. z = 6.0 - 7.0 (7 points)
9. z = 7.0 - 8.0 (6 points)
10. z = 8.0 - 10.0 (5 points)

## Usage with Galacticus

To use this dataset in Galacticus, add the following to your parameter file:

```xml
<blackHoleVsHaloMassRelation value="file">
  <fileNameTarget value="path/to/trinity_bhmr.hdf5"/>
</blackHoleVsHaloMassRelation>
```

## Data Provenance

The dataset was created using the script `scripts/create_trinity_bhmr.py` which:
1. Reads the raw TRINITY data from `fig14_median_BHHM_fit_z0-10.txt`
2. Groups data by redshift intervals
3. Converts logarithmic masses to linear masses
4. Adds appropriate uncertainties (0.3 dex for black hole masses, 0.1 dex for scatter)
5. Saves in Galacticus-compatible HDF5 format

## Notes

- The scatter values (σ_log10_Mbh) are directly from the TRINITY fits
- Error estimates for black hole masses are assumed to be 0.3 dex (typical observational uncertainty)
- Error estimates for scatter are assumed to be 0.1 dex (typical uncertainty in scatter measurements)
- This represents the **median** relation; TRINITY also provides percentile ranges that are not included here

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
