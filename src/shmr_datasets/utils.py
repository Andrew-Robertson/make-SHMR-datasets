"""
Utility functions for SHMR calculations and manipulations compatible with Galacticus.

This module provides functions for calculating SHMR from parametric forms,
interpolating between data points, and creating Galacticus-compatible datasets.
"""

import numpy as np
from scipy import interpolate
from typing import Union, Callable, Optional, Tuple, Dict, Any
from dataclasses import dataclass

from .data_format import (
    GalacticusSHMRData, 
    RedshiftInterval, 
    GalacticusCosmology,
    create_example_cosmology
)


def calculate_shmr(
    halo_masses: np.ndarray,
    shmr_function: Union[str, Callable],
    redshift: float = 0.0,
    redshift_width: float = 0.1,
    cosmology: Optional[GalacticusCosmology] = None,
    parameters: Optional[Dict[str, float]] = None,
    halo_mass_definition: str = "virial",
    label: str = "SHMR",
    reference: str = "Generated SHMR",
    scatter: Optional[np.ndarray] = None,
    stellar_mass_errors: Optional[np.ndarray] = None,
    **kwargs
) -> GalacticusSHMRData:
    """
    Calculate SHMR from a parametric function in Galacticus format.
    
    Parameters
    ----------
    halo_masses : array_like
        Array of halo masses to evaluate SHMR at (in M☉)
    shmr_function : str or callable
        Either a string specifying a known SHMR form or a custom function
    parameters : dict
        Parameters for the SHMR function
    redshift : float, optional
        Central redshift for the relation (default: 0.0)
    redshift_width : float, optional
        Width of redshift interval (default: 0.1)
    cosmology : GalacticusCosmology, optional
        Cosmological parameters (default: Planck 2018)
    halo_mass_definition : str, optional
        Halo mass definition (default: "virial")
    label : str, optional
        Dataset label (default: "SHMR")
    reference : str, optional
        Reference for the relation (default: "Generated SHMR")
    scatter : array_like, optional
        Intrinsic scatter in log stellar mass in dex (default: 0.16 dex)
    stellar_mass_errors : array_like, optional
        Observational errors in stellar mass (default: 10%)
    **kwargs
        Additional parameters passed to SHMR function
        
    Returns
    -------
    GalacticusSHMRData
        Calculated SHMR data in Galacticus format
    """
    halo_masses = np.asarray(halo_masses)
    
    if parameters is None:
        parameters = {}

    if isinstance(shmr_function, str):
        if shmr_function == "behroozi2010":
            stellar_masses = behroozi2010_shmr(halo_masses, **parameters)
        elif shmr_function == "behroozi2013":
            stellar_masses = behroozi2013_shmr(halo_masses, **parameters)
        elif shmr_function == "moster2013":
            stellar_masses = moster2013_shmr(halo_masses, **parameters)
        elif shmr_function == "rodriguez_puebla2017":
            stellar_masses = rodriguez_puebla2017_shmr(halo_masses, **parameters)
        elif shmr_function == "double_powerlaw":
            stellar_masses = double_powerlaw_shmr(halo_masses, **parameters)
        else:
            raise ValueError(f"Unknown SHMR function: {shmr_function}")
    else:
        stellar_masses = shmr_function(halo_masses, **parameters)
    
    # Set default cosmology if not provided
    if cosmology is None:
        cosmology = create_example_cosmology()
    
    # Set default scatter and errors if not provided
    if scatter is None:
        scatter = np.full(len(halo_masses), 0.16)  # 0.16 dex default scatter
    else:
        scatter = np.asarray(scatter)
        if scatter.shape != halo_masses.shape:
            scatter = np.full(len(halo_masses), scatter.item() if scatter.size == 1 else scatter)
    
    if stellar_mass_errors is None:
        stellar_mass_errors = np.full(len(halo_masses), 0.1)  # 0.1 dex default error
    else:
        stellar_mass_errors = np.asarray(stellar_mass_errors)
        if stellar_mass_errors.shape != halo_masses.shape:
            stellar_mass_errors = np.full(len(halo_masses), stellar_mass_errors.item() if stellar_mass_errors.size == 1 else stellar_mass_errors)
    
    # Default scatter errors (typically much smaller)
    scatter_errors = np.full(len(halo_masses), 0.04)  # 0.04 dex scatter error
    
    # Create redshift interval
    redshift_interval = RedshiftInterval(
        massHalo=halo_masses,
        massStellar=stellar_masses,
        massStellarError=stellar_mass_errors,
        massStellarScatter=scatter,
        massStellarScatterError=scatter_errors,
        redshiftMinimum=redshift - redshift_width/2,
        redshiftMaximum=redshift + redshift_width/2
    )
    
    return GalacticusSHMRData(
        redshift_intervals=[redshift_interval],
        cosmology=cosmology,
        haloMassDefinition=halo_mass_definition,
        label=label,
        reference=reference
    )


