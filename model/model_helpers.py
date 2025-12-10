import math

def get_weight(PSP_val:float, tau_m:float, C_m:float=250.0, tau_syn_ex:float=2.0):
    """ Computes weight to elicit a change in the membrane potential.
    Reference:
    [1] Potjans TC. and Diesmann M. 2014. The cell-type specific 
    cortical microcircuit: relating structure and activity in a 
    full-scale spiking network model. Cerebral Cortex. 
    24(3):785-806. DOI: 10.1093/cercor/bhs358.

    Args:
        PSP_valc (float): evoked postsynaptic potential.
        tau_m (float): membrane time constant.
        C_m (float, optional): membrane time constant (Defaults to 250.0).
        tau_syn_ex (float, optional): synaptic time constant (Defaults to 2.0).

    Returns:
        PSC_e (float): synaptic weight value.
    """

    PSC_e_over_PSP_e = (((C_m) ** (-1) * tau_m * tau_syn_ex / (
        tau_syn_ex - tau_m) * ((tau_m / tau_syn_ex) ** (
            - tau_m / (tau_m - tau_syn_ex)) - (tau_m / tau_syn_ex) ** (
                - tau_syn_ex / (tau_m - tau_syn_ex)))) ** (-1))
    PSC_e = (PSC_e_over_PSP_e * PSP_val)
    return PSC_e


def noise_params(mu_ext:float, sigma_ext:float, tau_m:float, dt:float=0.1, C_m:float=250.0):
    """
    Returns mean and std for noise generator for parameters provided;
    Default C_m for iaf_psc_exp is used.
    Reference: https://nest-simulator.readthedocs.io/en/v3.1/model_details/noise_generator.html

    Args:
        mu_ext (float): mean depolarization of the membrane.
        sigma_ext (float): standard deviation of membrane depolarization.
        tau_m (float): membrane time constant.
        dt (float, optional): timestep for signal changing. Defaults to 0.1.
        C_m (float, optional): membrane capacitance. Defaults to 250.0.

    Returns:
        (nu_ext, Sigma_ext): mean and standard deviation of the gaussian white noise current.
    """

    return (C_m / tau_m) * mu_ext, math.sqrt(2/(tau_m*dt))*C_m*sigma_ext


def get_rate_and_weight_poisson(eta:float, Sigma:float, tau_m:float, tau_syn:float=2.0, C_m:float=250., dt:float=0.1):
    """Returns the rate and the synaptic weight of a Poisson process able to elicit a depolarization of the membrane 
    designed as a Gaussian white noise.

    Args:
        eta (float): average membrane potential.
        Sigma (float): membrane potential standard deviation.
        tau_m (float): membrane time constant
        tau_syn (float, optional): synaptic time constant. Defaults to 2.0.
        C_m (float, optional): membrane capacitance. Defaults to 250..
        dt (float, optional): time interval at which the equivalent current would change. Defaults to 0.1.

    Returns:
        rate: rate of the Poisson process.
        weight: the synaptic weight modulated as a function of the Poisson process rate
    """
    mu, _ = noise_params(eta, Sigma, tau_m, dt, C_m)
    rate = (tau_m*mu/C_m)**2 /(2*(tau_m+tau_syn))
    weight = mu/(rate*tau_syn)

    print("Rate = {} Hz".format(rate*1000))

    return rate*1000, weight


def lognormal_params(mean:float, std:float):
    """Convert the mean and standard deviation of a lognormal distribution
    to the parameters of its underlying normal distribution.

    Args:
        mean (float): mean of the lognormal distribution.
        std (float): standard deviation of the lognormal distribution.

    Returns:
        mean_normal: mean of the underlying normal distribution ln(X).
        std_normal: standard deviation of the underlying normal distribution ln(X).

    """

    std_normal = math.sqrt(math.log((std / mean) ** 2 + 1.0))
    mean_normal = math.log(mean * math.exp(-(std_normal ** 2) / 2.0))

    return(mean_normal, std_normal)





