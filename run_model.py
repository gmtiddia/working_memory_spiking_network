from model.model import WMModel
import os
from argparse import ArgumentParser

# Get and check path and rng seed
parser = ArgumentParser()
parser.add_argument("--path", type=str, default=None, help='Path for the simulation output (default: data).')
parser.add_argument("--seed", type=int, default=143202461, help='Seed for random number generation (default: 143202461).')
parser.add_argument("--facil_frac", type=float, default=1.0, help='Fraction of facilitated synapses (default: 1.0).')
args = parser.parse_args()

if args.path is None:
    data_path = os.path.join(os.getcwd(), 'data/')
else:
    data_path = os.path.join(os.getcwd(), args.path+"/")

# Script needed to run the model.
#         eta_ext
# Fig 2A - 22.7 (single stable state activity)
# Fig 2B - 23.7 (bi-stable activity with synchronous spiking activity)
# Fig 2C - 24.1 (bi-stable activity with asynchronous spiking activity)

# average variation of membrane potential elicited by external current [mV]
eta_exc = 23.7
# short-term plasticity variable u at the beginning of the simulation
u_start = 0.19
# network params dict
# here add the parameters to be edited. The rest of the parameters are in model/default_params.py
network_p = {
    # excitatory input current [mV]
    'eta_exc': eta_exc,
    'poisson_bkg':{'allow': True},
    # current used to go back to the spontaneous activity
    'eta_exc_end': 22.7 - eta_exc,
    'stp_params' : {'u0': u_start, 'tau_F': 1500.0, 'tau_D': 200.0, 
                    'u0_normal_dist' : {'allow' : True, 'std' : 0.04},
                    'x0_uniform_dist' : {'allow' : True},
                    'tauF_normal_dist' : {'allow' : False, 'std' : 375},
                    'tauD_normal_dist' : {'allow' : False, 'std' : 55}},
    'syn_params' : {'autapses' : True, 'multapses' : False, 
                    'Jp_lognormal_dist' : {'allow' : False, 'std' : 0.36},
                    'Jb_lognormal_dist' : {'allow' : True, 'std' : 0.08},
                    'facil_frac' : 0.9}}

# presimulation time (i.e. time in which the network stays in the spontaneous activity)
tpresim = 3000.0
# simulation time
tsim = 3000.0

# simulation params dict
# here add the parameters to be edited. The rest of the parameters are in default_params.py
simulation_p = {
    # path to data
    "data_path" : data_path,
    # master seed
    #"master_seed" : 143202463,
    "master_seed" : args.seed,
    # number of OpenMP threads
    "threads" : 8,
    # overall simulation time
    "t_sim" : tsim + tpresim,
    # beginning of th current stimulus which diminishes overall background input
    "eta_end_origin": tsim + tpresim - 800.0,
    "recording_params" : {
        # fraction of neurons recorded for each selective population
        "fraction_pop_recorded" : 1.0,
        # selective excitatory population recorded (0, ..., p-1)
        "pop_recorded" : [0, 1, 2, 3, 4],
        "spike_recording_params": {"start": 100.0},
        # save spike data to file
        "save_to_file" : True,
        # save STP data to file
        "stp_recording" : False,
        # selective population for which the STP params (i.e. x, u) will be recorded
        "stp_pop_recorded" : [0, 1],
        # fraction of the selective population to be recorded for stp data
        "stp_fraction_recorded" : 0.1,
        
    }
}

# initialize the network model
network = WMModel(network_p, simulation_p)

# add background
network.add_background_input(start=0.0, stop=tsim+tpresim)

# to reproduce Figure 1A
#network.add_item_loading_signals(pop_id=[0], origin=[tpresim])
#network.add_nonspecific_readout_signal(origin=[tpresim+1100.0])

# to reproduce Figure 1B and 1C
network.add_item_loading_signals(pop_id=[0], origin=[tpresim])


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
#plt.show()