def interpolate_shmr(
    shmr_data: GalacticusSHMRData,
    new_halo_masses: np.ndarray,
    redshift_interval_index: int = 0,
    method: str = "linear",
    extrapolate: bool = False
) -> GalacticusSHMRData:
    """
    Interpolate SHMR to new halo mass points for Galacticus format.
    
    Parameters
    ----------
    shmr_data : GalacticusSHMRData
        Original SHMR data
    new_halo_masses : array_like
        New halo masses to interpolate to
    redshift_interval_index : int, optional
        Index of redshift interval to interpolate (default: 0)
    method : str, optional
        Interpolation method ("linear", "cubic", "log-linear")
    extrapolate : bool, optional
        Whether to allow extrapolation beyond original data range
        
    Returns
    -------
    GalacticusSHMRData
        Interpolated SHMR data in Galacticus format
    """
    new_halo_masses = np.asarray(new_halo_masses)
    
    if redshift_interval_index >= len(shmr_data.redshift_intervals):
        raise ValueError(f"Redshift interval index {redshift_interval_index} out of range")
    
    interval = shmr_data.redshift_intervals[redshift_interval_index]
    
    if method == "log-linear":
        # Interpolate in log space
        log_halo = np.log10(interval.massHalo)
        log_stellar = np.log10(interval.massStellar)
        log_new_halo = np.log10(new_halo_masses)
        
        interp_func = interpolate.interp1d(
            log_halo, log_stellar, 
            kind="linear",
            bounds_error=not extrapolate,
            fill_value="extrapolate" if extrapolate else np.nan
        )
        
        new_stellar_masses = 10**interp_func(log_new_halo)
        
    else:
        interp_func = interpolate.interp1d(
            interval.massHalo, interval.massStellar,
            kind=method,
            bounds_error=not extrapolate,
            fill_value="extrapolate" if extrapolate else np.nan
        )
        
        new_stellar_masses = interp_func(new_halo_masses)
    
    # Interpolate other quantities
    error_interp = interpolate.interp1d(
        interval.massHalo, interval.massStellarError,
        kind="linear", bounds_error=not extrapolate,
        fill_value="extrapolate" if extrapolate else np.nan
    )
    scatter_interp = interpolate.interp1d(
        interval.massHalo, interval.massStellarScatter,
        kind="linear", bounds_error=not extrapolate,
        fill_value="extrapolate" if extrapolate else np.nan
    )
    scatter_error_interp = interpolate.interp1d(
        interval.massHalo, interval.massStellarScatterError,
        kind="linear", bounds_error=not extrapolate,
        fill_value="extrapolate" if extrapolate else np.nan
    )
    
    new_errors = error_interp(new_halo_masses)
    new_scatter = scatter_interp(new_halo_masses)
    new_scatter_errors = scatter_error_interp(new_halo_masses)
    
    # Create new redshift interval
    new_interval = RedshiftInterval(
        massHalo=new_halo_masses,
        massStellar=new_stellar_masses,
        massStellarError=new_errors,
        massStellarScatter=new_scatter,
        massStellarScatterError=new_scatter_errors,
        redshiftMinimum=interval.redshiftMinimum,
        redshiftMaximum=interval.redshiftMaximum
    )
    
    return GalacticusSHMRData(
        redshift_intervals=[new_interval],
        cosmology=shmr_data.cosmology,
        haloMassDefinition=shmr_data.haloMassDefinition,
        label=f"{shmr_data.label}_interpolated",
        reference=f"{shmr_data.reference} (interpolated using {method} method)"
    )


