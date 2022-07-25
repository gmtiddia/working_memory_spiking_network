import math
import numpy as np

def get_weight(PSP_val, tau_m, C_m = 250.0, tau_syn_ex = 2.0):
    """ Computes weight to elicit a change in the membrane potential.
    Reference:
    [1] Potjans TC. and Diesmann M. 2014. The cell-type specific 
    cortical microcircuit: relating structure and activity in a 
    full-scale spiking network model. Cerebral Cortex. 
    24(3):785-806. DOI: 10.1093/cercor/bhs358.

    Parameters
    ----------
    PSP_val
        Evoked postsynaptic potential.
    net_dict
        Dictionary containing parameters of the microcircuit.

    Output
    -------
    PSC_e
        Weight value(s).
    """

    PSC_e_over_PSP_e = (((C_m) ** (-1) * tau_m * tau_syn_ex / (
        tau_syn_ex - tau_m) * ((tau_m / tau_syn_ex) ** (
            - tau_m / (tau_m - tau_syn_ex)) - (tau_m / tau_syn_ex) ** (
                - tau_syn_ex / (tau_m - tau_syn_ex)))) ** (-1))
    PSC_e = (PSC_e_over_PSP_e * PSP_val)

    return PSP_val
    #return PSC_e


def noise_params(mu_ext, sigma_ext, tau_m, dt=1.0, C_m=250., resolution = 0.1):
    """
    Returns mean and std for noise generator for parameters provided
    """

    V_mean = mu_ext*(resolution/tau_m)
    V_std = (sigma_ext / np.sqrt(( 1 - math.exp(-dt/tau_m) ) / ( 1 + math.exp(-dt/tau_m) )))*(resolution/tau_m)

    return V_mean, V_std

