import nest
import numpy as np
import math
import random
import matplotlib.pyplot as plt
from helpers import *

def noise_params(V_mean, V_std, dt=1.0, tau_m=10., C_m=250.):
    #'Returns mean and std for noise generator for parameters provided; defaults for iaf_psc_alpha.'

    return C_m / tau_m * V_mean, math.sqrt(2/(tau_m*dt))*C_m*V_std

neuron1 = nest.Create("iaf_psc_exp", params={"tau_m": neur_params["tau"][0],
                                            "t_ref": neur_params["t_ref"][0],
                                            "V_th": neur_params["V_th"][0],
                                            "E_L": 0.0,
                                            "V_m": 0.0})
neuron2 = nest.Create("iaf_psc_exp", params={"tau_m": neur_params["tau"][0],
                                            "t_ref": neur_params["t_ref"][0],
                                            "V_th": neur_params["V_th"][0],
                                            "E_L": 0.0,
                                            "V_m": 0.0})


print("\nConnecting background input...")
print(network_params["mu_excA"])
ng_exc, ng_inh = background_input(network_params["mu_excA"], network_params["mu_inh"])
nest.Connect(ng_exc, neuron1)
print(nest.GetStatus(ng_exc))

# additive bkg
mean_I_ext_exc, stdI_ext_exc = noise_params(network_params["mu_excA"]*(stim_params["A_cue"]), network_params["sigma_exc"], neur_params["tau"][0])
signal = nest.Create("noise_generator", params={"mean": mean_I_ext_exc, "std": stdI_ext_exc, "start": 100.0, "stop": 450.0})
nest.Connect(signal, neuron1)
print(nest.GetStatus(ng_exc))

conn_dict = {"rule": "one_to_one"}
syn_dict = {"synapse_model": "tsodyks_synapse",
            "weight": get_weight(syn_params["J_p"], neur_params["tau"][0]),
            "delay": random.uniform(0.0, 1.0),
            "tau_psc": 2.0, # default
            "tau_rec": stp_params["tau_D"],
            "tau_fac": stp_params["tau_F"],
            "U": stp_params["U"],
            "u": 0.0,
            "x": 1.0}
nest.Connect(neuron1, neuron2, conn_dict, syn_dict)

print(nest.GetConnections())


# recording
mult = nest.Create("multimeter")
mult.set(record_from=["V_m"])
nest.Connect(mult, neuron2)

spikerecorder = nest.Create("spike_recorder")
nest.Connect(neuron1, spikerecorder)
nest.Connect(neuron2, spikerecorder)

nest.Simulate(5000.0)

dmm = mult.get()
Vms = dmm["events"]["V_m"]
ts = dmm["events"]["times"]
plt.figure(1)
plt.plot(ts, Vms)
plt.draw()

dSD = spikerecorder.get("events")
evs = dSD["senders"]
ts = dSD["times"]
print(dSD)
plt.figure(2)
plt.plot(ts, evs, ".")
plt.show()