def behroozi2010_shmr(
    halo_mass: np.ndarray,
    redshift: float = 0.0,
    logMstar00: float = 10.72,
    logMstar0a: float = 0.59,
    logM10: float = 12.35,
    logM1a: float = 0.30,
    beta0: float = 0.43,
    betaa: float = 0.18,
    delta0: float = 0.56,
    deltaa: float = 0.18,
    gamma0: float = 1.54,
    gammaa: float = 2.52,
) -> np.ndarray:
    """
    Calculate the Stellar-to-Halo Mass Relation (SHMR) using the parametrization from Behroozi et al. (2010).

    This function computes the stellar mass corresponding to a given halo mass at a specified redshift,
    based on the empirical relations derived in Behroozi et al. 2010 (arXiv:1001.0015). The parameters
    used in the calculation can be adjusted to fit different scenarios or datasets.

    Parameters
    ----------
    halo_mass : np.ndarray
        An array of halo masses in solar masses for which the stellar masses are to be calculated.
    redshift : float, optional
        The redshift at which to calculate the SHMR (default is 0.0).
    logMstar00 : float, optional
        The initial value for the stellar mass relation (default is 10.72).
    logMstar0a : float, optional
        The redshift evolution parameter for stellar mass (default is 0.59).
    logM10 : float, optional
        The characteristic halo mass (default is 12.35).
    logM1a : float, optional
        The redshift evolution parameter for halo mass (default is 0.30).
    beta0 : float, optional
        The initial value for the beta parameter (default is 0.43).
    betaa : float, optional
        The redshift evolution parameter for beta (default is 0.18).
    delta0 : float, optional
        The initial value for the delta parameter (default is 0.56).
    deltaa : float, optional
        The redshift evolution parameter for delta (default is 0.18).
    gamma0 : float, optional
        The initial value for the gamma parameter (default is 1.54).
    gammaa : float, optional
        The redshift evolution parameter for gamma (default is 2.52).

    Returns
    -------
    np.ndarray
        An array of stellar masses in solar masses corresponding to the input halo masses.

    Notes
    -----
    The default parameters are based on the values provided in Behroozi et al. (2010). The function
    inverts the relationship presented by Behroozi to derive stellar masses from halo masses.
    """
    a = 1.0/(1.0+redshift)
    logm0 = logMstar00 + logMstar0a*(a - 1.0)
    logm1 = logM10 + logM1a*(a - 1.0)
    beta  = beta0 + betaa*(a - 1.0)
    delta = delta0 + deltaa*(a - 1.0)
    gamma = gamma0 + gammaa*(a - 1.0)

    # Behroozi present a relationship for Mh(Mstar) (not Mstar(Mh)), so we need to invert it
    def logMh_from_logMstar(logMstar=np.linspace(4.0, 14.0, 5001)):
        Mstar = 10**logMstar
        ratio = Mstar / (10**logm0)
        term3 = (ratio**delta) / (1.0 + ratio**(-gamma))
        logMh = logm1 + beta*np.log10(Mstar / (10**logm0)) + term3 - 0.5 # (eq.21)
        return logMh

    logMstar_table=np.linspace(4.0, 14.0, 5001)
    logMh_table = logMh_from_logMstar(logMstar_table)
    logMh_target = np.log10(halo_mass)
    logMstar = np.interp(logMh_target, logMh_table, logMstar_table)

    return 10**logMstar


def behroozi2013_shmr(
    halo_mass: np.ndarray,
    log_m1: float = 12.35,
    ms0: float = 10.72,
    beta: float = 0.44,
    delta: float = 0.57,
    gamma: float = 1.56
) -> np.ndarray:
    """
    Calculate SHMR using Behroozi+ 2013 parametrization.
    
    Parameters:
    -----------
    halo_mass : array_like
        Halo masses in solar masses
    log_m1 : float
        Characteristic halo mass (log10)
    ms0 : float
        Normalization (log10 stellar mass)
    beta : float
        Low-mass slope
    delta : float
        High-mass slope
    gamma : float
        Turnover sharpness
        
    Returns:
    --------
    np.ndarray
        Stellar masses in solar masses
    """
    log_mh = np.log10(halo_mass)
    x = log_mh - log_m1
    
    f = -np.log10(10**(beta * x) + 1) + delta * (np.log10(1 + np.exp(x)))**gamma / (1 + np.exp(10**(-x)))
    
    log_ms = ms0 + f
    return 10**log_ms


