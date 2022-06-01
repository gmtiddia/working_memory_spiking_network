from model.model import WMModel
import matplotlib.pyplot as plt
import os

# Script needed to run the model.
# Please choose the values of average external currents and the starting value of u

#         mu_ext   u0
# Fig 2A - 22.8 - 0.25 (single stable state activity)
# Fig 2B - 23.7 - 0.29 (bi-stable activity with synchronous spiking activity)
# Fig 2C - 24.0 - 0.29 (bi-stable activity with asynchronous spiking activity)

# average external current expressed in the average variation 
# of membrane potential elicited [mV]
mu_exc = 23.7
# short-term plasticity variable u at the beginning of the simulation
u_start = 0.29

# network params dict
# here add the parameters to be edited. The rest of the parameters are in default_params.py
network_p = {
    # excitatory input current [mV]
    'mu_exc': mu_exc,
    # current used to go back to the spontaneous activity
    'mu_exc_end': 22.8 - mu_exc,
    'stp_params' : {'u0': u_start}}


# presimulation time (i.e. time in which the network stays in the spontaneous activity)
tpresim = 2000.0
# simulation time
tsim = 4000.0

# simulation params dict
# here add the parameters to be edited. The rest of the parameters are in default_params.py
simulation_p = {
    # path to data
    "data_path" : os.path.join(os.getcwd(), 'data/'),
    # overall simulation time
    "t_sim" : tsim + tpresim,
    # beginning of th current stimulus which diminishes overall background input
    "mu_end_origin": tsim + tpresim - 1.0,
    "recording_params" : {
        # fraction of neurons recorded for each selective population
        "fraction_pop_recorded" : 1.0,
        # selective excitatory population recorded (0, ..., p-1)
        "pop_recorded" : [0, 1, 2, 3, 4],
        "spike_recording_params": {"start": 50.0},
        # save spike data to file
        "save_to_file" : True,
        # save STP data to file
        "stp_recording" : False,
        # recording step for STP recording [ms], min 2.0
        "stp_record_interval" : 10.0,
        # selective population for which the STP params (i.e. x, u) will be recorded
        "stp_pop_recorded" : [0,1],
        # fraction of the selective population to be recorded for stp data
        "stp_fraction_recorded" : 0.1
    }
}

# initialize the network model
network = WMModel(network_p, simulation_p)

# add background
network.add_background_input(start=0.0, stop=tsim+tpresim)

# instructions to reproduce the plots shown in the article. Please choose the correct value of mu_exc and u0 and then untag the desired lines

# to reproduce Figure 2A
#network.add_item_loading_signals(pop_id=[0], origin=[tpresim])
#network.add_nonspecific_readout_signal(origin=[tpresim+950.0])

# to reproduce Figure 2B and 2C
network.add_item_loading_signals(pop_id=[0], origin=[tpresim])

# to reproduce Figure 3A
#network.add_item_loading_signals(pop_id=[0,1], origin=[tpresim,tpresim+3000.0])
#network.add_periodic_sequence(intervals=[[tpresim+700.0, tpresim+1300.0], [tpresim+2000.0, tpresim+2900.0], [tpresim+3400, tpresim+5000.0]])
#network.add_random_nonspecific_noise([tpresim+1500.0], frac = 0.15)

# to reproduce Figure 3B
#network.add_item_loading_signals(pop_id=[0,1], origin=[tpresim,tpresim+3000.0])
#network.add_random_nonspecific_noise([tpresim+1450.0], frac = 0.15)

# to reproduce Figure 3B with overlapping populations
#network.add_item_loading_signals(pop_id=[0,1], origin=[tpresim,tpresim+3000.0])
#network.add_random_nonspecific_noise([tpresim+1250.0], frac = 0.15)

# save used parameters into a json
network.save_params()
# build network
network.build_network()
# simulate network
network.simulate_network()
# save data to file
network.save_spike_data()
# plots a raster plot of all the neurons recorded
network.raster_plot()
plt.show()
