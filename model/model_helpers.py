import math

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
    return PSC_e


def noise_params(eta_ext, Sigma_ext, tau_m, dt=0.1, C_m=250.):
    """
    Returns mean and std for noise generator for parameters provided;
    Default C_m for iaf_psc_exp.
    Reference: https://nest-simulator.readthedocs.io/en/v3.1/model_details/noise_generator.html
    """

    return (C_m / tau_m) * eta_ext, math.sqrt(2/(tau_m*dt))*C_m*Sigma_ext