def moster2013_shmr(
    halo_mass: np.ndarray,
    m1: float = 1.87e12,
    n10: float = 0.0351,
    beta: float = 1.376,
    gamma: float = 0.608
) -> np.ndarray:
    """
    Calculate SHMR using Moster+ 2013 parametrization.
    
    Parameters:
    -----------
    halo_mass : array_like
        Halo masses in solar masses
    m1 : float
        Characteristic halo mass
    n10 : float
        Normalization
    beta : float
        Low-mass slope
    gamma : float
        High-mass slope
        
    Returns:
    --------
    np.ndarray
        Stellar masses in solar masses
    """
    x = halo_mass / m1
    efficiency = 2 * n10 / (x**(-beta) + x**gamma)
    return efficiency * halo_mass


def rodriguez_puebla2017_shmr(
    halo_mass: np.ndarray,
    log_m1: float = 12.52,
    log_eps: float = -1.777,
    alpha: float = 2.133,
    beta: float = 0.484,
    gamma: float = 1.077
) -> np.ndarray:
    """
    Calculate SHMR using Rodriguez-Puebla+ 2017 parametrization.
    
    Parameters:
    -----------
    halo_mass : array_like
        Halo masses in solar masses
    log_m1 : float
        Characteristic halo mass (log10)
    log_eps : float
        Peak efficiency (log10)
    alpha : float
        Low-mass slope
    beta : float
        High-mass slope  
    gamma : float
        Turnover sharpness
        
    Returns:
    --------
    np.ndarray
        Stellar masses in solar masses
    """
    log_mh = np.log10(halo_mass)
    x = log_mh - log_m1
    
    log_eps_eff = log_eps - 0.5 * ((x/gamma)**2) / (1 + (x/gamma)**2)
    f = (x**alpha) / (1 + x**beta)
    
    log_ms = log_mh + log_eps_eff + f
    return 10**log_ms


def double_powerlaw_shmr(
    halo_mass: np.ndarray,
    ms_norm: float = 1e10,
    mh_norm: float = 1e12,
    alpha_low: float = 1.0,
    alpha_high: float = -0.5
) -> np.ndarray:
    """
    Calculate SHMR using a simple double power law.
    
    Parameters:
    -----------
    halo_mass : array_like
        Halo masses in solar masses
    ms_norm : float
        Stellar mass normalization
    mh_norm : float
        Halo mass normalization
    alpha_low : float
        Power law index for low masses
    alpha_high : float
        Power law index for high masses
        
    Returns:
    --------
    np.ndarray
        Stellar masses in solar masses
    """
    x = halo_mass / mh_norm
    
    stellar_mass = np.zeros_like(halo_mass)
    
    low_mask = halo_mass < mh_norm
    high_mask = halo_mass >= mh_norm
    
    stellar_mass[low_mask] = ms_norm * (x[low_mask]**alpha_low)
    stellar_mass[high_mask] = ms_norm * (x[high_mask]**alpha_high)
    
    return stellar_mass


