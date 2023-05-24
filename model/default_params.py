"""
Network and simulation parameters
"""

import os

"""
Network parameters
"""

default_network_params = {
    # coding level [fraction of exc neurons for each memory item]
    "f": 0.10,
    # possibility of overlap between populations
    "overlap": False,
    # inhibition: can be "classic" or "new"
    "inhibition": "classic",
    # number of memories
    "p": 5,
    # probability of synaptic contact for E->E connections
    "cEE": 0.20,
    # probability of synaptic contact for neurons belonging to the same selective population
    "cEEsp": 0.20,
    # probability of synaptic contact for E->I connections
    "cIE": 0.20,
    # probability of synaptic contact for I->E connections
    "cEI": 0.20,
    # probability of synaptic contact for I->I connections
    "cII": 0.20,
    # number of exc cells 
    "N_exc": 8000,
    # number of inh cells 
    "N_inh": 2000,
    # frequency of the external current
    "fr_eta": 15.0,
    # amplitude of the external current (A_eta*eta_exc)
    "A_eta": 1.05,
    # mean external current [mV for exc population]
    # case A: single stable activity
    "eta_excA": 22.70,
    # case B: bistable regime synchronous
    "eta_excB": 23.70,
    # case C: bistable regime asynchronous
    "eta_excC": 24.10,
    # mean external current used in the simulation [mV for exc population]
    "eta_exc": 23.70,
    # mean external current used in the simulation [mV for inh population]
    "eta_inh": 20.5,
    # current offset to return at stable state
    "eta_exc_end": 23.70 - 22.70,
    # std of external current [mV]
    "Sigma_exc": 1.0,
    "Sigma_inh": 1.0}

"""
Single-cell parameters
"""

default_neur_params = {
    # spike emission threshold [mV]
    "V_th": [20.0, 20.0],
    # reset potential [mV]
    "V_reset": [0.0, 0.0],#[16.0, 13.0], 
    # membrane time constant [ms]
    "tau": [15.0, 10.0],
    # absolute refractory period [ms]
    "t_ref": [2.0, 2.0],
    # resting potential [mV]
    "E_L": [0.0, 0.0],
    # synaptic time constants for excitatory synapses (intra EE, inter EE, inh connections)
    "tau_syn" : (2.0, 2.0, 2.0),
    # membrane potential at the beginning of the simulation [mV]
    "V_m": [0.0, 0.0]}

default_network_params.update({'neur_params': default_neur_params})

"""
Synaptic parameters
"""

default_syn_params = {
    # synaptic efficacy E->I [mV]
    "J_IE": 0.135,
    # synaptic efficacy I->E [mV]
    "J_EI": 0.25,
    # synaptic efficacy I->I [mV]
    "J_II": 0.20,
    # baseline level of E->E synapses [mV]
    "J_b": 0.10,
    # potentiated level of E->E synapses [mV]
    "J_p": 0.45,
    # fraction of potentiated synapses before learning
    "gamma_0": 0.10,
    # synaptic delays [ms, from min to max]
    "delay": [0.1, 1.0],
    # external current delays [ms, from min to max]
    "delay_ext": [0.1, 1.0],
    # possibility of doing self-connections
    "autapses" : True,
    # possibility of having multiple connections within two neurons
    "multapses" : True}

default_network_params.update({'syn_params': default_syn_params})

"""
STP parameters
"""
default_stp_params = {
    # baseline utilization factor
    "U": 0.19,
    # u value at the beginning
    "u0" : 0.19,
    # x value at the beginning
    "x0" : 1.0,
    # recovery time of utilization factor [ms]
    "tau_F": 1500.0,
    # recovery time of synaptic resources [ms]
    "tau_D": 200.0}

default_network_params.update({'stp_params': default_stp_params})

"""
Stimulation parameters
"""

default_stim_params = {
    # for a selective stimulation
    # duration [ms]
    "T_cue": 350.0,
    # contrast factor
    "A_cue": 1.15,
    # Reactivating signal
    # duration [ms]
    "T_reac": 250.0,
    # contrast factor
    "A_reac": 1.05,
    # Periodic reactivating signal
    # duration [ms]
    "T_period_reac": 100.0,
    # period
    "period": 300.0,
    # contrast factor
    "A_period_reac": 1.075,
    # current change interval [ms]
    "dt_external_stim": 1.0}

default_network_params.update({'stimulation_params': default_stim_params})

"""
Simulation parameters
"""

default_simulation_params = {
    # master seed for random number generators
    "master_seed" : 143202461,
    # number of threads
    "threads" : 8,
    # simulation step (in ms)
    "dt" : 0.05,
    # simulated time (in ms)
    "t_sim" : 6000.0,
    # offset origin [ms]
    "eta_end_origin": 5200.0,
    "recording_params" : {
        # fraction of neurons recorded for each population
        "fraction_pop_recorded" : 0.1,
        # selective excitatory population recorded "all", or a list to record selective pops [0, 1, ...]
        "pop_recorded" : "all",
        "spike_recording_params": {"start": 50.0},
        # save spike times
        # if pop_recorded = "all", non selective population and inhibitory population would be the
        # last two .dat files (e.g. spikedata5.dat & spikedata6.dat)
        "save_to_file" : True,
        # record membrane potential
        # it will be frecorded from a fraction of
        # neurons from each selective population
        "record_membrane_potential" : False,
        # fraction of neurons recorded
        "fraction_neurons_membrane_potential_redorded": 0.01,
        # fraction of 
        # save short-term plasticity (STP) data
        "stp_recording" : False,
        # intervak for STP recording
        "stp_record_interval" : 10.0,
        # populations for which the STP params have to be recorded
        "stp_pop_recorded" : [0],
        # fraction of neurons of a population for which STP params have to be recorded
        # choose 1.0 to have smooth lines for STP variables
        "stp_fraction_recorded" : 0.1},
    # path in which simulation data will be saved 
    "data_path" : os.path.join(os.getcwd(), 'data/'),
    "overwrite_files": True
}

"""
Update default parameters with custom parameters
"""

def update_params(d, d2):
    for key in d2:
        if isinstance(d2[key], dict) and key in d:
            update_params(d[key], d2[key])
        else:
            d[key] = d2[key]


# check custom params correctness
def check_params(d, def_d):
    for key, val in d.items():
        if isinstance(val, dict):
            check_params(d[key], def_d[key])
        else:
            try:
                def_val = def_d[key]
            except KeyError:
                raise KeyError('Custom key {} not used.'.format(key))
