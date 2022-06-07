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
    # number of memories
    "p": 5,
    # probability of synaptic contact
    "c": 0.20,
    # number of exc cells 
    "N_exc": 8000,
    # number of inh cells 
    "N_inh": 2000,
    #mean external current [mV for exc population]
    # case A: single stable activity
    "mu_excA": 22.80,
    # case B: bistable regime synchronous
    "mu_excB": 23.70,
    # case C: bistable regime asynchronous
    "mu_excC": 24.00,
    # mean external current used in the simulation [mV for exc population]
    "mu_exc": 24.30,
    # mean external current used in the simulation [mV for inh population]
    "mu_inh": 20.5,
    # current offset to return at stable state
    "mu_exc_end": 24.30 - 22.8,
    # std of external current
    "sigma_exc": 1.0,
    "sigma_inh": 1.0}

"""
Single-cell parameters
"""

default_neur_params = {
    # spike emission threshold [mV]
    "V_th": [20.0, 20.0],
    # reset potential [mV]
    "V_reset": [16.0, 13.0], 
    # membrane time constant [ms]
    "tau": [15.0, 10.0],
    # absolute refractory period [ms]
    "t_ref": [2.0, 2.0],
    # resting potential [mV]
    "E_L": [0.0, 0.0],
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
    "delay_ext": [0.1, 1.0]}

default_network_params.update({'syn_params': default_syn_params})

"""
STP parameters
"""
default_stp_params = {
    # baseline utilization factor
    "U": 0.19,
    # u value at the beginning
    "u0" : 0.25,
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
    "master_seed" : 123456,
    # number of threads
    "threads" : 1,
    # simulation step (in ms)
    "dt" : 0.1,
    # simulated time (in ms)
    "t_sim" : 5000.0,
    # offset origin [ms]
    "mu_end_origin": 4500.0,
    "recording_params" : {
        # fraction of neurons recorded for each population
        "fraction_pop_recorded" : 0.1,
        # selective excitatory population recorded (0, ..., p-1)
        "pop_recorded" : [0, 1],
        "spike_recording_params": {"start": 50.0},
        # save spike times
        "save_to_file" : True,
        # save short-term plasticity (STP) data
        "stp_recording" : False,
        # intervak for STP recording
        "stp_record_interval" : 25.0,
        # populations for which the STP params have to be recorded
        "stp_pop_recorded" : [0],
        # fraction of neurons of a population for which STP params have to be recorded
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