def scatter_relation(
    base_stellar_mass: np.ndarray,
    scatter_model: str = "lognormal",
    sigma: float = 0.15,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Add scatter to a stellar mass relation.
    
    Parameters:
    -----------
    base_stellar_mass : array_like
        Base stellar masses without scatter
    scatter_model : str
        Type of scatter ("lognormal", "gaussian")
    sigma : float
        Scatter amplitude (dex for lognormal)
    seed : int, optional
        Random seed for reproducibility
        
    Returns:
    --------
    np.ndarray
        Stellar masses with scatter
    """
    if seed is not None:
        np.random.seed(seed)
    
    base_stellar_mass = np.asarray(base_stellar_mass)
    
    if scatter_model == "lognormal":
        log_ms = np.log10(base_stellar_mass)
        scattered_log_ms = log_ms + np.random.normal(0, sigma, size=log_ms.shape)
        return 10**scattered_log_ms
    elif scatter_model == "gaussian":
        return base_stellar_mass + np.random.normal(0, sigma, size=base_stellar_mass.shape)
    else:
        raise ValueError(f"Unknown scatter model: {scatter_model}")


def convert_units(
    masses: np.ndarray,
    input_units: str,
    output_units: str,
    h: float = 0.7
) -> np.ndarray:
    """
    Convert mass units.
    
    Parameters:
    -----------
    masses : array_like
        Input masses
    input_units : str
        Input units ("Msun", "Msun/h", "kg")
    output_units : str  
        Output units ("Msun", "Msun/h", "kg")
    h : float
        Hubble parameter (for h-dependent conversions)
        
    Returns:
    --------
    np.ndarray
        Converted masses
    """
    masses = np.asarray(masses)
    
    # Convert to solar masses first
    if input_units == "Msun/h":
        masses_msun = masses / h
    elif input_units == "kg":
        masses_msun = masses / 1.989e30  # kg to solar masses
    elif input_units == "Msun":
        masses_msun = masses
    else:
        raise ValueError(f"Unknown input units: {input_units}")
    
    # Convert from solar masses to output units
    if output_units == "Msun/h":
        return masses_msun * h
    elif output_units == "kg":
        return masses_msun * 1.989e30
    elif output_units == "Msun":
        return masses_msun
    else:
        raise ValueError(f"Unknown output units: {output_units}")


def calculate_stellar_mass_function(
    shmr_data: GalacticusSHMRData,
    halo_mass_function: Callable,
    log_mass_bins: np.ndarray,
    redshift_interval_index: int = 0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate stellar mass function from SHMR and halo mass function.
    
    Parameters
    ----------
    shmr_data : GalacticusSHMRData
        SHMR data in Galacticus format
    halo_mass_function : callable
        Function that takes halo mass and returns dn/dlog(Mh)
    log_mass_bins : array_like
        Stellar mass bins (log10)
    redshift_interval_index : int, optional
        Index of redshift interval to use (default: 0)
        
    Returns
    -------
    tuple
        (stellar_mass_centers, number_density)
    """
    if redshift_interval_index >= len(shmr_data.redshift_intervals):
        raise ValueError(f"Redshift interval index {redshift_interval_index} out of range")
    
    interval = shmr_data.redshift_intervals[redshift_interval_index]
    
    # Create interpolation function for SHMR
    shmr_interp = interpolate.interp1d(
        np.log10(interval.massHalo),
        np.log10(interval.massStellar),
        kind='linear',
        bounds_error=False,
        fill_value=np.nan
    )
    
    # Calculate stellar mass function
    mass_centers = (log_mass_bins[:-1] + log_mass_bins[1:]) / 2
    number_density = np.zeros_like(mass_centers)
    
    # For each stellar mass bin, find corresponding halo masses
    for i, log_ms in enumerate(mass_centers):
        # Find halo masses that map to this stellar mass
        # This is a simplified approach - more sophisticated methods exist
        log_mh_range = np.linspace(10, 16, 1000)
        log_ms_pred = shmr_interp(log_mh_range)
        
        # Find halo masses within this stellar mass bin
        mask = ((log_ms_pred >= log_mass_bins[i]) & 
                (log_ms_pred < log_mass_bins[i+1]) &
                (~np.isnan(log_ms_pred)))
        
        if np.any(mask):
            mh_values = 10**log_mh_range[mask]
            hmf_values = halo_mass_function(mh_values)
            
            # Jacobian for transformation
            dlogms_dlogmh = np.gradient(log_ms_pred[mask])
            valid_jac = dlogms_dlogmh > 0
            
            if np.any(valid_jac):
                number_density[i] = np.trapz(
                    hmf_values[valid_jac] / dlogms_dlogmh[valid_jac],
                    log_mh_range[mask][valid_jac]
                )
    
    return 10**mass_centers, number_density