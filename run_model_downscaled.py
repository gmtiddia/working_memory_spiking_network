from model.model import WMModel
import matplotlib.pyplot as plt
import math
import os

# Script needed to run the model.
# Please choose the values of average external currents and the starting value of u

#         eta_ext   u0
# Fig 2A - 22.6  - 0.19 (single stable state activity)
# Fig 2B - 23.7  - 0.19 (bi-stable activity with synchronous spiking activity)
# Fig 2C - 24.1  - 0.19 (bi-stable activity with asynchronous spiking activity)

# average variation of membrane potential elicited by external current [mV]
eta_exc = 26.0 #25.0
# short-term plasticity variable u at the beginning of the simulation
u_start = 0.19

t_reac = 0.050 #0.100
a_reac = 1.5 #1.05
freq = 0.0
j_b = 0.1 #0.01
j_p = 2.3 #2.4

# network params dict
# here add the parameters to be edited. The rest of the parameters are in model/default_params.py
network_p = {
    # excitatory input current [mV]
    'eta_exc': eta_exc,
    # current used to go back to the spontaneous activity
    'eta_exc_end': 22.6 - eta_exc,
    # fraction of exc neurons for a selective pop (N = f* 8000)
    "f": 0.0025,
    "p": 5,
    # E->E
    "cEE": 0.5,
    # E->E within the same selective pop
    "cEEsp": 0.5,
    # E->I
    "cIE": 0.5,
    # I->E
    "cEI": 0.5,
    # I->I
    "cII": 0.5,
    'stimulation_params': {
    # item loading signal duration (default 350.0)
    "T_cue": 50.0,
    "A_cue": 2.0, #1.15
    # Reactivating signal
    # duration [ms]
    "T_reac": t_reac*1000.0,
    # contrast factor
    "A_reac": a_reac},
    "fr_eta": freq,
    # A = A_reac*eta_exc*pi*fr_eta*T_reac
    "A_eta": (a_reac-1.0)*eta_exc*math.pi*freq*t_reac,
    'neur_params' : {"tau_syn" : (2.5, 2.5, 2.0), # intra pop EE connections, inter pop EE connections, connections with I neurons
                    "tau": [15.0, 10.0]}, # tau_m (exc), tau_m (inh)
    'stp_params' : {'u0': u_start, 'tau_F': 1000.0, 'tau_D': 50.0},
    'syn_params' : {'autapses' : True, 'multapses' : True, 
                    'J_b': j_b, 
                    'J_p': j_p,
                    'J_II': 0.20,
                    # E->I
                    'J_IE': 0.15,
                    # I->E
                    'J_EI': 0.3}}

print("Frequency: {:.2f} Hz; Amplitude: {:.2f} mV".format(network_p["fr_eta"], network_p["A_eta"]))


# presimulation time (i.e. time in which the network stays in the spontaneous activity)
tpresim = 3000.0
# simulation time
tsim = 5000.0

# simulation params dict
# here add the parameters to be edited. The rest of the parameters are in default_params.py
simulation_p = {
    # path to data
    "data_path" : os.path.join(os.getcwd(), 'data_26mV/data_2A_ds20_750/'),
    # number of OpenMP threads
    "threads" : 8,
    # overall simulation time
    "t_sim" : tsim + tpresim,
    # beginning of th current stimulus which diminishes overall background input
    "eta_end_origin": tsim + tpresim - 0.0,
    "recording_params" : {
        # fraction of neurons recorded for each selective population
        "fraction_pop_recorded" : 1.0,
        # selective excitatory population recorded (0, ..., p-1)
        "pop_recorded" : "all",
        "spike_recording_params": {"start": 0.0},
        # save spike data to file
        "save_to_file" : True,
        # save STP data to file
        "stp_recording" : False,
        # recording step for STP recording [ms]
        "stp_record_interval" : 10.0,
        # selective population for which the STP params (i.e. x, u) will be recorded
        "stp_pop_recorded" : [0],#,1],
        # fraction of the selective population to be recorded for stp data
        "stp_fraction_recorded" : 0.1
    }
}

# initialize the network model
network = WMModel(network_p, simulation_p)

# add background
network.add_background_input(start=0.0, stop=tsim+tpresim)

# instructions to reproduce the plots shown in the article. Please choose the correct value of eta_exc and u0 and then untag the desired lines

# to reproduce Figure 2A
network.add_item_loading_signals(pop_id=[0], origin=[tpresim])
network.add_nonspecific_readout_signal(origin=[tpresim+750], specific=False, popids = [0])

# to reproduce Figure 2B and 2C
#network.add_item_loading_signals(pop_id=[0], origin=[tpresim])

# to reproduce Figure 3A
#network.add_item_loading_signals(pop_id=[0,1], origin=[tpresim,tpresim+3000.0])
# COMANDO MODIFICATO PER TARGETTARE UNA SOLA POPOLAZIONE SELETTIVA
#network.add_periodic_sequence(intervals=[[tpresim+700.0, tpresim+1300.0], [tpresim+2000.0, tpresim+2900.0], [tpresim+3400, tpresim+5000.0]], popid = [0, 0, 1])
#network.add_random_nonspecific_noise([tpresim+1550.0], frac = 0.15)

# to reproduce Figure 3B
#network.add_item_loading_signals(pop_id=[0,1], origin=[tpresim,tpresim+3000.0])
#network.add_random_nonspecific_noise([tpresim+1450.0], frac = 0.15)

# to reproduce Figure 3B with overlapping populations
#network.add_item_loading_signals(pop_id=[0,1], origin=[tpresim,tpresim+3000.0])
#network.add_random_nonspecific_noise([tpresim+1250.0], frac = 0.15)

# to reproduce Figure 4
#network.add_item_loading_signals(pop_id=[0,1,2], origin=[tpresim, tpresim+3000.0, tpresim+6000.0])
#network.add_item_loading_signals(pop_id=[0,1,2,3,4], origin=[tpresim, tpresim+500.0, tpresim+1000.0, tpresim+1500.0, tpresim+2000.0])

# save used parameters into a json
network.save_params()
# build network
network.build_network()
# simulate network
network.simulate_network()
# save data to file
network.save_spike_data()
#network.save_voltage_data()
# plots a raster plot of all the neurons recorded
network.raster_plot()
#plt.show()
