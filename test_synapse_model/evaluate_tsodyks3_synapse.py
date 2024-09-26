"""
Example of the tsodyks3_synapse in NEST
---------------------------------------

This example is based on the NEST example evaluate_tsodyks2_synapse.
Here, an additional postsynaptic neuron is simulated and connected
to the presynaptic neuron using the tsodyks3_synapse model.

"""

import nest
import nest.voltage_trace
import numpy as np
import matplotlib.pyplot as plt

from pynestml.codegeneration.nest_code_generator_utils import NESTCodeGeneratorUtils

stp_synapse= """
# Synapse model of STP with NESTML

model stp_synapse:

    state:
        u real = 0.2
        x real = 1.0
        t_ls ms = 0.0 ms
    parameters:
        w real = 1.0
        U real = 0.2
        tau_rec ms = 200.0 ms
        tau_fac ms = 1500.0 ms
        delay ms = 1.0 ms

    # Short term plasticity mechanism depends only from presynaptic activity
    input:
        pre_spikes <- spike

    output:
        spike

    onReceive(pre_spikes):
        inline dt ms = t - t_ls
        x = 1.0 + (x - 1.0)*exp(-dt/tau_rec)
        u = U + (u - U)*(exp(-dt/tau_fac))
        u = u + U*(1.0 - u)
        emit_spike(w*u*x, delay)
        x = x - u*x
        t_ls = t

"""

module_name, synapse_model_name = \
        NESTCodeGeneratorUtils.generate_code_for(stp_synapse,
                                                codegen_opts={"delay_variable": {"stp_synapse": "delay"},
                                                            "weight_variable": {"stp_synapse": "w"}})

nest.ResetKernel()
nest.Install(module_name)

###############################################################################
# Parameter set for facilitation

fac_params = {"U": 0.2, "u": 0.2, 'x': 1.0, 'y': 0.0, "tau_fac": 1500.,
              "tau_rec": 200., "weight": 100.}
fac_params2 = {"U": 0.2, "u": 0.2, 'x': 1.0, "tau_fac": 1500.,
              "tau_rec": 200., "weight": 100.}
fac_params3 = {"U": 0.2, "u": 0.2, 'x': 1.0, "tau_fac": 1500.,
              "tau_rec": 200., "weight": 100.}


###############################################################################
# Now we assign the parameter set to the synapse models.

tsodyks_params = dict(fac_params, synapse_model="tsodyks_synapse")     # for tsodyks_synapse
tsodyks2_params = dict(fac_params2, synapse_model="tsodyks2_synapse")  # for tsodyks2_synapse

nest.CopyModel(synapse_model_name, "stp_synapse", fac_params3)

###############################################################################
# Create three neurons.

neuron = nest.Create("iaf_psc_exp", 4, params={"tau_syn_ex": 2.})

###############################################################################
# Neuron one produces spikes. Neurons 2, 3 and 4 receive the spikes via the
# synapse models.

nest.Connect(neuron[0], neuron[1], syn_spec=tsodyks_params)
nest.Connect(neuron[0], neuron[2], syn_spec=tsodyks2_params)
nest.Connect(neuron[0], neuron[3], syn_spec={'synapse_model': 'stp_synapse'})


###############################################################################
# Now create the voltmeters to record the responses.

voltmeter = nest.Create("voltmeter", 3, params={'interval': 0.1})

###############################################################################
# Connect the voltmeters to the neurons.

nest.Connect(voltmeter[0], neuron[1])
nest.Connect(voltmeter[1], neuron[2])
nest.Connect(voltmeter[2], neuron[3])

###############################################################################
# Now simulate the standard STP protocol: a burst of spikes, followed by a
# pause and a recovery response.

sim1 = 500.0
sim2 = 1000.0
sim3 = 500.0


neuron[0].I_e = 376.0
nest.Simulate(sim1)

neuron[0].I_e = 0.0
nest.Simulate(sim2)

neuron[0].I_e = 376.0
nest.Simulate(sim3)


###############################################################################
# Finally, generate voltage traces. Both are shown in the same plot and
# should be almost completely overlapping.


voltmeter1 = voltmeter[0].get('events')
voltmeter2 = voltmeter[1].get('events')
voltmeter3 = voltmeter[2].get('events')

T = voltmeter1['times']
V1 = voltmeter1['V_m']
V2 = voltmeter2['V_m']
V3 = voltmeter3['V_m']

data_v = [T, V1, V2, V3]
np.savetxt("voltage_data.dat", data_v)


plt.figure(1)
nest.voltage_trace.from_device(voltmeter[0])
nest.voltage_trace.from_device(voltmeter[1])
nest.voltage_trace.from_device(voltmeter[2])
plt.show()


